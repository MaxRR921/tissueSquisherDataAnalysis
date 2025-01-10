import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class AngleFinder:
    def __init__(self, alpha=np.pi/4, n=3):
        self.alpha = alpha
        self.n = n

    def findAngle(y_values):
        # Define the modified sine function
        def sine_func(x, A, B, C):
            return 0.5 * A * np.sin(B * x + C) + 0.5
    
        # x-values in degrees
        x_values = np.radians([-20, 0, 20])  # Convert degrees to radians
        
        # Fit the sine function to the given points
        popt, _ = curve_fit(sine_func, x_values, y_values, p0=[1, 1, 0])
        A, B, C = popt

        # Find the nearest extrema by solving dy/dx = 0
        # dy/dx = 0.5 * A * B * cos(Bx + C) = 0 when cos(Bx + C) = 0
        extrema_x = (np.pi / 2 - C) / B

        # Convert the extremum angle from radians to degrees
        extrema_angle_deg = np.degrees(extrema_x)

        # Return the nearest extrema angle in degrees
        return extrema_angle_deg


# Example usage
y_values = [0.815, 0.995, 0.940]  # Sample y-values at x = -20, 0, 20 degrees
angle_to_extrema = AngleFinder.findAngle(y_values)
print(f"Angle to nearest extrema: {angle_to_extrema:.2f} degrees")


# Plotting code directly at the bottom
# Define the modified sine function for plotting
def sine_func(x, A, B, C):
    return 0.5 * A * np.sin(B * x + C) + 0.5

# x-values in degrees
x_values_deg = np.array([-20, 0, 20])
x_values_rad = np.radians(x_values_deg)  # Convert degrees to radians

# Fit the sine function to the given points
popt, _ = curve_fit(sine_func, x_values_rad, y_values, p0=[1, 1, 0])

# Generate points for plotting the fitted sine curve
x_plot_deg = np.linspace(-30, 30, 500)
x_plot_rad = np.radians(x_plot_deg)
y_plot = sine_func(x_plot_rad, *popt)

# Plot the points, fitted curve, and the vertical line at the extrema
plt.figure(figsize=(10, 6))
plt.scatter(x_values_deg, y_values, color='red', label='Given Points')
plt.plot(x_plot_deg, y_plot, label='Fitted Sine Curve', color='blue')
plt.axvline(angle_to_extrema, color='green', linestyle='--', label=f'Extrema at {angle_to_extrema:.2f}°')

# Add labels and legend
plt.title('Sine Function Fit and Nearest Extrema')
plt.xlabel('Angle (degrees)')
plt.ylabel('y-value')
plt.legend()
plt.grid(True)
plt.show()
