import numpy as np
import matplotlib.pyplot as plt

"""
Potential issues:
- Ex and Ey are each 1 value, not arrays. 


"""



def ex():
        npoints = 500
        # Material properties of fiber
        Y = 7.3e10  # Young's modulus of fiber in N/m^2
        sigma = 0.17  # Poisson's ratio at 633nm wavelength
        N = 1.46  # Refractive index
        N_s = 1.7
        N_f = 2.0
        N_s = float(N_s)
        N_f = float(N_f)
        p_11 = 0.121  # Photoelastic constants
        p_12 = 0.27
        p_44 = (p_11 - p_12) / 2  # For isotropic materials
        b = 62.5e-6  # Radius of cladding in meters
        Lb_0 = 2e-3  # Unstressed beat length, 2 mm

        S1 = np.zeros(npoints, dtype=complex)
        S2 = np.zeros(npoints, dtype=complex)
        Sdifference = np.zeros(npoints, dtype=complex)
        ExList = np.zeros(npoints, dtype=complex)
        EyList = np.zeros(npoints, dtype=complex)

        f = np.linspace(0, 10.36436, npoints)  # Force in N/m (2D analysis)
        l = np.linspace(7.25, 20, npoints)  # Interaction length, about 18 mm
        Ex_0 = 1
        lambda_light = 1550e-9  # Wavelength of light in fiber
        k = 1/lambda_light

        alpha = np.pi / 4  # angle between applied force and fast and slow axis of the fiber.
        beta = np.pi / 6  # Angle between polarized light and fast and slow axis of the fiber.
        delta = 570  # Extra phase from traveling through unstressed fiber
        gamma = np.pi/2# Angle of PM fiber wrt polarimeter. Should be 0 or pi/2
        eta = 376.730313 

        F = 2 * N**3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_light * np.pi * b * Y)  # Normalized force66
        phiVals = 0.5 * np.arctan((F * np.sin(2 * alpha)) / (1 + F * np.cos(2 * alpha)))  # Angle of rotated birefringence
        Lb = Lb_0 * (1 + F**2 + 2 * F * np.cos(2 * alpha))**(-1/2)  # Modified beat length
        print("PhiVals:", phiVals)
        print("LbVals: ", Lb)
        print("F", F)

        for li in range(npoints):
        
                A = ((np.cos(gamma)*np.cos(phiVals[li])) - (np.exp(1j*delta) * np.sin(gamma) * np.sin(phiVals[li]))) * np.cos(beta + phiVals[li])
                B = ((np.cos(gamma) * np.cos(phiVals[li])) + (np.exp(1j*delta) * np.sin(gamma) * np.cos(phiVals[li]))) * np.sin(beta+phiVals[li])
                C = ((-np.sin(gamma)*np.cos(phiVals[li])) - (np.exp(1j*delta) * np.cos(gamma) * np.sin(phiVals[li]))) * np.cos(beta + phiVals[li])
                D = ((-np.sin(gamma)*np.sin(phiVals[li])) + (np.exp(1j * delta)*np.cos(gamma)*np.cos(phiVals[li]))) * np.sin(beta + phiVals[li])

                Ex = Ex_0*np.exp(-1j*k*N*l[li]) * ((np.exp(-1j*k*l[li]*((2*np.pi)/(k*Lb[li])))*A) + B)
                Ey = Ex_0*np.exp(-1j*k*N*l[li]) * ((np.exp(-1j*k*l[li]*((2*np.pi)/(k*Lb[li])))*C) + D)

                # print("Ex: ", Ex)
                # print("Ey: ", Ey)
                
                #Why am I doing conjugate here??
                # ExConj = np.conjugate(Ex)
                # EyConj = np.conjugate(Ey)

                # Compute power
                Ex2= np.abs(Ex)**2  # Equivalent to |Ex|^2
                Ey2= np.abs(Ey)**2 #Equivalent to |Ey|^2
                # print("Ex2: ", Ex2)
                # print("Ey2: ", Ey2)
                # eta = 376.73  # Characteristic impedance of free space (ohms)
               
                S1[li] = Ex2/(2*eta)
                S2[li] = Ey2/(2*eta)
                Sdifference[li] = S1[li] - S2[li]
                ExList[li] = Ex
                EyList[li] = Ey
                
        print(ExList)
        print(EyList) 
        plt.figure()
        plt.plot(f, S1, label='S1')
        plt.plot(f, S2, label='S2')
        plt.plot(f, Sdifference, label='difference')
        plt.xlabel('Force (N/m)')
        plt.ylabel('S1, S2 (Real part)')
        plt.title('S1 and S2 vs. Force')
        plt.legend()
        plt.grid(True)
        plt.show()

        # Second Figure: Plot just the difference
        plt.figure()
        plt.plot(f, Sdifference, label='Difference (S2 - S1)', color='red')
        plt.xlabel('Force (N/m)')
        plt.ylabel('Difference (Real part)')
        plt.title('Difference (S1 - S2) vs. Force')
        plt.legend()
        plt.grid(True)

        plt.show()


              
#ex()




