
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (needed for 3-D)
from tkinter import Tk, filedialog


class PolarimeterCalibrator:




    def __init__(self, stokes1, stokes2, stokes3):

        """
        Converted one-for-one from the original MATLAB script
        “%theoretical circle trace: with polarizer”
        to pure-Python (NumPy + Matplotlib).
        """


        s1   = np.array(stokes1)
        s2   = np.array(stokes2) 
        s3   = np.array(stokes3)

        # ----------------------------------------------------------------------
        # 2) PRE-PROCESSING  (polar coordinates, theta unwrap, circle fit)
        # ----------------------------------------------------------------------
        sx    = np.sqrt(s1 * s1 + s2 * s2)
        theta = np.arctan2(s2, s1)
        psi   = np.arctan2(s3, sx)

        wrap = 0.0
        theta_ctr = np.zeros_like(theta)
        for i in range(len(theta) - 1):
            if np.sign(s1[i]) == -1:
                if  np.sign(s2[i]) ==  1 and np.sign(s2[i + 1]) == -1:
                    wrap += 2 * np.pi
                elif np.sign(s2[i]) == -1 and np.sign(s2[i + 1]) ==  1:
                    wrap -= 2 * np.pi
            theta_ctr[i + 1] = wrap
        theta += theta_ctr

        n   = len(theta)
        xx  = theta * theta
        yy  = psi   * psi
        xy  = theta * psi

        A = np.array([[np.sum(theta), np.sum(psi),  n],
                    [np.sum(xy),    np.sum(yy),   np.sum(psi)],
                    [np.sum(xx),    np.sum(xy),   np.sum(theta)]],
                    dtype=float)

        B = np.array([-np.sum(xx + yy),
                    -np.sum(xx * psi + yy * psi),
                    -np.sum(xx * theta + xy * psi)],
                    dtype=float)

        a  = np.linalg.solve(A, B)
        xc = -0.5 * a[0]
        yc = -0.5 * a[1]
        R  = np.sqrt((a[0] ** 2 + a[1] ** 2) / 4 - a[2])

        # ----------------------------------------------------------------------
        # 3) CONSTANTS  (identical names / values to the MATLAB)
        # ----------------------------------------------------------------------
        Y      = 7.3e10     # N m-2
        sigma  = 0.17
        Nidx   = 1.46
        p11    = 0.121
        p12    = 0.27
        p44    = (p11 - p12) / 2
        b      = 62.5e-6    # m
        Lb0    = 2e-3       # m
        lam    = 1550e-9     # m
        ℓ      = .03154   # m

        npts   = 1000
        alpha0 = 0.0
        β      = R / 2.0
        γ      = -xc / 2.0

        # helper shorthands (match MATLAB’s sin/ cos / exp)
        sin, cos, exp = np.sin, np.cos, np.exp
        j = 1j

        # ----------------------------------------------------------------------
        # 4) SOLVE δ (“delta”) – initial f = 0 branch
        # ----------------------------------------------------------------------
        δ_vec = np.linspace(0, 2 * np.pi, npts)
        f0    = 0.0

        F = 2 * (Nidx ** 3) * (1 + sigma) * (p12 - p11) * Lb0 * f0 / (lam * np.pi * b * Y)
        φ = 0.5 * np.arctan((F * sin(2 * alpha0)) / (1 + F * cos(2 * alpha0)))
        Lb = Lb0 * (1 + F ** 2 + 2 * F * cos(2 * alpha0)) ** (-0.5)
        arg = 2 * np.pi * ℓ / Lb

        # ––– giant explicit formulas (kept 1-to-1 with MATLAB) –––
        s1_fit = -np.abs(
            (sin(γ) * (exp(-arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            + exp(-δ_vec * j) * cos(γ) * (exp(-arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ)))
            * (sin(γ) * (exp(arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            + exp( δ_vec * j) * cos(γ) * (exp(arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ))))
        + np.abs(
            (cos(γ) * (exp(-arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            - exp(-δ_vec * j) * sin(γ) * (exp(-arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ)))
            * (cos(γ) * (exp(arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            - exp( δ_vec * j) * sin(γ) * (exp(arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ))))
        

        s2_fit = (
            2 * (cos(γ) * sin(δ_vec) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                + sin(arg) * sin(γ) * (cos(β) * sin(φ) ** 2
                + cos(φ) * sin(β) * sin(φ))
                + cos(δ_vec) * cos(γ) * sin(arg) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            * (sin(δ_vec) * sin(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                - cos(γ) * sin(arg) * (cos(β) * sin(φ) ** 2
                + cos(φ) * sin(β) * sin(φ))
                + cos(δ_vec) * sin(arg) * sin(γ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            - 2 * (sin(γ) * (cos(β) * cos(φ) ** 2 +
                cos(arg) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                - cos(φ) * sin(β) * sin(φ))
                + cos(δ_vec) * cos(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                - cos(γ) * sin(arg) * sin(δ_vec) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            * (cos(γ) * (cos(β) * cos(φ) ** 2 +
                cos(arg) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                - cos(φ) * sin(β) * sin(φ))
                - cos(δ_vec) * sin(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                + sin(arg) * sin(δ_vec) * sin(γ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
        )

        s3_fit = (cos(2 * φ) ** 2 * sin(2 * β) * sin(δ_vec)
                - sin(2 * β) * sin(δ_vec)
                - cos(2 * β) * sin(2 * φ) * cos(δ_vec) * sin(arg)
                - cos(2 * φ) * sin(2 * β) * cos(δ_vec) * sin(arg)
                - cos(2 * φ) ** 2 * sin(2 * β) * cos(arg) * sin(δ_vec)
                + cos(2 * β) * cos(2 * φ) * sin(2 * φ) * sin(δ_vec)
                - cos(2 * β) * cos(2 * φ) * sin(2 * φ) * cos(arg) * sin(δ_vec))

        # find δ giving the closest fit to the first experimental point
        err  = np.sqrt((s1_fit - s1[0]) ** 2 +
                    (s2_fit - s2[0]) ** 2 +
                    (s3_fit - s3[0]) ** 2)
        δ = δ_vec[np.argmin(err)]

        # ----------------------------------------------------------------------
        # 5) SOLVE α (“alpha”)  (second big loop, f = fMax)
        # ----------------------------------------------------------------------
        α_vec = np.linspace(0, np.pi, npts)
        fMax  = 455.875
        exp_i = len(s1) - 1           # MATLAB’s 1024th point

        F = 2 * (Nidx ** 3) * (1 + sigma) * (p12 - p11) * Lb0 * fMax / (lam * np.pi * b * Y)
        φ = 0.5 * np.arctan((F * sin(2 * α_vec)) / (1 + F * cos(2 * α_vec)))
        Lb = Lb0 * (1 + F ** 2 + 2 * F * cos(2 * α_vec)) ** (-0.5)
        arg = 2 * np.pi * ℓ / Lb

        # reuse giant expressions with α-vector-dependent φ / arg
        s1_fit = -np.abs(
            (sin(γ) * (exp(-arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            + exp(-δ * j) * cos(γ) * (exp(-arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ)))
            * (sin(γ) * (exp(arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            + exp( δ * j) * cos(γ) * (exp(arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ))))
        + np.abs(
            (cos(γ) * (exp(-arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            - exp(-δ * j) * sin(γ) * (exp(-arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ)))
            * (cos(γ) * (exp(arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            - exp( δ * j) * sin(γ) * (exp(arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ))))
        

        s2_fit = (
            2 * (cos(γ) * sin(δ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                + sin(arg) * sin(γ) * (cos(β) * sin(φ) ** 2
                + cos(φ) * sin(β) * sin(φ))
                + cos(δ) * cos(γ) * sin(arg) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            * (sin(δ) * sin(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                - cos(γ) * sin(arg) * (cos(β) * sin(φ) ** 2
                + cos(φ) * sin(β) * sin(φ))
                + cos(δ) * sin(arg) * sin(γ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            - 2 * (sin(γ) * (cos(β) * cos(φ) ** 2 +
                cos(arg) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                - cos(φ) * sin(β) * sin(φ))
                + cos(δ) * cos(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                - cos(γ) * sin(arg) * sin(δ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            * (cos(γ) * (cos(β) * cos(φ) ** 2 +
                cos(arg) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                - cos(φ) * sin(β) * sin(φ))
                - cos(δ) * sin(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                + sin(arg) * sin(δ) * sin(γ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
        )

        s3_fit = (cos(2 * φ) ** 2 * sin(2 * β) * sin(δ)
                - sin(2 * β) * sin(δ)
                - cos(2 * β) * sin(2 * φ) * cos(δ) * sin(arg)
                - cos(2 * φ) * sin(2 * β) * cos(δ) * sin(arg)
                - cos(2 * φ) ** 2 * sin(2 * β) * cos(arg) * sin(δ)
                + cos(2 * β) * cos(2 * φ) * sin(2 * φ) * sin(δ)
                - cos(2 * β) * cos(2 * φ) * sin(2 * φ) * cos(arg) * sin(δ))

        err = np.sqrt((s1_fit - s1[exp_i]) ** 2 +
                    (s2_fit - s2[exp_i]) ** 2 +
                    (s3_fit - s3[exp_i]) ** 2)
        α = α_vec[np.argmin(err)]

        print("ALPHA IS ", α )
        print("BETA IS: ", β)
        print("GAMMA IS: ", γ)
        # ----------------------------------------------------------------------
        # 6) FINAL THEORETICAL CURVE vs F (0 → fMax)
        # ----------------------------------------------------------------------
        f = np.linspace(0, fMax, npts)
        F = 2 * (Nidx ** 3) * (1 + sigma) * (p12 - p11) * Lb0 * f / (lam * np.pi * b * Y)
        φ = 0.5 * np.arctan((F * sin(2 * α)) / (1 + F * cos(2 * α)))
        Lb = Lb0 * (1 + F ** 2 + 2 * F * cos(2 * α)) ** (-0.5)
        arg = 2 * np.pi * ℓ / Lb

        s1_fit = -np.abs(
            (sin(γ) * (exp(-arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            + exp(-δ * j) * cos(γ) * (exp(-arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ)))
            * (sin(γ) * (exp(arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            + exp( δ * j) * cos(γ) * (exp(arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ))))
        + np.abs(
            (cos(γ) * (exp(-arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            - exp(-δ * j) * sin(γ) * (exp(-arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ)))
            * (cos(γ) * (exp(arg * j) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                    + cos(β) * cos(φ) ** 2 - cos(φ) * sin(β) * sin(φ))
            - exp( δ * j) * sin(γ) * (exp(arg * j) * (sin(β) * cos(φ) ** 2
                    + cos(β) * sin(φ) * cos(φ)) + sin(β) * sin(φ) ** 2
                    - cos(β) * cos(φ) * sin(φ))))
        

        s2_fit = (
            2 * (cos(γ) * sin(δ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                + sin(arg) * sin(γ) * (cos(β) * sin(φ) ** 2
                + cos(φ) * sin(β) * sin(φ))
                + cos(δ) * cos(γ) * sin(arg) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            * (sin(δ) * sin(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                - cos(γ) * sin(arg) * (cos(β) * sin(φ) ** 2
                + cos(φ) * sin(β) * sin(φ))
                + cos(δ) * sin(arg) * sin(γ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            - 2 * (sin(γ) * (cos(β) * cos(φ) ** 2 +
                cos(arg) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                - cos(φ) * sin(β) * sin(φ))
                + cos(δ) * cos(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                - cos(γ) * sin(arg) * sin(δ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
            * (cos(γ) * (cos(β) * cos(φ) ** 2 +
                cos(arg) * (cos(β) * sin(φ) ** 2 + cos(φ) * sin(β) * sin(φ))
                - cos(φ) * sin(β) * sin(φ))
                - cos(δ) * sin(γ) * (sin(β) * sin(φ) ** 2 +
                cos(arg) * (sin(β) * cos(φ) ** 2 + cos(β) * sin(φ) * cos(φ))
                - cos(β) * cos(φ) * sin(φ))
                + sin(arg) * sin(δ) * sin(γ) * (sin(β) * cos(φ) ** 2
                + cos(β) * sin(φ) * cos(φ)))
        )

        s3_fit = (cos(2 * φ) ** 2 * sin(2 * β) * sin(δ)
                - sin(2 * β) * sin(δ)
                - cos(2 * β) * sin(2 * φ) * cos(δ) * sin(arg)
                - cos(2 * φ) * sin(2 * β) * cos(δ) * sin(arg)
                - cos(2 * φ) ** 2 * sin(2 * β) * cos(arg) * sin(δ)
                + cos(2 * β) * cos(2 * φ) * sin(2 * φ) * sin(δ)
                - cos(2 * β) * cos(2 * φ) * sin(2 * φ) * cos(arg) * sin(δ))

        # ----------------------------------------------------------------------
        # 7) 3-D SCATTER + SPHERE
        # ----------------------------------------------------------------------
        fig1 = plt.figure()
        ax   = fig1.add_subplot(111, projection="3d")
        ax.scatter(s1, s2, s3,               label="Experimental")
        ax.scatter(s1_fit.real, s2_fit.real, s3_fit.real, label="Theoretical")

        u, v = np.mgrid[0:2*np.pi:40j, 0:np.pi:20j]
        xs, ys, zs = np.cos(u)*np.sin(v), np.sin(u)*np.sin(v), np.cos(v)
        ax.plot_wireframe(xs, ys, zs, color="lightgray", alpha=0.3)

        ax.set_box_aspect([1, 1, 1])
        ax.set_xlabel("s₁"); ax.set_ylabel("s₂"); ax.set_zlabel("s₃")
        ax.legend()

        # ----------------------------------------------------------------------
        # 8) FORCE vs PHASE
        # ----------------------------------------------------------------------
        x = s1_fit.real * sin(2 * γ) + s2_fit.real * cos(2 * γ)
        y = s3_fit.real
        phase = np.arctan2(y, x) / np.pi

        wrap = 0.0
        pctr = np.zeros_like(phase)
        for i in range(len(phase) - 1):
            if np.sign(x[i]) == -1:
                if  np.sign(y[i]) ==  1 and np.sign(y[i + 1]) == -1:
                    wrap += 2
                elif np.sign(y[i]) == -1 and np.sign(y[i + 1]) ==  1:
                    wrap -= 2
            pctr[i + 1] = wrap
        phase = phase + pctr - phase[0]

        fig2 = plt.figure()
        plt.plot(phase, f)
        plt.title("force vs. phase")
        plt.ylabel("force (N/m)")
        plt.xlabel("phase (π radians)")

        plt.show()


