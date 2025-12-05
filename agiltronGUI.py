import tkinter as tk
from tkinter import ttk, scrolledtext
import sys
from io import StringIO
from agiltronController import agiltronController
import threading


class ConsoleRedirector:
    """Redirects console output to the GUI text widget."""

    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class AgiltronGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Agiltron Controller GUI")
        self.root.geometry("800x600")

        # Initialize controller
        self.controller = agiltronController()
        self.connected = False

        # Setup UI
        self.setup_ui()

        # Redirect console output to GUI
        self.console_redirector = ConsoleRedirector(self.console_text)
        sys.stdout = self.console_redirector
        sys.stderr = self.console_redirector

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Connection section
        connection_frame = ttk.LabelFrame(main_frame, text="Connection", padding="10")
        connection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        connection_frame.columnconfigure(1, weight=1)

        self.connect_btn = ttk.Button(
            connection_frame, text="Connect", command=self.connect_controller
        )
        self.connect_btn.grid(row=0, column=0, padx=(0, 5))

        self.disconnect_btn = ttk.Button(
            connection_frame,
            text="Disconnect",
            command=self.disconnect_controller,
            state="disabled",
        )
        self.disconnect_btn.grid(row=0, column=1, padx=5)

        self.status_label = ttk.Label(
            connection_frame, text="Status: Disconnected", foreground="red"
        )
        self.status_label.grid(row=0, column=2, padx=(5, 0))

        # Control section
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)

        # Position input
        ttk.Label(control_frame, text="Position (0-50):").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )

        self.pos_var = tk.StringVar(value="0")
        self.pos_spinbox = ttk.Spinbox(
            control_frame, from_=0, to=50, textvariable=self.pos_var, width=10
        )
        self.pos_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(5, 0), pady=5)

        # Position slider
        self.pos_slider = ttk.Scale(
            control_frame,
            from_=0,
            to=50,
            orient=tk.HORIZONTAL,
            variable=self.pos_var,
            command=lambda v: self.pos_var.set(f"{int(float(v))}"),
        )
        self.pos_slider.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Set position button
        self.set_pos_btn = ttk.Button(
            control_frame,
            text="Set Position",
            command=self.set_position,
            state="disabled",
        )
        self.set_pos_btn.grid(row=2, column=0, columnspan=2, pady=5)

        # Get position button
        self.get_pos_btn = ttk.Button(
            control_frame,
            text="Get Current Position",
            command=self.get_position,
            state="disabled",
        )
        self.get_pos_btn.grid(row=3, column=0, columnspan=2, pady=5)

        # Separator
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10
        )

        # Max Velocity input
        ttk.Label(control_frame, text="Max Velocity:").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )

        self.vel_var = tk.StringVar(value="0")
        self.vel_spinbox = ttk.Spinbox(
            control_frame, from_=0, to=4294967295, textvariable=self.vel_var, width=10
        )
        self.vel_spinbox.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=5)

        # Max Velocity slider (scaled for easier interaction)
        self.vel_slider = ttk.Scale(
            control_frame,
            from_=0,
            to=1000000,
            orient=tk.HORIZONTAL,
            variable=self.vel_var,
            command=lambda v: self.vel_var.set(f"{int(float(v))}"),
        )
        self.vel_slider.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # Set max velocity button
        self.set_vel_btn = ttk.Button(
            control_frame,
            text="Set Max Velocity",
            command=self.set_velocity,
            state="disabled",
        )
        self.set_vel_btn.grid(row=7, column=0, columnspan=2, pady=5)

        # Get max velocity button
        self.get_vel_btn = ttk.Button(
            control_frame,
            text="Get Max Velocity",
            command=self.get_velocity,
            state="disabled",
        )
        self.get_vel_btn.grid(row=8, column=0, columnspan=2, pady=5)

        # Console section
        console_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="10")
        console_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)

        # Console text area with scrollbar
        self.console_text = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            height=15,
            state="normal",
            bg="black",
            fg="#ffffff",
            font=("JetBrainsMono Nerd Font", 10),
        )
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Clear console button
        clear_btn = ttk.Button(
            console_frame, text="Clear Console", command=self.clear_console
        )
        clear_btn.grid(row=1, column=0, pady=(5, 0))

    def connect_controller(self):
        """Connect to the Agiltron controller."""

        def connect_thread():
            print("Attempting to connect to controller...")
            if self.controller.start():
                self.connected = True
                self.root.after(0, self.update_connection_status, True)
                print("Successfully connected to controller!")
            else:
                self.connected = False
                self.root.after(0, self.update_connection_status, False)
                print("Failed to connect to controller.")

        # Run connection in separate thread to prevent GUI freezing
        thread = threading.Thread(target=connect_thread, daemon=True)
        thread.start()

    def disconnect_controller(self):
        """Disconnect from the controller."""
        self.controller.closePort()
        self.connected = False
        self.update_connection_status(False)
        print("Disconnected from controller.")

    def update_connection_status(self, connected):
        """Update the GUI based on connection status."""
        if connected:
            self.status_label.config(text="Status: Connected", foreground="green")
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.set_pos_btn.config(state="normal")
            self.get_pos_btn.config(state="normal")
            self.set_vel_btn.config(state="normal")
            self.get_vel_btn.config(state="normal")
        else:
            self.status_label.config(text="Status: Disconnected", foreground="red")
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.set_pos_btn.config(state="disabled")
            self.get_pos_btn.config(state="disabled")
            self.set_vel_btn.config(state="disabled")
            self.get_vel_btn.config(state="disabled")

    def set_position(self):
        """Set the position on the controller."""
        try:
            pos = int(self.pos_var.get())
            if 0 <= pos <= 50:
                # Scale input pos to 0-700000
                scaled_pos = self.controller.scale_int(pos)
                bits_to_send = self.controller.pos_to_bytes(scaled_pos)
                self.controller.send_bits(bits_to_send)
            else:
                print("Error: Position must be between 0 and 50")
        except ValueError:
            print("Error: Invalid position value")

    def get_position(self):
        """Get the current position from the controller."""
        if self.connected:
            self.controller.getCurrentPos()
        else:
            print("Error: Not connected to controller")

    def set_velocity(self):
        """Set the max velocity on the controller."""
        try:
            velocity = int(self.vel_var.get())
            if 0 <= velocity <= 4294967295:
                self.controller.setMaxVelocity(velocity)
            else:
                print("Error: Velocity must be between 0 and 4294967295")
        except ValueError:
            print("Error: Invalid velocity value")

    def get_velocity(self):
        """Get the max velocity from the controller."""
        if self.connected:
            self.controller.checkMaxVelocity()
        else:
            print("Error: Not connected to controller")

    def clear_console(self):
        """Clear the console output."""
        self.console_text.delete(1.0, tk.END)

    def on_closing(self):
        """Handle window closing."""
        if self.connected:
            self.controller.closePort()
        # Restore stdout and stderr
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.root.destroy()


def main():
    root = tk.Tk()
    app = AgiltronGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