# # Material properties of fiber
# Y = 7.3e10  # Young's modulus of fiber in N/m^2
# sigma = 0.17  # Poisson's ratio at 633nm wavelength
# N = 1.46  # Refractive index
# p_11 = 0.121  # Photoelastic constants
# p_12 = 0.27
# p_44 = (p_11 - p_12) / 2  # For isotropic materials
# b = 62.5e-6  # Radius of cladding in meters
# Lb_0 = 2e-3  # Unstressed beat length, 2 mm

# lambda_light = 980e-9  # Wavelength of light in fiber

# # Variables
# npoints = 100
# f = np.linspace(0, 500, npoints)  # Force in N/m (2D analysis)
# l = np.linspace(7.25e-3, 20e-3, npoints)  # Interaction length, about 18 mm

# alpha = np.pi / 2  # Angle of birefringence axis wrt force
# beta = np.pi / 3  # Angle of PM fiber wrt polarizer
# delta = 0  # Extra phase from traveling through unstressed fiber
# gamma = np.pi / 2  # Angle of PM fiber wrt polarimeter. Should be 0 or pi/2

# # Some simplified equations for a fiber without a jacket
# F = 2 * N**3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_light * np.pi * b * Y)  # Normalized force
# phi = 0.5 * np.arctan((F * np.sin(2 * alpha)) / (1 + F * np.cos(2 * alpha)))  # Angle of rotated birefringence
# Lb = Lb_0 * (1 + F**2 + 2 * F * np.cos(2 * alpha))**(-1/2)  # Modified beat length
# print("PHIVALS: ", phi)
# print("F VALS: ", F)
# print("Lb values: ", Lb)
# SOP = np.zeros((npoints, npoints))
# for q in range(npoints):
#     arg = (2 * np.pi * l[q]) / Lb

#     # Calculate the stokes parameters
#     # Compute the expression
#     term1 = (np.sin(gamma) * (np.exp(-arg * 1j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#                             np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#             np.exp(-delta * 1j) * np.cos(gamma) * (np.exp(-arg * 1j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) +
#                                                 np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))

#     term2 = (np.sin(gamma) * (np.exp(arg * 1j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#                             np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#             np.exp(delta * 1j) * np.cos(gamma) * (np.exp(arg * 1j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) +
#                                                 np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))

#     term3 = (np.cos(gamma) * (np.exp(-arg * 1j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#                             np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi)) -
#             np.exp(-delta * 1j) * np.sin(gamma) * (np.exp(-arg * 1j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) +
#                                                 np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))

#     term4 = (np.cos(gamma) * (np.exp(arg * 1j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#                             np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi)) -
#             np.exp(delta * 1j) * np.sin(gamma) * (np.exp(arg * 1j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) +
#                                                 np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))

#     s1 = -np.abs(term1 * term2) + np.abs(term3 * term4)




#     # Compute the expression
#     term1 = (np.cos(gamma) * np.sin(delta) * (np.sin(beta) * np.sin(phi)**2 + np.cos(arg) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) - np.cos(beta) * np.cos(phi) * np.sin(phi)) +
#             np.sin(arg) * np.sin(gamma) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#             np.cos(delta) * np.cos(gamma) * np.sin(arg) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)))

#     term2 = (np.sin(delta) * np.sin(gamma) * (np.sin(beta) * np.sin(phi)**2 + np.cos(arg) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) - np.cos(beta) * np.cos(phi) * np.sin(phi)) -
#             np.cos(gamma) * np.sin(arg) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#             np.cos(delta) * np.sin(arg) * np.sin(gamma) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)))

#     term3 = (np.sin(gamma) * (np.cos(beta) * np.cos(phi)**2 + np.cos(arg) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) - np.cos(phi) * np.sin(beta) * np.sin(phi)) +
#             np.cos(delta) * np.cos(gamma) * (np.sin(beta) * np.sin(phi)**2 + np.cos(arg) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) - np.cos(beta) * np.cos(phi) * np.sin(phi)) -
#             np.cos(gamma) * np.sin(arg) * np.sin(delta) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)))

#     term4 = (np.cos(gamma) * (np.cos(beta) * np.cos(phi)**2 + np.cos(arg) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi)) - np.cos(phi) * np.sin(beta) * np.sin(phi)) -
#             np.cos(delta) * np.sin(gamma) * (np.sin(beta) * np.sin(phi)**2 + np.cos(arg) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)) - np.cos(beta) * np.cos(phi) * np.sin(phi)) +
#             np.sin(arg) * np.sin(delta) * np.sin(gamma) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi)))

#     s2 = 2 * (term1 * term2) - 2 * (term3 * term4)

#     s3 = (np.cos(2 * phi)**2 * np.sin(2 * beta) * np.sin(delta) -
#       np.sin(2 * beta) * np.sin(delta) -
#       np.cos(2 * beta) * np.sin(2 * phi) * np.cos(delta) * np.sin(arg) -
#       np.cos(2 * phi) * np.sin(2 * beta) * np.cos(delta) * np.sin(arg) -
#       np.cos(2 * phi)**2 * np.sin(2 * beta) * np.cos(arg) * np.sin(delta) +
#       np.cos(2 * beta) * np.cos(2 * phi) * np.sin(2 * phi) * np.sin(delta) -
#       np.cos(2 * beta) * np.cos(2 * phi) * np.sin(2 * phi) * np.cos(arg) * np.sin(delta))



#     # Calculate the phase-angle of the theoretical fit circle
#     x = s2
#     y = s3

