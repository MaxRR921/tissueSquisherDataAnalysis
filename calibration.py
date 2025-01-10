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

        f = np.linspace(0, 9, npoints)  # Force in N/m (2D analysis)
        l = np.linspace(7.25, 20, npoints)  # Interaction length, about 18 mm
        Ex_0 = 1
        lambda_light = 1550e-9  # Wavelength of light in fiber
        k = 1/lambda_light

        alpha = np.pi / 4  # angle between applied force and fast and slow axis of the fiber.
        beta = np.pi / 6  # Angle between polarized light and fast and slow axis of the fiber.
        delta = 0  # Extra phase from traveling through unstressed fiber
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

        S1 = np.zeros(npoints, dtype=complex)
        S2 = np.zeros(npoints, dtype=complex)
        Sdifference = np.zeros(npoints, dtype=complex)
        ExList = np.zeros(npoints, dtype=complex)
        EyList = np.zeros(npoints, dtype=complex)

        f = np.linspace(0, 90, npoints)  # Force in N/m (2D analysis)
        l = np.linspace(7.25, 20, npoints)  # Interaction length, about 18 mm
        Ex_0 = 1
        lambda_light = 1550e-9  # Wavelength of light in fiber
        k = 1/lambda_light

        alpha = alphaVal # angle between applied force and fast and slow axis of the fiber.
        beta = np.pi / 6  # Angle between polarized light and fast and slow axis of the fiber.
        delta = 0  # Extra phase from traveling through unstressed fiber
        gamma = np.pi/2# Angle of PM fiber wrt polarimeter. Should be 0 or pi/2
        eta = 376.730313 

        F = 2 * N**3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_light * np.pi * b * Y)  # Normalized force66
        phiVals = 0.5 * np.arctan((F * np.sin(2 * alpha)) / (1 + F * np.cos(2 * alpha)))  # Angle of rotated birefringence
        Lb = Lb_0 * (1 + F**2 + 2 * F * np.cos(2 * alpha))**(-1/2)  # Modified beat length
     #    print("PhiVals:", phiVals)
     #    print("LbVals: ", Lb)
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

               Ex = Ex_0*np.exp(-2j*k*N*l[li])*np.exp(-2j*k*l[li]*((2*np.pi)/(k*Lb[li]))) * (I*np.cos(beta) - J*np.sin(beta))
               Ey = Ex_0*np.exp(-2j*k*N*l[li])*np.exp(-2j*k*l[li]*((2*np.pi)/(k*Lb[li]))) * (K*np.cos(beta) - L*np.sin(beta))

               

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

               S1[li] = Ex2/(2*eta)
               S2[li] = Ey2/(2*eta)

               
               Sdifference[li] = S2[li] - S1[li]
               
               if (li == 0):
                      initialPowerDifference = Sdifference[li]
                      print("INIT: ", initialPowerDifference)

               if(li == npoints - 1):
                      finalPowerDifference = Sdifference[li]
                      print("FIN: ", finalPowerDifference)

               ExList[li] = Ex
               EyList[li] = Ey


     #    print("S1: ", S1) 
     #    print("S2: ", S2)
     #    print("Sdifference: ", Sdifference)
     #    print(ExList)
     #    print(EyList) 
     #    plt.figure()
     #    plt.plot(f, S1, label='S1')
     #    plt.plot(f, S2, label='S2')
     #    plt.xlabel('Force (N/m)')
     #    plt.ylabel('S1, S2 (Real part)')
     #    plt.title('S1 and S2 vs. Force')
     #    plt.legend()
     #    plt.grid(True)
     #    plt.show()


     #    # Second Figure: Plot just the difference
     #    plt.figure()
     #    plt.plot(f, Sdifference, label='Difference (S2 - S1)', color='red')
     #    plt.xlabel('Force (N/m)')
     #    plt.ylabel('Difference (Real part)')
     #    plt.title('Difference (S1 - S2) vs. Force')
     #    plt.legend()
     #    plt.grid(True)

     #    plt.show()
        return (finalPowerDifference-initialPowerDifference)
        


              
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



     


            
            
test_ex1()






