import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class AngleFinder:
    def __init__(self, separation=np.pi / 9):
        self.sin_func = None
        self.optimalAlpha = 0
        self.y_values = None
        self.x_values = [-separation, -separation+np.pi/18, 0, separation - np.pi/18, separation]  # Initialize x-values

    def findAngle(self, y_values):
        for i in range(100):
            print("POWERS: ", y_values)
            
        self.y_values = y_values

        # Define the sine function with fixed frequency B = 2, 'sensitivity' with respect to alpha will always have this frequency
        def sine_func(x, A, C):
            return A * np.sin(2 * x + C)

        # Fit the sine function to the given points
        popt, _ = curve_fit(sine_func, self.x_values, y_values, p0=[1, 0])
        A, C = popt

        # Store the fitted sine function parameters
        self.sin_func = lambda x: sine_func(x, A, C)

        # Find all possible extrema by solving dy/dx = 0
        extrema_x_1 = (np.pi / 2 - C) / 2  # First extrema
        extrema_x_2 = (-np.pi / 2 - C) / 2  # Second extrema (opposite phase)

        # Convert the extrema to degrees
        extrema_deg_1 = np.degrees(extrema_x_1)
        extrema_deg_2 = np.degrees(extrema_x_2)

        # Check which extrema is within ±45° of 0°
        valid_extrema = []
        for extrema in [extrema_deg_1, extrema_deg_2]:
            if -45 <= extrema <= 45:
                valid_extrema.append(extrema)

        # Ensure there is at least one valid extrema within the range
        if not valid_extrema:
            raise ValueError("No extrema found within ±45° of 0°.")

        # Select the nearest extrema to 0°
        self.optimalAlpha = min(valid_extrema, key=abs)

        # Return the nearest valid extrema angle in degrees
        return self.optimalAlpha

    def plot(self):
        if self.sin_func is None or self.y_values is None:
            raise ValueError("You must call findAngle() before plotting.")

        # Generate points for plotting the fitted sine curve
        x_plot_rad = np.linspace(-np.pi / 2, np.pi / 2, 500)
        y_plot = self.sin_func(x_plot_rad)

        # Plot the points, fitted curve, and the vertical line at the extrema
        plt.figure(figsize=(10, 6))
        plt.scatter(self.x_values, self.y_values, color='red', label='Given Points')
        plt.plot(x_plot_rad, y_plot, label='Fitted Sine Curve', color='blue')
        plt.axvline(np.radians(self.optimalAlpha), color='green', linestyle='--', label=f'Extrema at {self.optimalAlpha:.2f}°')

        # Set axis limits to show the relevant section of the curve
        plt.xlim(-np.pi / 2, np.pi / 2)

        # Add labels and legend
        plt.title('Sine Function Fit and Nearest Extrema')
        plt.xlabel('Angle (radians)')
        plt.ylabel('y-value')
        plt.xticks([-np.pi / 2, -np.pi / 4, 0, np.pi / 4, np.pi / 2], ['-π/2', '-π/4', '0', 'π/4', 'π/2'])
        plt.legend()
        plt.grid(True)
        plt.show()


# # Example usage
# angle_finder = AngleFinder()
# y_values = [0.85, 0.35, -0.65]  # y-values at x = -separation, 0, separation
# angle_to_extrema = angle_finder.findAngle(y_values)
# print(f"Angle to nearest extrema: {angle_to_extrema:.2f} degrees")

# # Plotting the result
# angle_finder.plot()