#     # Find the angle of the circle (phase)
#     phase = np.arctan2(y, x) / np.pi

#     # Normalize the phase so it starts at zero and is always increasing or decreasing
#     k = len(phase)
#     phaseCounter = np.zeros(k)  # This variable counts how many times the phase wraps around
#     wrapCount = 0

#     # Check to see if the sign has changed
#     for i in range(k - 1):
#         if np.sign(x[i]) == -1:
#             if (np.sign(y[i]) == 1) and (np.sign(y[i + 1]) == -1):
#                 wrapCount += 2
#             elif (np.sign(y[i]) == -1) and (np.sign(y[i + 1]) == 1):
#                 wrapCount -= 2
#         phaseCounter[i + 1] = wrapCount

#     phase = phase + phaseCounter - phase[0]  # Normalize phase to start at 0

#     SOP[q, :] = phase

# force = f / .000245  # 245 um for 635 and 400 um for 1550

# # Plot the phase vs. force graph for the theoretical fit
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# X, Y = np.meshgrid(force, l)
# ax.plot_surface(X, Y, SOP, cmap='viridis')

# ax.set_title('Pol change vs. applied stress and length')
# ax.set_xlabel('Stress (Pa)')
# ax.set_ylabel('Interaction length (m)')
# ax.set_zlabel('Phase')

# plt.show()






# def calculateE():
#         # Material properties of fiber
#         Y = 7.3e10  # Young's modulus of fiber in N/m^2
#         sigma = 0.17  # Poisson's ratio at 633nm wavelength
#         N = 1.46  # Refractive index
#         N_s = 1.7
#         N_f = 2.0
#         N_s = float(N_s)
#         N_f = float(N_f)
#         p_11 = 0.121  # Photoelastic constants
#         p_12 = 0.27
#         p_44 = (p_11 - p_12) / 2  # For isotropic materials
#         b = 62.5e-6  # Radius of cladding in meters
#         Lb_0 = 2e-3  # Unstressed beat length, 2 mm

#         Ex_0 = .1

#         lambda_light = 1550e-9  # Wavelength of light in fiber
#         k = 1/lambda_light
        
#         # Variables
#         npoints = 100
#         f = np.linspace(0, 500, npoints)  # Force in N/m (2D analysis)
#         l = np.linspace(7.25, 20, npoints)  # Interaction length, about 18 mm

#         alpha = np.pi / 2  # Angle of birefringence axis wrt force
#         beta = np.pi / 3  # Angle of PM fiber wrt polarizer
#         delta = 0  # Extra phase from traveling through unstressed fiber
#         gamma = np.pi / 2  # Angle of PM fiber wrt polarimeter. Should be 0 or pi/2
#         eta = 376.730313

#         # Some simplified equations for a fiber without a jacket
#         F = 2 * N**3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_light * np.pi * b * Y)  # Normalized force66
#         phiVals = 0.5 * np.arctan((F * np.sin(2 * alpha)) / (1 + F * np.cos(2 * alpha)))  # Angle of rotated birefringence
#         Lb = Lb_0 * (1 + F**2 + 2 * F * np.cos(2 * alpha))**(-1/2)  # Modified beat length
#         power = np.zeros((npoints, npoints))
#         ExList = np.zeros((npoints, npoints))
#         SOP = np.zeros((npoints, npoints))
#         for li in range(npoints):
#                 phi = phiVals[li]
#                 M1 = np.array([
#                         [np.cos(gamma), np.sin(gamma)],
#                         [-np.sin(gamma), np.cos(gamma)]
#                 ])

#                 M2 = np.array([
#                         [1, 0],
#                         [0, np.exp(1j * delta)]
#                 ])

#                 M3 = np.array([
#                         [np.cos(phi), -np.sin(phi)],
#                         [np.sin(phi), np.cos(phi)]
#                 ])

#                 M4 = np.array([
#                         [np.exp(-1j * k * N_s * l[li]), 0],
#                         [0, np.exp(-1j * k * N_f * l[li])]
#                 ])

#                 M5 = np.array([
#                         [np.cos(phi), np.sin(phi)],
#                         [-np.sin(phi), np.cos(phi)]
#                 ])

#                 M6 = np.array([
#                         [np.cos(beta), np.sin(beta)],
#                         [-np.sin(beta), np.cos(beta)]
#                 ])

#                 # Initial field vector
#                 E_initial = np.array([Ex_0, 0])

#                 # Calculate the resulting field vector
#                 E_final = M1 @ M2 @ M3 @ M4 @ M5 @ M6 @ E_initial

#                 # Extract Ex and Ey from the resulting field vector
#                 Ex = E_final[0]
#                 Ey = E_final[1]

#                 print(E_final)
#                 # Calculate the magnitude of the electric field
#                 E_peak = np.sqrt(np.abs(Ex)**2 + np.abs(Ey)**2)

#                 print("EPEAK:", E_peak)

#                 # Calculate the average power per unit area
#                 average_power = (E_peak**2) / (2*eta)
#                 print(average_power)
#                 power[li] = average_power
#                 ExList[li] = Ex
        
#         force = f / .000245  # 245 um for 635 and 400 um for 1550

