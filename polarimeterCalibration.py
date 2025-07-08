import numpy as np
import matplotlib.pyplot as plt
import pandas as pd





class PolarimeterCalibrator:




    def __init__(self, stokes1, stokes2, stokes3):


        # Load CSV data
        s1 = np.array(stokes1)
        s2 = np.array(stokes2)
        s3 = np.array(stokes3)

        # Convert Stokes vector to polar coordinates
        sx = np.sqrt(s1 ** 2 + s2 ** 2)
        theta = np.arctan2(s2, s1)
        psi = np.arctan2(s3, sx)

        # Fix sudden sign-change jumps in theta
        wrap_count = 0
        theta_counter = np.zeros(len(theta))
        for i in range(len(theta) - 1):
            if np.sign(s1[i]) == -1:
                if np.sign(s2[i]) == 1 and np.sign(s2[i + 1]) == -1:
                    wrap_count += 2 * np.pi
                elif np.sign(s2[i]) == -1 and np.sign(s2[i + 1]) == 1:
                    wrap_count -= 2 * np.pi
            theta_counter[i + 1] = wrap_count
        theta += theta_counter

        # Circle fit
        xx = theta ** 2
        yy = psi ** 2
        xy = theta * psi
        n = len(theta)
        A = np.array([
            [np.sum(theta), np.sum(psi), n],
            [np.sum(xy), np.sum(yy), np.sum(psi)],
            [np.sum(xx), np.sum(xy), np.sum(theta)]
        ])
        B = -np.array([
            np.sum(xx + yy),
            np.sum(xx * psi + yy * psi),
            np.sum(xx * theta + xy * psi)
        ])
        a = np.linalg.solve(A, B)
        xc = -0.5 * a[0]
        yc = -0.5 * a[1]
        R = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2])

        # Material properties
        Y = 7.3e10
        sigma = 0.17
        N = 1.46
        p_11 = 0.121
        p_12 = 0.27
        b = 62.5e-6
        Lb_0 = 2e-3
        lambda_ = 980e-9
        l = 22.90e-3

        # Initial parameters
        npoints = 1000
        alpha = 0
        beta = R / 2
        gamma = -xc / 2
        delta = np.linspace(0, 2 * np.pi, npoints)
        f = 0

        # Theoretical fit: force and angles
        F = 2 * N ** 3 * (1 + sigma) * (p_12 - p_11) * Lb_0 * f / (lambda_ * np.pi * b * Y)
        phi = 0.5 * np.arctan2(F * np.sin(2 * alpha), 1 + F * np.cos(2 * alpha))
        Lb = Lb_0 / np.sqrt(1 + F ** 2 + 2 * F * np.cos(2 * alpha))
        arg = (2 * np.pi * l) / Lb

        # Fit equations
        E = np.exp
        j = 1j

        s1_fit = -np.abs((
            (np.sin(gamma) * (E(-arg * j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi))
                            + np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi))
            + E(-delta * j) * np.cos(gamma) * (E(-arg * j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi))
                                                + np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))
            * (np.sin(gamma) * (E(arg * j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi))
                                + np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi))
            + E(delta * j) * np.cos(gamma) * (E(arg * j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi))
                                                + np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))
        ) + np.abs((
            np.cos(gamma) * (E(-arg * j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi))
                            + np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi))
            - E(-delta * j) * np.sin(gamma) * (E(-arg * j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi))
                                            + np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))
            * (np.cos(gamma) * (E(arg * j) * (np.cos(beta) * np.sin(phi)**2 + np.cos(phi) * np.sin(beta) * np.sin(phi))
                                + np.cos(beta) * np.cos(phi)**2 - np.cos(phi) * np.sin(beta) * np.sin(phi))
            - E(delta * j) * np.sin(gamma) * (E(arg * j) * (np.sin(beta) * np.cos(phi)**2 + np.cos(beta) * np.sin(phi) * np.cos(phi))
                                                + np.sin(beta) * np.sin(phi)**2 - np.cos(beta) * np.cos(phi) * np.sin(phi)))
        ))

        # Remaining s2_fit and s3_fit equations are long—continue conversion if needed
        # Plotting result
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(s1, s2, s3, label="Experimental")
        ax.scatter(s1_fit.real, s2[:len(s1_fit)], s3[:len(s1_fit)], label="Theoretical")
        ax.set_xlabel('s1')
        ax.set_ylabel('s2')
        ax.set_zlabel('s3')
        ax.set_title('Stokes Parameters')
        ax.legend()
        plt.show()

