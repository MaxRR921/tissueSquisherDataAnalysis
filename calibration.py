import numpy as np
import matplotlib.pyplot as plt



# function to back calculate beta given S1, S2, 
def calculate_beta(E_x, E_y):
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

     force_vals = 2 * N**3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_light * np.pi * b * Y)  # Normalized force66
     phiVals = 0.5 * np.arctan((force_vals * np.sin(2 * alpha)) / (1 + force_vals * np.cos(2 * alpha)))  # Angle of rotated birefringence
     Lb = Lb_0 * (1 + force_vals**2 + 2 * force_vals * np.cos(2 * alpha))**(-1/2)  # Modified beat length
     print("PhiVals:", phiVals)
     print("LbVals: ", Lb)
     print("F", force_vals)
     
     beta_vals = np.zeros(npoints, dtype=complex)
    

     for li in range(npoints):
          A = (np.cos(phiVals[li]) * (np.exp(-1j*k*N_s*l[li])*((np.cos(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta)*np.sin(gamma)*np.sin(phiVals[li]))))) - (np.sin(phiVals[li])*(np.exp(-1j*k*N_f*l[li])*((-np.cos(gamma)*np.sin(phiVals[li]))+(np.exp(1j*delta)*np.sin(gamma)*np.cos(phiVals[li])))))
          B = (np.sin(phiVals[li]) * (np.exp(-1j*k*N_s*l[li])*((np.cos(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta)*np.sin(gamma)*np.sin(phiVals[li]))))) + (np.cos(phiVals[li])*(np.exp(-1j*k*N_f*l[li])*((-np.cos(gamma)*np.sin(phiVals[li]))+(np.exp(1j*delta)*np.sin(gamma)*np.cos(phiVals[li])))))
          C = (np.cos(phiVals[li]) * (np.exp(-1j*k*N_s*l[li])*((-np.sin(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta)*np.cos(gamma)*np.sin(phiVals[li]))))) - (np.sin(phiVals[li])*(np.exp(-1j*k*N_f*l[li])*((np.sin(gamma)*np.sin(phiVals[li]))+(np.exp(1j*delta)*np.cos(gamma)*np.cos(phiVals[li])))))
          D = (np.sin(phiVals[li]) * (np.exp(-1j*k*N_s*l[li])*((-np.sin(gamma)*np.cos(phiVals[li])) + (np.exp(1j*delta)*np.cos(gamma)*np.sin(phiVals[li]))))) + (np.cos(phiVals[li])*(np.exp(-1j*k*N_f*l[li])*((np.sin(gamma)*np.sin(phiVals[li]))+(np.exp(1j*delta)*np.cos(gamma)*np.cos(phiVals[li])))))

          M = np.array([[A, B],
                        [C, D]], dtype=complex)
          # print("M SHAPE: ", M.shape)
          Minv = np.linalg.inv(M)
          print("LI:", li)
          EXEY = np.array([[E_x[li]],
                           [E_y[li]]], dtype=complex)
          
          AB = Minv @ EXEY
          Ab = AB[0][0]
          Bb = AB[1][0] 
          print("RESULT: ", np.arctan(Bb/Ab).real)
          print("A is: ", AB[0][0])
          print("B is: ", AB[1][0])
          print("AB IS: ", AB) 
          print("M INVERSE:",Minv)
          beta_vals[li] = np.arctan(Bb/Ab)
          

     print("BETA VALS: ", beta_vals.real)
     print("BETA AVG: ", np.average(beta_vals.real))

     plt.figure()
     plt.plot(f, beta_vals, label='beta')
     plt.xlabel('Force (N/m)')
     plt.ylabel('beta')
     plt.title('force vs. beta')
     plt.legend()
     plt.grid(True)
     plt.show()

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

        alpha = np.pi/4 # angle between applied force and fast and slow axis of the fiber.
        beta = np.pi / 6  # Angle between polarized light and fast and slow axis of the fiber.
        delta = 1  # Extra phase from traveling through unstressed fiber
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


       # Second Figure: Plot just the difference
     #    plt.figure()
     #    plt.plot(f, Sdifference, label='Difference (S2 - S1)', color='red')
     #    plt.xlabel('Force (N/m)')
     #    plt.ylabel('Difference (Real part)')
     #    plt.title('Difference (S1 - S2) vs. Force')
     #    plt.legend()
     #    plt.grid(True)

     #    plt.show()
     #    print("VALUE: ", finalPowerDifference - initialPowerDifference)
        return ExList, EyList
        


              
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

def test_calculate_beta():
     Ex, Ey = ex1(np.pi/4)

     calculate_beta(Ex, Ey)




     

# test_calculate_beta()
            
            
test_ex1()
# ex1(np.pi/6)