#         # Plot the phase vs. force graph for the theoretical fit
#         fig = plt.figure()
#         ax = fig.add_subplot(111, projection='3d')
#         X, Y = np.meshgrid(force, l)
#         ax.plot_surface(X, Y, ExList, cmap='viridis')

#         ax.set_title('Pol change vs. applied stress and length')
#         ax.set_xlabel('Stress (Pa)')
#         ax.set_ylabel('Interaction length (m)')
#         ax.set_zlabel('Ex')

#         plt.show() 



class Calibration: #Px - Py/Px+Py Use Ex0, normalize power, should match 
     def __init__(self, npoints, force_values, interaction_length, P_in):
          # Material properties of the fiber
          self.Y = 7.3e10 # young's modulus of the fiber in N/m^2
          self.sigma = 0.17 # Poisson's ratio at 633nm wavelength
          self.N = 1.46 # Refractive index of the fiber 
          self.p_11 = 0.121 #photelastic constants 
          self.p_12 = 0.27
          self.b = 62.5e-6 # Radius of fiber cladding in meters 
          self.Lb_0 = 2e-3 # unstressed beat length in meters
          self.fiberWavelength = 2e-3
          self.k=1/self.fiberWavelength
          
          
          
          self.fiberArea = 8.5e-11 # powermeter sensor area in meters 
          self.P_in = P_in
          self.npoints = npoints

          #calculated values
          self.S1 = np.zeros(npoints) # powermeter 1 power
          self.S2 = np.zeros(npoints) # powermeter 2 power 
          self.S1Normalized = np.zeros(npoints)
          self.S2Normalized = np.zeros(npoints)
          self.Sdifferences = np.zeros(npoints) # difference between the two powers 
          self.SdifferencesNormalized = np.zeros(npoints)
          self.stresses = np.zeros(npoints)

          self.ExList = np.zeros(npoints, dtype=complex)
          self.EyList = np.zeros(npoints, dtype=complex)


          self.f = force_values
          self.l = interaction_length
          self.Ex_0 = 1

          self.alpha = np.pi/4
          self.beta = np.pi/4
          self.delta = 0
          self.gamma = np.pi/2
          self.eta = 376.730313

          self.normalizedForce = 2 * self.N**3 * (1 + self.sigma) * (self.p_12 - self.p_11) * self.Lb_0 * self.f / (self.fiberWavelength * np.pi * self.b * self.Y)  # Normalized force66
          self.phiValues = 0.5 * np.arctan((self.normalizedForce * np.sin(2 * self.alpha)) / (1 + self.normalizedForce * np.cos(2 * self.alpha)))  # Angle of rotated birefringence 
          self.Lb = self.Lb_0 * (1 + self.normalizedForce**2 + 2 * self.normalizedForce * np.cos(2 * self.alpha))**(-1/2)  # Modified beat length
          self.initialPowerDifference = 0
          self.finalPowerDifference = 0

     def calculatePowers(self, initialHeight, finalHeight):
          for li in range(self.npoints):          
               A = ((np.cos(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.sin(self.phiValues[li])))
               B = ((-np.cos(self.gamma) * np.sin(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.cos(self.phiValues[li])))
               C = ((np.cos(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.sin(self.phiValues[li])))
               D = ((-np.cos(self.gamma) * np.sin(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.cos(self.phiValues[li])))
               E = ((-np.sin(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.cos(self.gamma) * np.sin(self.phiValues[li])))
               F = ((np.sin(self.gamma)*np.sin(self.phiValues[li])) + (np.exp(1j * self.delta)*np.cos(self.gamma)*np.cos(self.phiValues[li])))
               G = ((-np.sin(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.cos(self.gamma) * np.sin(self.phiValues[li])))
               H = ((np.sin(self.gamma)*np.sin(self.phiValues[li])) + (np.exp(1j * self.delta)*np.cos(self.gamma)*np.cos(self.phiValues[li])))
               
               I = (np.cos(self.phiValues[li]) * A) - (np.sin(self.phiValues[li]) * B)
               J = (np.sin(self.phiValues[li]) * C) - (np.cos(self.phiValues[li]) * D)
               K = (np.cos(self.phiValues[li] * E)) - (np.sin(self.phiValues[li]) * F)
               L = (np.sin(self.phiValues[li]) * G) - (np.cos(self.phiValues[li]) * H)

               print("THIS TERM IS: ", np.exp(-2j*self.k*self.l*((2*np.pi)/(self.k*self.Lb[li]))) * np.exp(-2j*self.k*self.N*self.l))
               Ex = (self.Ex_0) * np.exp(-2j*self.k*self.N*self.l)*np.exp(-2j*self.k*self.l*((2*np.pi)/(self.k*self.Lb[li]))) * (I*np.cos(self.beta) - J*np.sin(self.beta))
               Ey = (self.Ex_0) * np.exp(-2j*self.k*self.N*self.l     )*np.exp(-2j*self.k*self.l*((2*np.pi)/(self.k*self.Lb[li]))) * (K*np.cos(self.beta) - L*np.sin(self.beta))               

               # Compute power
               Ex2= np.abs(Ex)**2  # Equivalent to |Ex|^2
               Ey2= np.abs(Ey)**2 #Equivalent to |Ey|^2
               eta = 376.73  # Characteristic impedance of free space (ohms)

               self.S1[li] = Ex2/(2*eta) * self.fiberArea 
               self.S2[li] = Ey2/(2*eta) * self.fiberArea 
               self.S1Normalized[li] = self.S1[li]/self.P_in
               self.S2Normalized[li] = self.S2[li]/self.P_in
               self.stresses[li] = self.f[li]/self.l #might have to change this
               self.strains = np.linspace(initialHeight, finalHeight, npoints)
               for i, val in enumerate(self.strains):
                    print("val = ", val)
                    print("initialHeight - val ", np.abs((initialHeight - val)))
                    self.strains[i] = (initialHeight - val) / initialHeight
                    print("STRAIN ACTUAL: ", self.strains[i])
               print("SELF.STRAINS: ", self.strains)
               
               self.Sdifferences[li] = self.S2[li] - self.S1[li]
               self.SdifferencesNormalized[li] = self.S2Normalized[li] - self.S1Normalized[li]
               
               if (li == 0):
                    self.initialPowerDifference = self.Sdifferences[li]
                    self.initialPower1 = self.S1Normalized[li]
                    self.initialPower2 = self.S2Normalized[li]


               if(li == self.npoints - 1):
                    self.finalPowerDifference = self.Sdifferences[li]
                    self.finalPower1 = self.S1Normalized[li]
                    self.finalPower2 = self.S2Normalized[li]

               self.ExList[li] = Ex
               self.EyList[li] = Ey
               
               

     def __calculatePowersVaryLength(self, l):
          S1 = np.zeros(self.npoints)
          S2 = np.zeros(self.npoints)
          S1Normalized = np.zeros(self.npoints)
          S2Normalized = np.zeros(self.npoints)
          Sdifferences = np.zeros(self.npoints)
          SdifferencesNormalized = np.zeros(self.npoints)

          for li in range(self.npoints):          
               A = ((np.cos(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.sin(self.phiValues[li])))
               B = ((-np.cos(self.gamma) * np.sin(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.cos(self.phiValues[li])))
               C = ((np.cos(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.sin(self.phiValues[li])))
               D = ((-np.cos(self.gamma) * np.sin(self.phiValues[li])) + (np.exp(1j*self.delta) * np.sin(self.gamma) * np.cos(self.phiValues[li])))
               E = ((-np.sin(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.cos(self.gamma) * np.sin(self.phiValues[li])))
               F = ((np.sin(self.gamma)*np.sin(self.phiValues[li])) + (np.exp(1j * self.delta)*np.cos(self.gamma)*np.cos(self.phiValues[li])))
               G = ((-np.sin(self.gamma)*np.cos(self.phiValues[li])) + (np.exp(1j*self.delta) * np.cos(self.gamma) * np.sin(self.phiValues[li])))
               H = ((np.sin(self.gamma)*np.sin(self.phiValues[li])) + (np.exp(1j * self.delta)*np.cos(self.gamma)*np.cos(self.phiValues[li])))
               
               I = (np.cos(self.phiValues[li]) * A) - (np.sin(self.phiValues[li]) * B)
               J = (np.sin(self.phiValues[li]) * C) - (np.cos(self.phiValues[li]) * D)
               K = (np.cos(self.phiValues[li] * E)) - (np.sin(self.phiValues[li]) * F)
               L = (np.sin(self.phiValues[li]) * G) - (np.cos(self.phiValues[li]) * H)

               print("THIS TERM IS: ", np.exp(-2j*self.k*l*((2*np.pi)/(self.k*self.Lb[li]))) * np.exp(-2j*self.k*self.N*l))
               Ex = (self.Ex_0) * np.exp(-2j*self.k*self.N*l)*np.exp(-2j*self.k*l*((2*np.pi)/(self.k*self.Lb[li]))) * (I*np.cos(self.beta) - J*np.sin(self.beta))
               Ey = (self.Ex_0) * np.exp(-2j*self.k*self.N*l)*np.exp(-2j*self.k*l*((2*np.pi)/(self.k*self.Lb[li]))) * (K*np.cos(self.beta) - L*np.sin(self.beta))               

               # Compute power
               Ex2= np.abs(Ex)**2  # Equivalent to |Ex|^2
               Ey2= np.abs(Ey)**2 #Equivalent to |Ey|^2
               eta = 376.73  # Characteristic impedance of free space (ohms)

               S1[li] = Ex2/(2*eta) * self.fiberArea 
               S2[li] = Ey2/(2*eta) * self.fiberArea 
               S1Normalized[li] = S1[li]/self.P_in
               S2Normalized[li] = S2[li]/self.P_in
               self.stresses[li] = self.f[li]/l
               
               Sdifferences[li] = S2[li] - S1[li]
               SdifferencesNormalized[li] = S2Normalized[li] - S1Normalized[li]
               
               if (li == 0):
                    self.initialPowerDifference = self.Sdifferences[li]
                    self.initialPower1 = self.S1[li]
                    self.initialPower2 = self.S2[li]
                    initialSDifferenceNormalized = SdifferencesNormalized[li]
                    

               if(li == self.npoints - 1):
                    self.finalPowerDifference = self.Sdifferences[li]
                    self.finalPower1 = self.S1[li]
                    self.finalPower2 = self.S2[li]
                    finalS1DifferenceNormalized = SdifferencesNormalized[li]
               self.ExList[li] = Ex
               self.EyList[li] = Ey
          return finalS1DifferenceNormalized - initialSDifferenceNormalized

     def varyLength(self, ls):
          powerdiffs = np.zeros(100)
          for i in range(0,100):
               powerdiffs[i]=self.__calculatePowersVaryLength(ls[i])

          plt.figure()
          plt.plot(ls, powerdiffs, label='change in power difference')
          plt.xlabel('interaction length')
          plt.ylabel('change in power difference')
          plt.title('Change in power difference')
          plt.legend()
          plt.grid(True)

          # fix the scaling weirdness
          plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)  # no offset

          plt.show()

     
     def plotPowers(self):
          plt.figure()
          plt.plot(self.f, self.S1, label='S1')
          plt.plot(self.f, self.S2, label='S2')
          plt.xlabel('Force (N)')
          plt.ylabel('S1, S2 (Real part) (W)')
          plt.title('S1 and S2 vs. Force')
          plt.legend()
          plt.grid(True)
          plt.show()

     def plotStressStrain(self):
          plt.figure()
          plt.plot(self.strains, self.stresses, label='stress strain')
          plt.ylabel('Stress N/M')
          plt.xlabel('Strain (%)')       
          plt.legend()
          plt.grid(True)
          plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)  # no offset
          plt.show()
          
     def plotNormalizedPowers(self):
          plt.figure()
          plt.plot(self.stresses, self.S1Normalized, label='S1')
          plt.plot(self.stresses, self.S2Normalized, label='S2')
          plt.xlabel('Stress (N/M)')
          plt.ylabel('S1, S2 Normalized')
          plt.title('S1 and S2 vs. Stress')
          plt.legend()
          plt.grid(True)
          plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)  # no offset
          plt.show()

     def plotPowerDifferences(self):
          plt.figure()
          plt.plot(self.f, self.SdifferencesNormalized, label='Sdifference (W)')
          plt.xlabel('Force (N)')
          plt.ylabel('Power Difference')
          plt.title('Power Difference vs. Force')
          plt.legend()
          plt.grid(True)
          plt.show()

     def plotPowerDifferencesNormalized(self):
          plt.figure()
          plt.plot(self.stresses, self.SdifferencesNormalized, label='Sdifference (W)')
          plt.xlabel('Stress (N/M)')
          plt.ylabel('Power Difference Normalized')
          plt.title('Power Difference vs. Stress')
          plt.legend()
          plt.grid(True)
          plt.show()

     def plotPowersSeperately(self):
          plt.figure()
          plt.plot(self.f, self.S1, label='S1 (W)')
          plt.xlabel('Force (N)')
          plt.ylabel('Power Difference')
          plt.title('Power Difference vs. Force')
          plt.legend()
          plt.grid(True)
          plt.show()

          plt.figure()
          plt.plot(self.f, self.S2, label='S2 (W)')
          plt.xlabel('Force (N)')
          plt.ylabel('Power Difference')
          plt.title('Power Difference vs. Force')
          plt.legend()
          plt.grid(True)
          plt.show()

     def calculateEx0(self, P_in, MFD=10.5e-6, n=1.46, epsilon0=8.85e-12, c=3e8):
          """
          Calculate the peak electric field amplitude E_x0 (in V/m) for a given input power.

          Parameters:
               P_in      : Input power in Watts.
               MFD       : Mode Field Diameter of the fiber (in meters). Default is 10.5e-6 m.
               n         : Effective refractive index of the fiber mode. Default is 1.46.
               epsilon0  : Permittivity of free space (F/m). Default is 8.85e-12.
               c         : Speed of light in vacuum (m/s). Default is 3e8.

          Returns:
               E_x0      : Peak electric field amplitude in V/m.

          The formula used is:

               E_x0 = sqrt( 2 * P_in / [ n * epsilon0 * c * π * (MFD/2)^2 ] )
          """
          A_eff = np.pi * (MFD / 2)**2
          E_x0 = np.sqrt((2 * P_in) / (n * epsilon0 * c * A_eff))
          return E_x0

     def generate_function_force_to_powerdiff(self):
          m, b = np.polyfit(self.f, self.Sdifferences, 1)
          fmodel = lambda F_in: m*F_in + b  
          return fmodel
     
     def generate_function_powerdiff_to_force(self):
          # fit Sdifference = m*force + b
          m, b = np.polyfit(self.f, self.SdifferencesNormalized, 1)
          # return a function that inverts that relation:
          print("m: ", m)
          print("b: ", b)
          print("TEST: ", (1.5e-12-b)/m)
          return lambda Sdiff: (Sdiff - b) / m




          
def ex1(alphaVal):
     npoints = 500
     # Material properties of fiber
     Y = 7.3e10  # Young's modulus of fiber in N/m^2
     sigma = 0.17  # Poisson's ratio at 633nm wavelength
     N = 1.46  # Refractive index
     N_s = 1.7
     N_f = 2.0
     N_s = float(N_s)
     N_f = float(N_f)
     p_11 = 0.121  # Photoelastic constants
     p_12 = 0.27
     p_44 = (p_11 - p_12) / 2  # For isotropic materials
     b = 62.5e-6  # Radius of cladding in meters
     Lb_0 = 2e-3  # Unstressed beat length, 2 mm

     area = 8.5e-11

     S1 = np.zeros(npoints, dtype=complex)
     S2 = np.zeros(npoints, dtype=complex)
     Sdifference = np.zeros(npoints, dtype=complex)
     ExList = np.zeros(npoints, dtype=complex)
     EyList = np.zeros(npoints, dtype=complex)

     f = np.linspace(0, 100, npoints)  # Force in N/m (2D analysis)
     l = .018  # Interaction length, about 18 mm
     Ex_0 = calculate_Ex_0(3.42e-7)
     lambda_light = 1550e-9  # Wavelength of light in fiber
     k = 1/lambda_light

     alpha = np.pi/4 # angle between applied force and fast and slow axis of the fiber.
     beta = np.pi / 4  # Angle between polarized light and fast and slow axis of the fiber.
     delta = 1  # Extra phase from traveling through unstressed fiber
     gamma = np.pi/2# Angle of PM fiber wrt polarimeter. Should be 0 or pi/2
     eta = 376.730313 

     F = 2 * N**3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_light * np.pi * b * Y)  # Normalized force66
     print("NORMALIZED FORCE: ", F)
     phiVals = 0.5 * np.arctan((F * np.sin(2 * alpha)) / (1 + F * np.cos(2 * alpha)))  # Angle of rotated birefringence
     #    phiVals = np.linspace(0,, npoints)
     Lb = Lb_0 * (1 + F**2 + 2 * F * np.cos(2 * alpha))**(-1/2)  # Modified beat length
     #    print("PhiVals:", phiVals)
     print("LbVals: ", Lb)
     #    print("F", F)
     initialPowerDifference = 0
     finalPowerDifference = 0
     for li in range(npoints):
          A = ((np.cos(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta) * np.sin(gamma) * np.sin(phiVals[li])))
          B = ((-np.cos(gamma) * np.sin(phiVals[li])) + (np.exp(1j*delta) * np.sin(gamma) * np.cos(phiVals[li])))
          C = ((np.cos(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta) * np.sin(gamma) * np.sin(phiVals[li])))
          D = ((-np.cos(gamma) * np.sin(phiVals[li])) + (np.exp(1j*delta) * np.sin(gamma) * np.cos(phiVals[li])))
          E = ((-np.sin(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta) * np.cos(gamma) * np.sin(phiVals[li])))
          F = ((np.sin(gamma)*np.sin(phiVals[li])) + (np.exp(1j * delta)*np.cos(gamma)*np.cos(phiVals[li])))
          G = ((-np.sin(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta) * np.cos(gamma) * np.sin(phiVals[li])))
          H = ((np.sin(gamma)*np.sin(phiVals[li])) + (np.exp(1j * delta)*np.cos(gamma)*np.cos(phiVals[li])))
          
          I = (np.cos(phiVals[li]) * A) - (np.sin(phiVals[li]) * B)
          J = (np.sin(phiVals[li]) * C) - (np.cos(phiVals[li]) * D)
          K = (np.cos(phiVals[li] * E)) - (np.sin(phiVals[li]) * F)
          L = (np.sin(phiVals[li]) * G) - (np.cos(phiVals[li]) * H)

          print("THIS TERM IS: ", np.exp(-2j*k*l*((2*np.pi)/(k*Lb[li]))) * np.exp(-2j*k*N*l))
          Ex = (Ex_0**2) * np.exp(-2j*k*N*l)*np.exp(-2j*k*l*((2*np.pi)/(k*Lb[li]))) * (I*np.cos(beta) - J*np.sin(beta))
          Ey = (Ex_0**2) * np.exp(-2j*k*N*l)*np.exp(-2j*k*l*((2*np.pi)/(k*Lb[li]))) * (K*np.cos(beta) - L*np.sin(beta))

          

          # print("Ex: ", Ex)
          # print("Ey: ", Ey)
          #Why am I doing conjugate here??
          # ExConj = np.conjugate(Ex)
          # EyConj = np.conjugate(Ey)

          # Compute power
          Ex2= np.abs(Ex)**2  # Equivalent to |Ex|^2
          Ey2= np.abs(Ey)**2 #Equivalent to |Ey|^2
          # print("Ex2: ", Ex2)
          # print("Ey2: ", Ey2)
          eta = 376.73  # Characteristic impedance of free space (ohms)

          S1[li] = Ex2/(2*eta) * area
          S2[li] = Ey2/(2*eta) * area
          
          # S1[li] = np.real(S1[li])
          # S2[li] = np.real(S2[li])

          
          Sdifference[li] = S2[li] - S1[li]
          
          if (li == 0):

               initialPowerDifference = Sdifference[li]

          if(li == npoints - 1):
               finalPowerDifference = Sdifference[li]
               print("FIN: ", finalPowerDifference)

          ExList[li] = Ex
          EyList[li] = Ey


     print("S1: ", S1) 
     print("S2: ", S2)
     print("Sdifference: ", Sdifference)
     #    print(ExList)
     #    print(EyList) 
     plt.figure()
     plt.plot(f, S1, label='S1')
     plt.plot(f, S2, label='S2')
     plt.xlabel('Force (N/m)')
     plt.ylabel('S1, S2 (Real part)')
     plt.title('S1 and S2 vs. Force')
     plt.legend()
     plt.grid(True)
     plt.show()


     # Second Figure: Plot just the difference
     plt.figure()
     plt.plot(f, Sdifference, label='Difference (S2 - S1)', color='red')
     plt.xlabel('Force (N/m)')
     plt.ylabel('Difference (Real part)')
     plt.title('Difference (S1 - S2) vs. Force')
     plt.legend()
     plt.grid(True)

     plt.show()
     fmodel = generate_function(f, Sdifference)
     print("F::::: ", fmodel(30))
     print("VALUE: ", finalPowerDifference - initialPowerDifference)
     return (finalPowerDifference-initialPowerDifference)
        

import numpy as np

def calculate_Ex_0(P_in, MFD=10.5e-6, n=1.46, epsilon0=8.85e-12, c=3e8):
    """
    Calculate the peak electric field amplitude E_x0 (in V/m) for a given input power.

    Parameters:
      P_in      : Input power in Watts.
      MFD       : Mode Field Diameter of the fiber (in meters). Default is 10.5e-6 m.
      n         : Effective refractive index of the fiber mode. Default is 1.46.
      epsilon0  : Permittivity of free space (F/m). Default is 8.85e-12.
      c         : Speed of light in vacuum (m/s). Default is 3e8.

    Returns:
      E_x0      : Peak electric field amplitude in V/m.

    The formula used is:

      E_x0 = sqrt( 2 * P_in / [ n * epsilon0 * c * π * (MFD/2)^2 ] )
    """
    A_eff = np.pi * (MFD / 2)**2
    E_x0 = np.sqrt((2 * P_in) / (n * epsilon0 * c * A_eff))
    return E_x0

def generate_function(f, pDiff):
     m, b = np.polyfit(f, pDiff, 1)
     fmodel = lambda F_in: m*F_in + b  
     return fmodel

def generate_function(f, pDiff):
     # fit a line: pDiff = m * f + b
     m, b = np.polyfit(f, pDiff, 1)
    
    # invert it: f = (pDiff - b) / m
     force_from_pDiff = lambda p: (p - b) / m
     return force_from_pDiff


# force_from pdiff gives us force, force divided by l is stress, strain is finalPos - initialPos
# need to have queue for power difference -> 

# def returnStressFromPowerDiff(powerDiff):
     
# NEED: power diff, micrometer position. Feed power diff into function, get force, 


# needs to tell you:
# 1. How much you need to turn the fiber to maximize the amount of power difference for that force. (A way to reliably find alpha in the testing setup)
# 2. How much force you are applying based on the power difference from the data you take
# 
def test_ex1():
     print("make a function that goes from 0-90 deg and finds max change in power dif....")

     # NEW IDEA!!! TO TEST THE CALIBRATION CODE MORE COMPLETELY, WE 

     #TWO THINGS: 
     # 1. FOR TESTING:
          # make a function that tells you
     

     #we are looking at distance on the micrometer and force on the calibration curve !!!!!

     # 1. Checks the avg. change in power difference normalized for the data we just took.
     # 2. Checks the database of normalized power changes for the closest match
     # 3. Tells user what that angle is and how far they need to turn it to get to the best angle.
     n = 50
     alpha = np.linspace(0, 2*np.pi, n)
     deltaPowerDifferences = np.zeros(n) #might need dtype
     for i in range(0,n):
          deltaPowerDifferences[i] = ex1(alpha[i])

     deltaPowerDifferencesNormalized = np.zeros(n)

     for i in range(0,n):
          deltaPowerDifferencesNormalized[i] = (deltaPowerDifferences[i] - (-1e-5)) / (2e-5) 
     
     print("DELTA POWER DIFFERENCES:", deltaPowerDifferences)
     print("Normalized Delta power differences: ", deltaPowerDifferencesNormalized)

     plt.figure()
     plt.plot(alpha, deltaPowerDifferencesNormalized, label='change in power difference ')
     plt.xlabel('alpha (angle of force with respect to fast and slow axes)')
     plt.ylabel('change in power difference')
     plt.title('Change in power difference')
     plt.legend()
     plt.grid(True)
     plt.show()


     plt.figure()
     plt.plot(alpha, deltaPowerDifferences, label='change in power difference ')
     plt.xlabel('alpha (angle of force with respect to fast and slow axes)')
     plt.ylabel('change in power difference')
     plt.title('Change in power difference')
     plt.legend()
     plt.grid(True)
     plt.show()



     


            
npoints = 500
c = Calibration(npoints, np.linspace(0, 100, npoints), .018, 3.42e-7)
# c.varyLength(np.linspace(0, .18, 100))
initialHeight = 7
finalHeight = 5.2
c.calculatePowers(initialHeight, finalHeight)
# test_ex1()
c.plotPowerDifferences()
# c.plotPowers()
# c.plotPowersSeperately()
c.plotPowerDifferencesNormalized()
c.plotNormalizedPowers()
c.plotStressStrain()


func = c.generate_function_powerdiff_to_force()

print("FUNC(1.5e-12): ", func(1.5e-12))
print("FUNC(10): ", func(10))

print("Initial Power 1 Normalized: ", c.initialPower1)
print("Initial Power 2 Normalized: ", c.initialPower2)
print("Final Power 1 Normalized: ", c.finalPower1)
print("Final Power 2 Normalized: ", c.finalPower2)