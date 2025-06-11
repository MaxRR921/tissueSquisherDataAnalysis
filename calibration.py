import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import pandas as pd
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
          




          
          


       def calcNormalizedPower(self, S1, S2):
          return S1/(S1+S2), S2/(S1+S2) 

       def calcNormalizedPowerDifference(self, S1, S2):
          return np.abs((S2 - S1))/np.abs(S1+S2)
       
       def calcNormalizedCrossIntensity(self, S1, S2):
            return S2/S1

       def plotNormalizedPowersVsAlpha(self, alphaValues, forces):
          plt.figure()
          Sdifferences  = np.zeros(len(alphaValues))
          curves = []
          S10=0
          for j in range(len(forces)):
               Sdifferences  = np.zeros(len(alphaValues))
               for i in range(len(alphaValues)):
                    self.alpha = alphaValues[i]
                    Ex, Ey = self.__calcFields(forces[j])
                    S1, S2 = self.__calcPower(Ex, Ey)
                    if(i == 0):
                         S10 = S1
                    Sdifferences[i] = self.calcNormalizedCrossIntensity(S10, S2)
               curves.append((forces[j], Sdifferences.copy()))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(alphaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('Alpha (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Alpha')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.alpha = np.pi/4

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
                    Ex, Ey = self.__calcFields(forces[j])
                    S1, S2 = self.__calcPower(Ex, Ey)
                    s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2)
               print("S1:", s1Arr)
               curves.append((forces[j], s1Arr.copy()-s2Arr.copy()))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(gammaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('gamma (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Gamma')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.gamma = np.pi/4


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
                    Ex, Ey = self.__calcFields(forces[j])
                    S1, S2 = self.__calcPower(Ex, Ey)
                    s1Arr[i], s2Arr[i] = self.calcNormalizedPower(S1, S2)
               print("S1:", s1Arr)
               curves.append((forces[j], s1Arr.copy()-s2Arr.copy()))
               print("S1:")

          for curve in curves:
               plt.plot(np.rad2deg(betaValues), curve[1], label=f'Force: {curve[0]} ')

          plt.xlabel('gamma (deg)')
          plt.ylabel('Normalized Power')
          plt.title('Normalized S1 and S2 vs. Gamma')
          plt.legend()
          plt.grid(True)

          plt.show()
          self.gamma = np.pi/4

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
          crossIntensityArr = np.zeros(len(forces))

          for i in range(len(forces)):
               Ex, Ey = self.__calcFields(forces[i])
               s1Arr[i], s2Arr[i] = self.__calcPower(Ex, Ey) 
               crossIntensityArr[i] = self.calcNormalizedCrossIntensity(s1Arr[0], s2Arr[i])
               print("normalized cross intensity: ", crossIntensityArr[i])
                

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
               Ex, Ey = self.__calcFields(forces[i])
               S1, S2 = self.__calcPower(Ex, Ey) 
               Sdiff[i] = self.calcNormalizedPowerDifference(S1, S2)


          # --- Plot 1: Sdiff vs Force ---
          plt.figure()
          plt.plot(forces, Sdiff, label='Sdifference (W)', color='tab:blue')

          coeffs1 = np.polyfit(forces, Sdiff, deg=4)
          poly1 = np.poly1d(coeffs1)
          x_fit1 = np.linspace(min(forces), max(forces), 500)
          y_fit1 = poly1(x_fit1)
          plt.plot(x_fit1, y_fit1, '--', label='Fitted Curve', color='tab:orange')

          plt.xlabel('Force')
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

          coeffs2 = np.polyfit(Sdiff, forces, deg=1)
          poly2 = np.poly1d(coeffs2)
          x_fit2 = np.linspace(min(Sdiff), max(Sdiff), 500)
          y_fit2 = poly2(x_fit2)
          plt.plot(x_fit2, y_fit2, '--', label='Fitted Curve', color='tab:red')

          plt.xlabel('Power Difference Normalized')
          plt.ylabel('Force')
          plt.title('Force vs Power Difference')
          plt.legend()
          plt.grid(True)
          plt.show()

          eq2 = f"{coeffs2[0]:.5e} * Sdiff  + {coeffs2[1]:.5e}"
          print("Force = " + eq2)


       def calculateAlphaAndBeta(self, targetForce):
            curves = []
            df = pd.read_csv('trial3.csv')
            sdiffs = df['Sdifference'].dropna().values
          #   maxPower = np.max(sdiffs)
          #   minPower = np.min(sdiffs)
            maxPower = np.max(sdiffs[sdiffs != 0])
            minPower = np.min(sdiffs[sdiffs != 0])
            print("Max power: ", maxPower, "Min power: ", minPower)

            finds = []
            #theoretical:
            done = False
            for alpha in np.linspace(0, np.pi/2, 90):
               self.alpha = alpha
               for beta in np.linspace(0, np.pi/2, 90):
                    self.beta = beta
                    forces = np.linspace(0, targetForce, 500)
                    powerDifferences = np.zeros(500)
                    for i in range (len(forces)): 
                         Ex, Ey = self.__calcFields(forces[i])
                         S1, S2 = self.__calcPower(Ex, Ey)
                         powerDifferences[i] = self.calcNormalizedPowerDifference(S1, S2)
                     # plot at α≈π/4, β≈π/4
                    coeffs2 = np.polyfit(powerDifferences, forces, deg=1)
                    poly2 = np.poly1d(coeffs2)
                    x_fit2 = np.linspace(min(powerDifferences), max(powerDifferences), 500)
                    y_fit2 = poly2(x_fit2)
                    fMax = poly2(maxPower)
                    fMin = poly2(minPower)
                    print("fmin: ", fMin, "fMax: ", fMax, "alpha: ", np.rad2deg(alpha), "beta: ", np.rad2deg(beta))
                    if np.isclose(np.abs(fMax - fMin), targetForce, atol=1):
                         finds.append(f"Slope = {y_fit2[0]}, Found Fmax = {fMax:.001f}, Fmin = {fMin:.001}, α={np.rad2deg(self.alpha):.1f}°, β={np.rad2deg(self.beta):.1f}°")
                         curves.append((x_fit2, y_fit2, maxPower, fMax, minPower, fMin))


            for find in finds:
               print(find)

            plt.figure(figsize=(8, 6))
            for x_fit2, y_fit2, maxP, fMax, minP, fMin in curves:
               plt.plot(x_fit2, y_fit2)
               plt.plot(maxP, fMax, 'ro')  # red point for max
               plt.plot(minP, fMin, 'bo')  # blue point for min

               plt.xlabel('Power Difference')
               plt.ylabel('Force')
               plt.title('Fitted Curves with Fmin and Fmax Points')
               plt.grid(True)
               plt.tight_layout()
               plt.show()



                    

npoints = 500
c = Calibration(.02365)
# c.calculateAlphaAndBeta(0.08993091942) # 6.71 N is the target force
# c.plotStressVsPowerDifference(np.linspace(0, 0.090748, 500))
# c.plotPowerDifferencesNormalized(np.linspace(0, 0.08993091942, 500))
c.plotNormalizedPowersSeperately(np.linspace(0,0.08993091942, 500)) 
c.plotNormalizedPowersVsAlpha(np.linspace(0,np.pi,500), np.linspace(0,2.5,3)) #GOOD! look at envelope maximum... 45 degrees is the maximum of the envelope
c.plotNormalizedPowersVsGamma(np.linspace(0,np.pi,500), np.linspace(0,0.090748,3))
c.plotNormalizedPowersVsBeta(np.linspace(0,np.pi,500), np.linspace(0,0.090748,3))
# alphas = np.deg2rad([30, 45, 60, 75])
# c.plotPhiVsNormalizedForce(np.linspace(0,50,500), alphas)
# gammas = np.deg2rad([30, 45, 60, 75])
# c.plotGammaVsSingleForce(gammas, 0.090748)

print(c.b)

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