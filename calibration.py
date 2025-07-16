
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import pandas as pd
from scipy.interpolate import PchipInterpolator
import csv
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
          self.Px_0 = 1

          self.phi = 0 
          self.normalizedForce = 0

          #FIND OUT MFD?? 
          self.fiberArea = np.pi*(self.b**2) # fiber area cross sectional in meters 

          #calculated values


          self.l = interaction_length
          self.Ex_0 = 1
          # α=55.9°, β=65.2°, gamma=74.5

          #0.8136 rad

          # β = 55.9° → 55.9·π/180 ≈ 0.9757 rad

          # γ = 18.6° → 18.6·π/180 ≈ 0.3240 rad
          self.alpha = 0
          self.beta  = 0
          self.gamma = 0 
          self.delta =  0
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
          f = force
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

          return np.abs(Ex**2), np.abs(Ey**2) 
     



     def calculateForceOnFiber(self, inputForce):
          divisor = np.pi * ((self.l / 2) ** 2)
          left = inputForce / divisor
          right = self.l * self.b
          return left * right


     def __calcPowersChua(self,force):
          f = force/.0002
          self.normalizedForce = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * f / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
          self.phi = 0.5 * np.arctan2(self.normalizedForce * np.sin(2*self.alpha),
                    1 + self.normalizedForce * np.cos(2*self.alpha) )
          Lb = self.Lb_0 * (1 + self.normalizedForce**2 + 2 * self.normalizedForce * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length 
          
          return self.Px_0*(1- ((np.sin(2*self.phi))**2)*( (np.sin((np.pi*self.l)/(Lb))) **2)), self.Px_0*(((np.sin(2*self.phi))**2)*( (np.sin((np.pi*self.l)/(Lb))) **2)), 



     def __calcPowersNewEquations(self, force):
          #divide force by width 
          f = force/.0002
          self.normalizedForce = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * f / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
          self.phi = 0.5 * np.arctan2(self.normalizedForce * np.sin(2*self.alpha),
                    1 + self.normalizedForce * np.cos(2*self.alpha) )
          Lb = self.Lb_0 * (1 + self.normalizedForce**2 + 2 * self.normalizedForce * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length 

          Px = .25*np.exp(-2j*self.k*self.N*self.l)* (np.exp(-1j*self.l*((2*np.pi)/Lb))*(np.cos(self.phi)*np.cos(self.phi+self.beta))+(np.sin(self.phi)*np.sin(self.phi+self.beta)))**2
          Py = .25*np.exp(2j*(self.delta-(self.k*self.N*self.l)))* (np.exp(-1j*self.l*((2*np.pi)/Lb))*(np.sin(self.phi)*np.cos(self.phi+self.beta))+(np.cos(self.phi)*np.sin(self.phi+self.beta)))**2
          return Px, Py


     def __calcPowersFromExEy(self, force):
          f = force/0.0002
          self.normalizedForce = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * f / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
          self.phi = 0.5 * np.arctan2(self.normalizedForce * np.sin(2*self.alpha),
                    1 + self.normalizedForce * np.cos(2*self.alpha) )
          Lb = self.Lb_0 * (1 + self.normalizedForce**2 + 2 * self.normalizedForce * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length 
          
          Ex = -0.5*self.Ex_0*np.exp(-1j*self.k*self.N*self.l)*((np.exp(-1j*self.l*((2*np.pi)/Lb))*np.cos(self.phi)*np.cos(self.phi+self.beta)) + np.sin(self.phi)*np.sin(self.phi+self.beta))
          Ey = -0.5*np.exp(-1j*self.delta)*np.exp(-1j*self.k*self.N*self.l)*self.Ex_0*((np.exp(-1j*self.l*((2*np.pi)/Lb))*np.sin(self.phi)*np.cos(self.phi+self.beta)) - np.cos(self.phi)*np.sin(self.phi+self.beta))
          
          Sx = np.abs(Ex)**2
          Sy = np.abs(Ey)**2
          return Sx, Sy


     def __calcNormalizedCrossIntensityChua(self, force):
          f = force/.0002
          lOverLb_0 = self.l/self.Lb_0
          self.normalizedForce = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * f / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
          print("normalized force: ", self.normalizedForce)
          Lb = self.Lb_0 * (1 + self.normalizedForce**2 + 2 * self.normalizedForce * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length 
          return ((np.pi*lOverLb_0)**2) * (self.normalizedForce**2) * ((np.sin(2*self.alpha))**2) * ((((np.sin((np.pi*lOverLb_0*(1+(self.normalizedForce**2) + (2*self.normalizedForce*np.cos(2*self.alpha)))**.5)))))/((np.pi*lOverLb_0*(1+(self.normalizedForce**2) + (2*self.normalizedForce*np.cos(2*self.alpha)))**.5)))**2

     

     def calcForce(self, Fsample, dFiber):

          # Given values
          F_sample = Fsample            # N
          D_sample = self.l         # meters (diameter of sample)
          d_fiber = dFiber          # meters (diameter of fiber)

          # A_sample = π * (D_sample^2) / 4
          A_sample = np.pi * (D_sample**2) / 4

          # A_fiber = D_sample * (π * d_fiber / 2)
          A_fiber = D_sample * (np.pi * d_fiber / 2)

          # Force on fiber
          F_fiber = F_sample * (A_fiber / A_sample)

          # Output
          print(f"A_sample = {A_sample:.6e} m^2")
          print(f"A_fiber = {A_fiber:.6e} m^2")
          print(f"F_fiber = {F_fiber:.6f} N")

          return F_fiber
       


     def __calcPower(self, Ex, Ey):

          Ex2= np.abs(Ex)**2  # Equivalent to |Ex|^2
          Ey2= np.abs(Ey)**2 #Equivalent to |Ey|^2
          eta = 376.73  # Characteristic impedance of free space (ohms)

          return Ex2/(2*eta) * self.fiberArea, Ey2/(2*eta) * self.fiberArea 


     def plotStressVsPowerDifference(self, forces):
          plt.figure()
          s1Arr = np.zeros(len(forces))
          s2Arr = np.zeros(len(forces))
          for i in range(len(forces)):
               Ex, Ey = self.__calcFields(forces[i])
               S1, S2 = self.__calcPower(Ex, Ey) 
               s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2)

          stresses = forces/(self.fiberArea * self.l)
          powerDifferences = (s1Arr.copy() - s2Arr.copy())


          plt.plot(powerDifferences, stresses,  label=f'Stress: ')

          plt.xlabel('power Difference')
          plt.ylabel('Stress')
          plt.title('Force vs. Stress')
          plt.legend()
          plt.grid(True)

          plt.show()
          
          plt.figure()
               




          
          


     #   def calcNormalizedPowerDiff(self, S1, S2):
     #      return np.abs( (S2/(S1+S2)) - (S1/(S1+S2)) ) 

     def calcNormalizedPowerDifference(self, S1, S2):
          return np.abs((S2 - S1)/(S1+S2))
       
     def calcNormalizedPowers(self, Sx, Sy):
          return Sx/(Sx+Sy), Sy/(Sx+Sy)
       
     def calcNormalizedCrossIntensity(self, S1, S2):
          print(self.Px_0)
          print("cross intensity: ", S2/self.Px_0)
          return S2/self.Px_0

     def plotNormalizedPowersVsAlpha(self, alphaValues, forces):
          plt.figure()
          SdifferencesCrossIntensityChua  = np.zeros(len(alphaValues))
          SdifferencesChua = np.zeros(len(alphaValues))
          Sdifferences = np.zeros(len(alphaValues))
          curves = []
          curvesChuaCrossIntensity = []
          curvesChua = []
          S10=0
          for j in range(len(forces)):
               Sdifferences  = np.zeros(len(alphaValues))
               for i in range(len(alphaValues)):
                    self.alpha = alphaValues[i]
                    Sx, Sy = self.__calcFields(forces[j])
                    SxChua, SyChua = self.__calcPowersChua(forces[j])
                    SdifferencesCrossIntensityChua[i] = self.calcNormalizedPowerDifference(SxChua, SyChua)
                    Sdifferences[i] = self.calcNormalizedPowerDifference(Sx, Sy)
               curvesChuaCrossIntensity.append((forces[j], SdifferencesCrossIntensityChua.copy()))
               curvesChua.append((forces[j], SdifferencesChua.copy()))
               curves.append((forces[j], Sdifferences.copy()))

               # print("S1:",)


          for curve in curves:
               plt.plot(np.rad2deg(alphaValues), curve[1], label=f'Force: {curve[0]} ')

          # for curve in curvesChuaCrossIntensity:
          #      plt.plot(np.rad2deg(alphaValues), curve[1], label=f'Force: {curve[0]} ')

          # for curve in curvesChua:
          #      plt.plot(np.rad2deg(alphaValues), curve[1], label=f'ForceChua: {curve[0]} ')

          plt.xlabel('Alpha (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Alpha')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.alpha = 0
       



     def plotNormalizedPowersVsDelta(self, deltaValues, forces):
          plt.figure()
          s1Arr = np.zeros(len(deltaValues))
          s2Arr = np.zeros(len(deltaValues))
          curves = []
          for j in range(len(forces)):
               s1Arr = np.zeros(len(deltaValues))     # new array each force
               s2Arr = np.zeros(len(deltaValues))
               for i in range(len(deltaValues)):
                    self.gamma = deltaValues[i]
                    S1, S2 = self.__calcPowersFromExEy(forces[j])
                    s1Arr[i] = self.calcNormalizedPowerDifference(S1, S2)
               print("S1:", s1Arr)
               curves.append((forces[j], s1Arr))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(deltaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('Delta (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Delta')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.delta = np.pi/4

     def plotNormalizedPowersVsGamma(self, gammaValues, forces):
          plt.figure()
          s1Arr = np.zeros(len(gammaValues))
          s2Arr = np.zeros(len(gammaValues))
          curves = []
          for j in range(len(forces)):
               s1Arr = np.zeros(len(gammaValues))     # new array each force
               s2Arr = np.zeros(len(gammaValues))
               for i in range(len(gammaValues)):
                    self.gamma = gammaValues[i]
                    S1, S2 = self.__calcFields(forces[j])
                    s1Arr[i] = self.calcNormalizedPowerDifference(S1, S2)
               print("S1:", s1Arr)
               curves.append((forces[j], s1Arr))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(gammaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('gamma (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Gamma')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.gamma = 0 


     def plotNormalizedPowersVsBeta(self, betaValues, forces):
          plt.figure()
          s1Arr = np.zeros(len(betaValues))
          s2Arr = np.zeros(len(betaValues))
          curves = []
          for j in range(len(forces)):
               s1Arr = np.zeros(len(betaValues))     # new array each force
               s2Arr = np.zeros(len(betaValues))
               for i in range(len(betaValues)):
                    self.beta = betaValues[i]
                    S1, S2 = self.__calcFields(forces[j])
                    s1Arr[i] = self.calcNormalizedPowerDifference(S1, S2)
               print("S1:", s1Arr)
               curves.append((forces[j], s1Arr))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(betaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('beta (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. beta')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.beta = 0 

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
          self.alpha = np.pi/4

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


     def plotGammaVsSingleForce(self, gammaVals, f):
          s1Arr = np.zeros(len(gammaVals))
          s2Arr = np.zeros(len(gammaVals))
          for i in range(len(gammaVals)):
               self.gamma = gammaVals[i]
               Ex, Ey = c.__calcFields(f)
               S1, S2 = c.__calcPower(Ex, Ey)
               s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2)


               

          plt.figure()
          plt.plot(gammaVals, (s1Arr - s2Arr), label="power difference Normalized")

          plt.xlabel('Gamma')
          plt.ylabel('Normalized power difference')
          plt.title('Normalized power difference vs gamma for a single force ')
          plt.legend()
          plt.grid(True, linestyle='--', alpha=0.3)
          plt.show()            




               


     def plotNormalizedPowersSeperately(self, forces):
          plt.figure()
          s1Arr = np.zeros(len(forces))
          s2Arr = np.zeros(len(forces))
          sDifferencesNormalized = np.zeros(len(forces))

          for i in range(len(forces)):
               Sx, Sy = self.__calcFields(forces[i])
               s1Arr[i], s2Arr[i] = self.calcNormalizedPowers(Sx, Sy) 
               # crossIntensityArr[i] = self.calcNormalizedCrossIntensity(s1Arr[0], s2Arr[i])
               # Sx, Sy = self.__calcPowersNewEquations(forces[i])

               print("normalized cross intensity: ", sDifferencesNormalized[i])
                    

          plt.plot(forces, s1Arr, label='S1 ')
          plt.plot(forces, s2Arr, label='S2 ')
          # plt.plot(forces, crossIntensityArr, label='Normalized cross intensity')
          plt.xlabel('Force')
          plt.ylabel('Normalized Power')
          plt.title('S1 and S2 Normalized Power vs. Force')
          plt.legend()
          plt.grid(True)

          plt.show()



     def plotPowerDifferencesNormalized(self, forces):
          plt.figure()
          Sdiff = np.zeros(len(forces))

          for i in range(len(forces)):
               Sx, Sy = self.__calcFields(forces[i])
               Sdiff[i] = self.calcNormalizedPowerDifference(Sx, Sy)


          # --- Plot 1: Sdiff vs Force ---
          stresses = forces/(np.pi*self.b**2)
          plt.figure()
          plt.plot(forces, Sdiff, label='Sdifference (W)', color='tab:blue')

          interp = PchipInterpolator(forces, Sdiff)
          x_fit = np.linspace(min(forces), max(forces), 500)

          # Interpolated (fitted) power differences
          y_fit = interp(x_fit)

          plt.plot(x_fit, y_fit, '--', label='Fitted Curve', color='tab:orange')

          plt.xlabel('force')
          plt.ylabel('Power Difference Normalized')
          plt.title('Power Difference vs Force')
          plt.legend()
          plt.grid(True)
          plt.show()

          # eq1 = f"{coeffs1[0]:.5e} * Force² + {coeffs1[1]:.5e} * Force + {coeffs1[2]:.5e}"
          # print("Sdiff = " + eq1)
          # 
          # --- Plot 2: Force vs Sdiff (inverted axes) ---
          plt.figure()
          plt.plot(Sdiff, forces, label='Force (N)', color='tab:green')

          sorted_idx = np.argsort(Sdiff)
          Sdiff_sorted = Sdiff[sorted_idx]
          stresses_sorted = forces[sorted_idx]
          interp = PchipInterpolator(Sdiff_sorted, stresses_sorted)
          x_fit = np.linspace(min(Sdiff_sorted), max(Sdiff_sorted), 500)

          # Interpolated (fitted) power differences
          y_fit = interp(x_fit)

          plt.plot(x_fit, y_fit, '--', label='Fitted Curve', color='tab:red')

          print("MIN STRESS: ", np.min(forces), "MAX STRESS", np.max(forces))
          print("MAX POWER: ", np.max(Sdiff), "MIN POWER: ", np.min(Sdiff))

          plt.xlabel('Power Difference Normalized')
          plt.ylabel('force')
          plt.title('Force vs Power Difference')
          plt.legend()
          plt.grid(True)
          plt.show()
          


     # def findBestAlphaGamma(self, targetForce):
     #      for alpha 



     def calculateAlphaAndBeta(self, targetForce):
          curves = []
          # df = pd.read_csv('avg.csv')
          # sdiffs = df['Sdifference'].dropna().values
          # print("sdiffs: ", sdiffs)
     #   maxPower = np.max(sdiffs)
     #   minPower = np.min(sdiffs)
     #   maxPower = np.max(sdiffs[sdiffs != 0])
     #   minPower = np.min(sdiffs[sdiffs != 0])
          minPower = .028
          midPower = .032
          maxPower = .035
          difference = maxPower-minPower
          print("Max power: ", maxPower, "Min power: ", minPower)

          finds = []
          #theoretical:
          done = False
     #   self.gamma = 1.3
          lengths = [0.01818]
          for gamma in np.linspace(0, np.pi/2, 30):
               self.gamma = gamma 
               for alpha in np.linspace(0, np.pi/2, 30):
                    self.alpha = alpha
                    for beta in np.linspace(0, np.pi/2, 30):
                         self.beta = beta
                         forces = np.linspace(0, targetForce, 500)
                         stresses = forces/(np.pi * self.b**2)

                         targetStress = targetForce/(np.pi*self.b**2)
                         print("TARGET STRESS: ", targetStress)
                         powerDifferences = np.zeros(500)
                         for i in range (len(forces)): 
                              Sx, Sy = self.__calcFields(forces[i])
                              powerDifferences[i] = self.calcNormalizedPowerDifference(Sx, Sy)
                         # plot at α≈π/4, β≈π/4
                         theoreticalPmax = np.max(powerDifferences)
                         theoreticalPmid = np.median(powerDifferences)
                         theoreticalPmin = np.min(powerDifferences)

                         
                         if (minPower >= theoreticalPmin and maxPower <= theoreticalPmax and np.isclose(midPower, theoreticalPmid)):
                              sorted_idx = np.argsort(powerDifferences)
                              Sdiff_sorted = powerDifferences[sorted_idx]
                              forces_sorted = forces[sorted_idx]
                              Sdiff_unique, unique_indices = np.unique(Sdiff_sorted, return_index=True)
                              forces_unique = forces_sorted[unique_indices]
                              if len(Sdiff_unique) < 2:
                                   print(f"Skipping α={np.rad2deg(alpha):.1f}, β={np.rad2deg(beta):.1f}, γ={np.rad2deg(gamma):.1f} — only one unique Sdiff")
                                   continue  # Skip this case
                              interp = PchipInterpolator(Sdiff_unique, forces_unique)

                              x_fit = np.linspace(min(Sdiff_sorted), max(Sdiff_sorted), 500)

                              # Interpolated (fitted) power differences
                              y_fit = interp(x_fit)


                              # Interpolated (fitted) power differences
                              print("powerDifferences range:", np.min(powerDifferences), np.max(powerDifferences))
                              print("sdiffs range:", minPower, maxPower)
                              forceMax = interp(maxPower)
                              forceMin = interp(minPower)
                              print("FORCE Max (real val): ", np.abs(forceMax))
                              print("theoretical max force:", targetForce)
                              # print("fmin: ", stressMin, "fMax: ", stressMax, "alpha: ", np.rad2deg(alpha), "beta: ", np.rad2deg(beta), "gamma: ", np.rad2deg(gamma))
                              if np.isclose(difference, (theoreticalPmax-theoreticalPmin), atol=.01):
                                   finds.append(f"Slope = {y_fit[0]}, Found force max = {forceMax:.6f}, force min = {forceMin:.6f}, α={np.rad2deg(self.alpha):.1f}°, β={np.rad2deg(self.beta):.1f}°, gamma={np.rad2deg(self.gamma):.1f}")
                                   curves.append((x_fit, y_fit, maxPower, forceMax, minPower, forceMin))
                         else:
                              print("Invalid range")


          for find in finds:
               print(find)

          plt.figure(figsize=(8, 6))
          for x_fit, y_fit, maxP, stressMax, minP, stressMin in curves:
               plt.plot(x_fit, y_fit)
               plt.plot(maxP, stressMax, 'ro')  # red point for max
               plt.plot(minP, stressMin, 'bo')  # blue point for min

               plt.xlabel('Power Difference')
               plt.ylabel('Force')
               plt.title('Fitted Curves with Fmin and Fmax Points')
               plt.grid(True)
               plt.tight_layout()
               plt.show()



                    

     def findMinStartingDiff(self):
          bzeros = []
          self.alpha = np.pi/5
          self.gamma = np.pi/5
          for b in np.linspace(0, 2*np.pi, 360):
               self.beta = b
               Sx, Sy = self.__calcFields(0)
               print("power diff: ", self.calcNormalizedPowerDifference(Sx, Sy))
               if np.isclose(self.calcNormalizedPowerDifference(Sx, Sy), 0, atol=.01):
                    bzeros.append(self.beta) 
                              
          with open("zeroes.csv", "w", newline="") as f:      # use "a" to append instead of overwrite
               writer = csv.writer(f)
               writer.writerow([ "beta"])     # header row

               # write the data rows
               for b in zip(bzeros):
                    writer.writerow([b])
          


npoints = 500
c = Calibration(.03154)
print(c.calcForce(11.2940, .0002)/.0002)
#4.0861
# c.calculateAlphaAndBeta(c.calcForce(4.0861, .0002)/.0002) # 6.71 N is the target force

c.findMinStartingDiff()





# 1. Updates for the new changes to the setup and 



# c.plotNormalizedPowersVsDelta(np.linspace(0,np.pi,500), np.linspace(0,.08993091942,3))
# c.plotStressVsPowerDifference(np.linspace(0, 0.090748, 500))
# c.gamma = 6.2516115116661215 
# c.beta = 4.609774144965928 
# c.alpha = 2.3680346635098943

#MESSAGE HARRISON: noticed from the plots that when the gamma and alpha are too close to zero it doesnt work well, calibration will fail because we go through a larger portion of the curve and get non-function behavior That's why my results from the other day were wrong.
#What can happen is we can still see sensitivits at different angles of beta, but the force doesn't cause a large change in power difference, namely  different forces don't have different power difference deltas for certain angles.


# all angles at pi/5 good candidate 

c.gamma = np.pi/5 
c.alpha = np.pi/5 
c.beta = np.pi/5
c.plotPowerDifferencesNormalized(np.linspace(0, c.calcForce(11.29, .0002)/.0002, 500))  
# c.findMinStartingDiff()
# c.plotNormalizedPowersVsAlpha(np.linspace(0,np.pi,500), np.linspace(0,c.calcForce(4.0861, .0002)/.0002,3)) #GOOD! look at envelope maximum... 45 degrees is the maximum of the envelope
# c.plotNormalizedPowersVsGamma(np.linspace(0,np.pi,500), np.linspace(0, c.calcForce(4.0861, .0002)/.0002,3))
# c.plotNormalizedPowersVsBeta(np.linspace(0,np.pi,500), np.linspace(0,c.calcForce(1.6835, .0002)/.0002,3))
# alphas = np.deg2rad([30, 45, 60, 75])
# c.plotPhiVsNormalizedForce(np.linspace(0,50,500), alphas)
# gammas = np.deg2rad([30, 45, 60, 75])
# c.plotGammaVsSingleForce(gammas, 0.090748)

# print(c.b)

# func = c.generate_function_powerdiff_to_force()

# print("FUNC(1.5e-12): ", (func(440e-9)/20e6))
# print("FUNC(10): ", func(10))

# sample holder: 35, scale: 33.0 dif 2

#move 3.7 to 0.3 applies 6.71 N

# interaction length: .019 m

#Equation for this physical setup : Force = 4.43433e+02 * Sdiff  + -1.56962e-07




## ALL THE CURVES ARE DIFFERENT. CHANGING ALPHA CHANGES THE SHAPE OF THE CURVE, NOT JUST HOW MUCH THE POWER CHANGES
#DRAFT BY 23RD


#DO LOWER STARTING VALUES IN EITHER ARM CORRESPOND TO LOWER CHANGE IN POWER??




#GOAL:


# Read in csv of values: index vs power 1, index vs power 2
# take the normalized power difference.
# once we have this, set a target force: target force = 6.71 N 
# sweep through alpha and beta values (n^2), generating curves of power difference vs force. 
# find the maximum and minimum of the data powerdifference, subtract to find the change in power difference
# sweep through our curves, feeding in the power difference to each, find the curve with the corresponding force that most
# closely matches the target force.


#CONCLUSION: Scaling is messed up, can't get good curve fits. we need to reevaluate our method for normalizing power.
# I think the best thing to do is to model how we do it after the way chua paper does it. Redo the multiplication to get S1 and S0 as functions of phi and beta!
# normalized force might be wrong?? I get the same alpha curves for everything, it's just for 3N of force, my normalized force is different I thinkg
# make sure our core cladding offset is zero. If it's not we have to use unjacketed fiber as the sensing element
# they were using .633 micrometer cable, that changes the sensitivity a lot. (simply uniformly scales it up and down)
#Trial 2: Slope = 0.045364637014770046, Found Fmax = 0.0, Fmin = 0.1, α=76.9°, β=42.5°
#Tral 3: Slope = 0.045364637014770046, Found Fmax = 0.0, Fmin = 0.1, α=76.9°, β=42.5°

#Use fiber width instead of interaction length for force/area .22 mm


# DO PHOTONICS WESt ABSTRACT
#gamma sensor to patch cable angle



# trial 3:
# Slope = -14656461.171191733, Found stress max = 7927069.1, stress min = 6e+05, α=42.2°, β=45.8°
# Slope = -14656461.171191733, Found stress max = -534743.2, stress min = -8e+06, α=47.8°, β=48.3°
# Slope = -14656461.171191733, Found stress max = -20000693.7, stress min = -3e+07, α=48.8°, β=54.8°


#trial 2:
# Slope = -14656461.171191733, Found stress max = 58815499.5, stress min = 5e+07, α=41.2°, β=29.7°
# Slope = -14656461.171191733, Found stress max = 27291218.4, stress min = 2e+07, α=42.2°, β=38.7°
# Slope = -14656461.171191733, Found stress max = 15055663.4, stress min = 8e+06, α=42.7°, β=43.2°
# Slope = -14656461.171191733, Found stress max = 16867407.6, stress min = 1e+07, α=43.7°, β=42.7°
# Slope = -14656461.171191733, Found stress max = -7170635.9, stress min = -1e+07, α=47.8°, β=50.3°
# Slope = -6197421.457157226, Found stress max = 22193708.1, stress min = 1e+07, α=76.4°, β=43.2°



#trial 4: 
# trial 5: 



#GOING FROM 3.65 to 2.0 on scale ::
# need to add +2.53 to heights: 6 - 4.35




#2.34 pounds


#25.6 mm - black holder + 9.5 - black platform things = 35.1 total
# Scale: 32.57 mm


#Force: 0.03177983425 - trials 4-5
#Force: 0.08993091942 - trials 2-3



# 6/17: my math isn't the issue; compared with chua and __calcfields and __calcfromExEy and everything was the same when i set gamma and beta to zero. 
# I'm thinking my only option now is to sweep through all gammas as well...

#TRIAL 2: 
# Slope = 0.0, Found force max = 0.1, force min = 0.006, α=46.6°, β=55.9°, gamma=18.6
# Slope = 0.0, Found force max = 0.1, force min = 0.006, α=46.6°, β=71.4°, gamma=34.1



# TRIAL 6: 
# INTERACTION LENGTH: 17.94, same force (0.03177)

#Trial 7:
#interaction length: 18.00
# did .03177 6-4.35
# did .03177 6-3.9


# 32.5 = scale
# 34.68 = sample holder

# 2.18 diff


#interaction length: 19.13


#7/6:
# Slope = 0.0, Found force max = 97.898349, force min = 3.897924, α=0.0°, β=34.1°, gamma=6.2
# Slope = 0.0, Found force max = 98.357063, force min = 3.905824, α=3.1°, β=34.1°, gamma=6.2
# Slope = 0.0, Found force max = 99.985516, force min = 3.960257, α=6.2°, β=34.1°, gamma=6.2
# Slope = 0.0, Found force max = 102.881567, force min = 4.064529, α=9.3°, β=34.1°, gamma=6.2
# Slope = 0.0, Found force max = 103.000497, force min = 4.784336, α=37.2°, β=27.9°, gamma=21.7
# Slope = 0.0, Found force max = 104.822470, force min = 4.899857, α=37.2°, β=21.7°, gamma=27.9
# Slope = 0.0, Found force max = 97.898349, force min = 3.897924, α=0.0°, β=6.2°, gamma=34.1
# Slope = 0.0, Found force max = 98.582501, force min = 3.936087, α=3.1°, β=6.2°, gamma=34.1
# Slope = 0.0, Found force max = 100.449737, force min = 4.022607, α=6.2°, β=6.2°, gamma=34.1
# Slope = 0.0, Found force max = 103.613227, force min = 4.162890, α=9.3°, β=6.2°, gamma=34.1
# Slope = 0.0, Found force max = 97.898349, force min = 3.897924, α=0.0°, β=83.8°, gamma=55.9
# Slope = 0.0, Found force max = 98.357063, force min = 3.905824, α=3.1°, β=83.8°, gamma=55.9
# Slope = 0.0, Found force max = 99.985516, force min = 3.960257, α=6.2°, β=83.8°, gamma=55.9
# Slope = 0.0, Found force max = 102.881567, force min = 4.064529, α=9.3°, β=83.8°, gamma=55.9
# Slope = 0.0, Found force max = 103.000497, force min = 4.784336, α=37.2°, β=68.3°, gamma=62.1
# Slope = 0.0, Found force max = 104.822470, force min = 4.899857, α=37.2°, β=62.1°, gamma=68.3
# Slope = 0.0, Found force max = 97.898349, force min = 3.897924, α=0.0°, β=55.9°, gamma=83.8
# Slope = 0.0, Found force max = 98.582501, force min = 3.936087, α=3.1°, β=55.9°, gamma=83.8
# Slope = 0.0, Found force max = 100.449737, force min = 4.022607, α=6.2°, β=55.9°, gamma=83.8
# Slope = 0.0, Found force max = 103.613227, force min = 4.162890, α=9.3°, β=55.9°, gamma=83.8





#7/7 actual alpha = around 45, actual gamma = around 0


#7/7 less weight:

# Slope = 0.0, Found force max = 101.120728, force min = 27.019259, α=43.4°, β=46.6°, gamma=6.2
# Slope = 0.0, Found force max = 101.120728, force min = 27.019259, α=43.4°, β=83.8°, gamma=43.4
# Slope = 0.0, Found force max = 76.083265, force min = 20.900032, α=40.3°, β=6.2°, gamma=46.6
# Slope = 0.0, Found force max = 76.083265, force min = 20.900032, α=40.3°, β=43.4°, gamma=83.8



# 7/7 more weight: 
# Slope = 0.0, Found force max = 255.585391, force min = 60.508062, α=52.8°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 238.454330, force min = 59.464134, α=55.9°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 231.070047, force min = 59.417046, α=59.0°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 231.459129, force min = 60.340783, α=62.1°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 240.394652, force min = 62.311717, α=65.2°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 255.585391, force min = 60.508062, α=52.8°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 238.454330, force min = 59.464134, α=55.9°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 231.070047, force min = 59.417046, α=59.0°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 231.459129, force min = 60.340783, α=62.1°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 240.394652, force min = 62.311717, α=65.2°, β=90.0°, gamma=43.4



#
#-.06771

#TODO: third point in fitting, stress strain curve, polarimeter comparison.


# with just min and max in range:
# Slope = 0.0, Found force max = 255.585391, force min = 86.052636, α=52.8°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 238.454330, force min = 83.409153, α=55.9°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 231.070047, force min = 82.441213, α=59.0°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 231.459129, force min = 82.982068, α=62.1°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 240.394652, force min = 85.061804, α=65.2°, β=46.6°, gamma=0.0
# Slope = 0.0, Found force max = 255.585391, force min = 86.052636, α=52.8°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 238.454330, force min = 83.409153, α=55.9°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 231.070047, force min = 82.441213, α=59.0°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 231.459129, force min = 82.982068, α=62.1°, β=90.0°, gamma=43.4
# Slope = 0.0, Found force max = 240.394652, force min = 85.061804, α=65.2°, β=90.0°, gamma=43.4

