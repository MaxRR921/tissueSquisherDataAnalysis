import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

"""
Potential issues:
- Ex and Ey are each 1 value, not arrays. 


"""



#NORMALIZE USING THE CALCULATED VALUES NOT MEASURED FROM SETUP...
class Calibration: #Px - Py/Px+Py Use Ex0, normalize power, should match 
       def __init__(self, interaction_length):
              # Material properties of the fiber
              self.Y = 7.3e10 # young's modulus of the fiber in N/m^2
              self.sigma = 0.17 # Poisson's ratio at 633nm wavelength
              self.N = 1.46 # Refractive index of the fiber 
              self.p_11 = 0.121 #photelastic constants 
              self.p_12 = 0.27
              self.b = 62.5e-6 # Radius of fiber cladding in meters 
              self.Lb_0 = 2e-3 # unstressed beat length in meters
              self.fiberWavelength = 1550e-9
              self.k=(2*np.pi)/self.fiberWavelength

              self.phi = 0 
              self.normalizedForce = 0
              
              #FIND OUT MFD?? 
              self.fiberArea = np.pi*(self.b**2) # fiber area cross sectional in meters 

              #calculated values


              self.l = interaction_length
              self.Ex_0 = 1

              self.alpha = np.pi/4
              self.beta  = np.pi/4
              self.gamma = np.pi/2
              self.delta = 0
              self.eta = 376.730313


       def compute_fields(self, force):
              """Return complex field amplitudes (Ex, Ey) at a given force.

              Args:
              force: Tensile load applied to the fibre [N].

              Returns:
              Tuple of complex field amplitudes (Ex, Ey).
              """
              # --- Physically derived angles and indices ---------------------
              self.normalizedForces = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * force / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
              self.phiValues= 0.5 * np.arctan2(self.normalizedForces * np.sin(2*self.alpha),
                        1 + self.normalizedForces * np.cos(2*self.alpha) )

              # print("phivalues: ", self.phiValues)
              self.Lb = self.Lb_0 * (1 + self.normalizedForces**2 + 2 * self.normalizedForces * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length
              self.deltaN = (2*np.pi)/(self.k*self.Lb)
              self.Ns = self.N + (self.deltaN/2) 
              self.Nf = self.N - (self.deltaN/2)

              # --- Ex, Ey via explicit matrix expression ---------------------
              exp_ns = np.exp(-1j * self.k * self.Ns * self.l)   # e^{-i k N_s l}
              exp_nf = np.exp(-1j * self.k * self.Nf * self.l)   # e^{-i k N_f l}

              # Helper brackets from the hand-derived expression
              bracket_1 = (
              np.cos(self.phiValues) * np.cos(self.phiValues + self.beta) * exp_ns
              + np.sin(self.phiValues) * np.sin(self.phiValues + self.beta) * exp_nf
              )
              bracket_2 = (
              np.sin(self.phiValues) * np.cos(self.phiValues + self.beta) * exp_ns
              - np.cos(self.phiValues) * np.sin(self.phiValues + self.beta) * exp_nf
              )

              Ex = self.Ex_0 * (
              np.cos(self.gamma) * bracket_1
              + np.sin(self.gamma) * bracket_2 * np.exp(1j * self.delta)
              )
              Ey = self.Ex_0 * (
              -np.sin(self.gamma) * bracket_1
              + np.cos(self.gamma) * bracket_2 * np.exp(1j * self.delta)
              )



       def __calcFields(self, force): 
              f = force/self.l
              self.normalizedForce = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * f / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
              self.phi = 0.5 * np.arctan2(self.normalizedForce * np.sin(2*self.alpha),
                        1 + self.normalizedForce * np.cos(2*self.alpha) )

              # print("phivalues: ", self.phiValues)
              Lb = self.Lb_0 * (1 + self.normalizedForce**2 + 2 * self.normalizedForce * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length
              deltaN = (2*np.pi)/(self.k*Lb)
              Ns = self.N + (deltaN/2) 
              Nf = self.N - (deltaN/2)

              
              A = np.cos(self.phi)*(np.exp(-1*1j*self.k*Ns*self.l)*np.cos(self.phi + self.beta)) 
              B = np.sin(self.phi)*(np.exp(-1*1j*self.k*Nf*self.l)*(np.sin(self.phi + self.beta)))
              C = np.sin(self.phi)*(np.exp(-1*1j*self.k*Ns*self.l)*np.cos(self.phi + self.beta))
              D = -np.cos(self.phi)*(np.exp(-1*1j*self.k*Nf*self.l)*(np.sin(self.phi + self.beta)))

              
              # print("(A+B): ", (A+B))
              # print("(C+D): ", (C+D))
              # PHI SEEMS TO HAVE AN INVERSE RELATIONSHIP ON HOW much (A+B) and (C+D) change (less phi change is more (A+B) and (C+D) change), and by extension how much Ex and Ey change 
              # PHI is much more when alpha is 
              Ex = self.Ex_0 * ( (np.cos(self.gamma)*(A+B)) + (np.sin(self.gamma) * (np.exp(1j*self.delta) * (C+D)))) 

 
              Ey = self.Ex_0 * ( (-np.sin(self.gamma)*(A+B)) + (np.cos(self.gamma) * (np.exp(1j*self.delta) * (C+D))))


              # print("Ex: ", self.Ex)
              # print("Ey: ", self.Ey)




              return Ex, Ey 
       

       def __calcPower(self, Ex, Ey):

          Ex2= np.abs(Ex)**2  # Equivalent to |Ex|^2
          Ey2= np.abs(Ey)**2 #Equivalent to |Ey|^2
          eta = 376.73  # Characteristic impedance of free space (ohms)

          return Ex2/(2*eta) * self.fiberArea, Ey2/(2*eta) * self.fiberArea 

          
          


       def calcNormalizedPower(self, S1, S2):
          return S1/(S1+S2), S2/(S1+S2) 

       def plotNormalizedPowersVsAlpha(self, alphaValues, forces):
          plt.figure()
          s1Arr = np.zeros(len(alphaValues))
          s2Arr = np.zeros(len(alphaValues))
          curves = []
          for j in range(len(forces)):
               s1Arr = np.zeros(len(alphaValues))     # new array each force
               s2Arr = np.zeros(len(alphaValues))
               for i in range(len(alphaValues)):
                    self.alpha = alphaValues[i]
                    Ex, Ey = self.__calcFields(forces[j])
                    S1, S2 = self.__calcPower(Ex, Ey)
                    s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2)
               print("S1:", s1Arr)
               curves.append((forces[j], s1Arr.copy()))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(alphaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('Alpha (radians)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Alpha')
          plt.legend()
          plt.grid(True)

          plt.show()

       def plotPhiVsNormalizedForce(self, f, alphaVals):
          phiValues = []
          phiLines = []
          normalizedForceValues = []

          phiValues.append(phiLines) 
          
          for alpha in alphaVals:
               phiValues = []
               normalizedForceValues = []
               for F in f:
                    self.alpha = alpha 
                    self.__calcFields(F)
                    normalizedForceValues.append(self.normalizedForce)
                    phiValues.append(self.phi)
               phiLines.append(phiValues)

          plt.figure()
          plt.plot(normalizedForceValues, phiLines[0], label="phi = 30deg")
          plt.plot(normalizedForceValues, phiLines[1], label="phi = 45deg")
          plt.plot(normalizedForceValues, phiLines[2], label="phi = 60deg")
          plt.plot(normalizedForceValues, phiLines[3], label="phi = 75deg")

          plt.xlabel('Normalized force')
          plt.ylabel('Phi')
          plt.title('Phi with respect to normalized force')
          plt.legend()
          plt.grid(True, linestyle='--', alpha=0.3)
          plt.show()

       def plotNormalizedBeatLengthVsNormalizedForce(self, alphaVals):
              beatLines = []
              for i in range(len(alphaVals)):
                     
                     self.alpha = alphaVals[i] 
                     h, k = self.redidCalculatePowers(7,5.2)
                     beatLines.append(self.Lb/self.Lb_0)
                     
              plt.figure()
              plt.plot(self.normalizedForces, beatLines[0], label="phi = 30deg")
              plt.plot(self.normalizedForces, beatLines[1], label="phi = 45deg")
              plt.plot(self.normalizedForces, beatLines[2], label="phi = 60deg")
              plt.plot(self.normalizedForces, beatLines[3], label="phi = 75deg")

              plt.xlabel('Normalized force')
              plt.ylabel('Normalized beat Length')
              plt.title('Normalized beat length with respect to normalized force')
              plt.legend()
              plt.grid(True, linestyle='--', alpha=0.3)
              plt.show()            

       def plotNormalizedPowersSeperately(self, forces):
          plt.figure()
          s1Arr = np.zeros(len(forces))
          s2Arr = np.zeros(len(forces))

          for i in range(len(forces)):
               Ex, Ey = self.__calcFields(forces[i])
               S1, S2 = self.__calcPower(Ex, Ey) 
               s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2) 

          plt.plot(forces, s1Arr, label='S1 Normalized')
          plt.plot(forces, s2Arr, label='S2 Normalized')
          plt.xlabel('Force')
          plt.ylabel('Normalized Power')
          plt.title('S1 and S2 Normalized Power vs. Force')
          plt.legend()
          plt.grid(True)

          # plt.ylim(0, 1)  # Optional: Set fixed Y-axis range if needed
          # plt.tight_layout()
          plt.show()

       def plotPowerDifferencesNormalized(self, forces):
          plt.figure()
          s1Arr = np.zeros(len(forces))
          s2Arr = np.zeros(len(forces))

          for i in range(len(forces)):
               Ex, Ey = self.__calcFields(forces[i])
               S1, S2 = self.__calcPower(Ex, Ey) 
               
               s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2) 
          SdifferencesNormalized = s1Arr - s2Arr


          plt.plot(forces, SdifferencesNormalized, label='Sdifference (W)')
          plt.xlabel('Force')
          plt.ylabel('Power Difference Normalized')
          plt.title('Power Difference Force')
          plt.legend()
          plt.grid(True)

          # plt.ylim(-1, 1)  # Set Y-axis to fixed scale
          # plt.tight_layout()
          plt.show()

npoints = 500
c = Calibration(.018)
c.plotPowerDifferencesNormalized(np.linspace(0,25,500))
c.plotNormalizedPowersSeperately(np.linspace(0,25,500))
c.plotNormalizedPowersVsAlpha(np.linspace(0,np.pi,500), np.linspace(0,50,3))
alphas = np.deg2rad([30, 45, 60, 75])
c.plotPhiVsNormalizedForce(np.linspace(0,50,500), alphas)
# func = c.generate_function_powerdiff_to_force()

# print("FUNC(1.5e-12): ", (func(440e-9)/20e6))
# print("FUNC(10): ", func(10))
