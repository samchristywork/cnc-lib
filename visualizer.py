#!/usr/bin/env python3

import re
import math
import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class GCodeParser:
    """Parses G-code and tracks machine state"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset parser state"""
        self.position = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'A': 0.0}
        self.absolute_mode = True  # G90 = absolute, G91 = relative
        self.units = 'mm'  # G21 = mm, G20 = inches
        self.feed_rate = 0
        self.spindle_speed = 0
        self.current_tool = 0
        self.paths = []  # List of path segments: (start, end, type, feed_rate)
        self.rapid_moves = []
        self.cut_moves = []
        self.arc_moves = []

    def parse_line(self, line):
        """Parse a single line of G-code"""
        # Remove comments
        line = re.sub(r';.*$', '', line)
        line = re.sub(r'\(.*?\)', '', line)
        line = line.strip().upper()

        if not line:
            return

        # Extract commands and parameters
        tokens = re.findall(r'[A-Z]-?\d*\.?\d*', line)

        params = {}
        commands = []

        for token in tokens:
            letter = token[0]
            value = token[1:] if len(token) > 1 else None

            if letter in ['G', 'M', 'T']:
                if value:
                    commands.append((letter, float(value) if '.' in value else int(value)))
            else:
                if value:
                    params[letter] = float(value)

        # Process commands
        for cmd_type, cmd_num in commands:
            if cmd_type == 'G':
                self.process_g_command(cmd_num, params)
            elif cmd_type == 'M':
                self.process_m_command(cmd_num, params)
            elif cmd_type == 'T':
                self.current_tool = cmd_num

        # Update feed rate if specified
        if 'F' in params:
            self.feed_rate = params['F']

    def process_g_command(self, cmd, params):
        """Process G commands"""
        # Motion commands
        if cmd in [0, 1, 2, 3]:
            self.process_motion(cmd, params)
        # Coordinate system
        elif cmd == 20:  # Inches
            self.units = 'inches'
        elif cmd == 21:  # Millimeters
            self.units = 'mm'
        elif cmd == 90:  # Absolute positioning
            self.absolute_mode = True
        elif cmd == 91:  # Relative positioning
            self.absolute_mode = False
        elif cmd == 92:  # Set position
            for axis in ['X', 'Y', 'Z', 'A']:
                if axis in params:
                    self.position[axis] = params[axis]

    def process_m_command(self, cmd, params):
        """Process M commands"""
        if cmd == 3:  # Spindle on CW
            self.spindle_speed = params.get('S', 1000)
        elif cmd == 4:  # Spindle on CCW
            self.spindle_speed = params.get('S', 1000)
        elif cmd == 5:  # Spindle off
            self.spindle_speed = 0

    def process_motion(self, motion_type, params):
        """Process motion commands (G0, G1, G2, G3)"""
        start_pos = self.position.copy()

        # Calculate end position
        end_pos = start_pos.copy()

        if self.absolute_mode:
            for axis in ['X', 'Y', 'Z', 'A']:
                if axis in params:
                    end_pos[axis] = params[axis]
        else:
            for axis in ['X', 'Y', 'Z', 'A']:
                if axis in params:
                    end_pos[axis] = start_pos[axis] + params[axis]

        # Store the move
        move_data = {
            'start': start_pos,
            'end': end_pos,
            'type': motion_type,
            'feed_rate': self.feed_rate
        }

        if motion_type == 0:  # Rapid move (G0)
            self.rapid_moves.append(move_data)
        elif motion_type == 1:  # Linear cutting move (G1)
            self.cut_moves.append(move_data)
        elif motion_type in [2, 3]:  # Arc moves (G2 = CW, G3 = CCW)
            # For arcs, we need I, J, K offsets or R radius
            move_data['i'] = params.get('I', 0.0)
            move_data['j'] = params.get('J', 0.0)
            move_data['k'] = params.get('K', 0.0)
            move_data['r'] = params.get('R', None)
            move_data['direction'] = 'CW' if motion_type == 2 else 'CCW'
            self.arc_moves.append(move_data)

        # Update current position
        self.position = end_pos

    def get_arc_points(self, move, num_points=20):
        """Generate points along an arc for visualization"""
        start = move['start']
        end = move['end']

        if move['r'] is not None:
            # Arc defined by radius
            # This is more complex - simplified implementation
            center_x = (start['X'] + end['X']) / 2
            center_y = (start['Y'] + end['Y']) / 2
        else:
            # Arc defined by I, J offsets from start point
            center_x = start['X'] + move['i']
            center_y = start['Y'] + move['j']

        # Calculate start and end angles
        start_angle = math.atan2(start['Y'] - center_y, start['X'] - center_x)
        end_angle = math.atan2(end['Y'] - center_y, end['X'] - center_x)

        # Calculate radius
        radius = math.sqrt((start['X'] - center_x)**2 + (start['Y'] - center_y)**2)

        # Determine sweep direction
        if move['direction'] == 'CW':
            if end_angle > start_angle:
                end_angle -= 2 * math.pi
        else:  # CCW
            if end_angle < start_angle:
                end_angle += 2 * math.pi

        # Generate points
        angles = np.linspace(start_angle, end_angle, num_points)
        x_points = center_x + radius * np.cos(angles)
        y_points = center_y + radius * np.sin(angles)
        z_points = np.linspace(start['Z'], end['Z'], num_points)

        return x_points, y_points, z_points


class GCodeVisualizer:
    """GUI for visualizing G-code toolpaths"""

    def __init__(self, root):
        self.root = root
        self.root.title("G-Code Visualizer")
        self.root.geometry("1200x800")

        self.parser = GCodeParser()
        self.current_file = None
        self.view_3d = False

        self.create_widgets()

    def create_widgets(self):
        """Create the GUI widgets"""
        # Top frame for controls
        control_frame = tk.Frame(self.root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # File controls
        tk.Button(control_frame, text="Load G-Code", command=self.load_file).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Reload", command=self.reload_file).pack(side=tk.LEFT, padx=2)
        tk.Button(control_frame, text="Clear", command=self.clear_plot).pack(side=tk.LEFT, padx=2)

        # View toggle
        tk.Label(control_frame, text="View:").pack(side=tk.LEFT, padx=(10, 2))
        self.view_var = tk.StringVar(value="2D")
        tk.Radiobutton(control_frame, text="2D (XY)", variable=self.view_var,
                      value="2D", command=self.update_plot).pack(side=tk.LEFT)
        tk.Radiobutton(control_frame, text="3D", variable=self.view_var,
                      value="3D", command=self.update_plot).pack(side=tk.LEFT)

        # Display options
        tk.Label(control_frame, text="Show:").pack(side=tk.LEFT, padx=(10, 2))
        self.show_rapid = tk.BooleanVar(value=True)
        self.show_cuts = tk.BooleanVar(value=True)
        self.show_arcs = tk.BooleanVar(value=True)
        tk.Checkbutton(control_frame, text="Rapid", variable=self.show_rapid,
                      command=self.update_plot).pack(side=tk.LEFT)
        tk.Checkbutton(control_frame, text="Cuts", variable=self.show_cuts,
                      command=self.update_plot).pack(side=tk.LEFT)
        tk.Checkbutton(control_frame, text="Arcs", variable=self.show_arcs,
                      command=self.update_plot).pack(side=tk.LEFT)

        # File info label
        self.file_label = tk.Label(control_frame, text="No file loaded", fg="gray")
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))

        # Main container for plot and info
        main_frame = tk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left side: Plot
        plot_frame = tk.Frame(main_frame)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_title('G-Code Toolpath Visualization')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')

        # Embed in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Add matplotlib toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, plot_frame)
        toolbar.update()

        # Right side: Info panel
        info_frame = tk.LabelFrame(main_frame, text="Information", padx=10, pady=10)
        info_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        self.info_text = tk.Text(info_frame, width=30, height=40, font=("Courier", 9))
        info_scroll = tk.Scrollbar(info_frame, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=info_scroll.set)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar at bottom
        self.status_label = tk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def load_file(self):
        """Load a G-code file"""
        filename = filedialog.askopenfilename(
            title="Select G-code file",
            filetypes=[("G-code files", "*.nc *.gcode"), ("All files", "*.*")]
        )

        if filename:
            self.current_file = filename
            self.reload_file()

    def reload_file(self):
        """Reload the current file"""
        if not self.current_file:
            return

        try:
            self.status_label.config(text=f"Loading {self.current_file}...")
            self.root.update()

            # Reset parser
            self.parser.reset()

            # Parse file
            with open(self.current_file, 'r') as f:
                lines = f.readlines()

            for line in lines:
                self.parser.parse_line(line)

            # Update display
            import os
            filename = os.path.basename(self.current_file)
            self.file_label.config(text=f"File: {filename}", fg="black")
            self.update_plot()
            self.update_info()
            self.status_label.config(text=f"Loaded {len(lines)} lines from {filename}")

        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}")
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Error loading file:\n{str(e)}")

    def clear_plot(self):
        """Clear the plot"""
        self.parser.reset()
        self.current_file = None
        self.file_label.config(text="No file loaded", fg="gray")
        self.update_plot()
        self.info_text.delete(1.0, tk.END)
        self.status_label.config(text="Cleared")

    def update_plot(self):
        """Update the visualization"""
        # Clear current plot
        self.fig.clear()

        # Create new axes based on view mode
        if self.view_var.get() == "3D":
            self.ax = self.fig.add_subplot(111, projection='3d')
            self.plot_3d()
        else:
            self.ax = self.fig.add_subplot(111)
            self.plot_2d()

        self.canvas.draw()

    def plot_2d(self):
        """Plot in 2D (X-Y plane)"""
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_title('G-Code Toolpath (2D View)')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')

        # Plot rapid moves
        if self.show_rapid.get() and self.parser.rapid_moves:
            for move in self.parser.rapid_moves:
                start = move['start']
                end = move['end']
                self.ax.plot([start['X'], end['X']],
                           [start['Y'], end['Y']],
                           'b--', linewidth=0.5, alpha=0.5, label='Rapid' if move == self.parser.rapid_moves[0] else "")

        # Plot cutting moves
        if self.show_cuts.get() and self.parser.cut_moves:
            for move in self.parser.cut_moves:
                start = move['start']
                end = move['end']
                self.ax.plot([start['X'], end['X']],
                           [start['Y'], end['Y']],
                           'r-', linewidth=1.5, label='Cut' if move == self.parser.cut_moves[0] else "")

        # Plot arc moves
        if self.show_arcs.get() and self.parser.arc_moves:
            for move in self.parser.arc_moves:
                x_points, y_points, _ = self.parser.get_arc_points(move)
                self.ax.plot(x_points, y_points,
                           'g-', linewidth=1.5, label='Arc' if move == self.parser.arc_moves[0] else "")

        # Mark start and end points
        if self.parser.rapid_moves or self.parser.cut_moves or self.parser.arc_moves:
            # Find first move
            all_moves = self.parser.rapid_moves + self.parser.cut_moves + self.parser.arc_moves
            if all_moves:
                start = all_moves[0]['start']
                end = self.parser.position

                self.ax.plot(start['X'], start['Y'], 'go', markersize=8, label='Start')
                self.ax.plot(end['X'], end['Y'], 'rs', markersize=8, label='End')

        # Add legend if there are moves
        if self.parser.rapid_moves or self.parser.cut_moves or self.parser.arc_moves:
            self.ax.legend(loc='upper right')

    def plot_3d(self):
        """Plot in 3D"""
        self.ax.set_xlabel('X (mm)')
        self.ax.set_ylabel('Y (mm)')
        self.ax.set_zlabel('Z (mm)')
        self.ax.set_title('G-Code Toolpath (3D View)')

        # Plot rapid moves
        if self.show_rapid.get() and self.parser.rapid_moves:
            for move in self.parser.rapid_moves:
                start = move['start']
                end = move['end']
                self.ax.plot([start['X'], end['X']],
                           [start['Y'], end['Y']],
                           [start['Z'], end['Z']],
                           'b--', linewidth=0.5, alpha=0.5, label='Rapid' if move == self.parser.rapid_moves[0] else "")

        # Plot cutting moves
        if self.show_cuts.get() and self.parser.cut_moves:
            for move in self.parser.cut_moves:
                start = move['start']
                end = move['end']
                self.ax.plot([start['X'], end['X']],
                           [start['Y'], end['Y']],
                           [start['Z'], end['Z']],
                           'r-', linewidth=1.5, label='Cut' if move == self.parser.cut_moves[0] else "")

        # Plot arc moves
        if self.show_arcs.get() and self.parser.arc_moves:
            for move in self.parser.arc_moves:
                x_points, y_points, z_points = self.parser.get_arc_points(move)
                self.ax.plot(x_points, y_points, z_points,
                           'g-', linewidth=1.5, label='Arc' if move == self.parser.arc_moves[0] else "")

        # Mark start and end points
        if self.parser.rapid_moves or self.parser.cut_moves or self.parser.arc_moves:
            all_moves = self.parser.rapid_moves + self.parser.cut_moves + self.parser.arc_moves
            if all_moves:
                start = all_moves[0]['start']
                end = self.parser.position

                self.ax.scatter(start['X'], start['Y'], start['Z'],
                              c='green', marker='o', s=100, label='Start')
                self.ax.scatter(end['X'], end['Y'], end['Z'],
                              c='red', marker='s', s=100, label='End')

        # Add legend if there are moves
        if self.parser.rapid_moves or self.parser.cut_moves or self.parser.arc_moves:
            self.ax.legend(loc='upper right')

    def update_info(self):
        """Update the information panel"""
        self.info_text.delete(1.0, tk.END)

        info = []
        info.append("=== File Statistics ===\n")
        info.append(f"Rapid moves: {len(self.parser.rapid_moves)}\n")
        info.append(f"Cut moves: {len(self.parser.cut_moves)}\n")
        info.append(f"Arc moves: {len(self.parser.arc_moves)}\n")
        info.append(f"Total moves: {len(self.parser.rapid_moves) + len(self.parser.cut_moves) + len(self.parser.arc_moves)}\n\n")

        info.append("=== Final State ===\n")
        info.append(f"Position:\n")
        info.append(f"  X: {self.parser.position['X']:.3f}\n")
        info.append(f"  Y: {self.parser.position['Y']:.3f}\n")
        info.append(f"  Z: {self.parser.position['Z']:.3f}\n")
        info.append(f"Mode: {'Absolute' if self.parser.absolute_mode else 'Relative'}\n")
        info.append(f"Units: {self.parser.units}\n")
        info.append(f"Feed rate: {self.parser.feed_rate}\n\n")

        # Calculate bounding box
        if self.parser.rapid_moves or self.parser.cut_moves or self.parser.arc_moves:
            all_moves = self.parser.rapid_moves + self.parser.cut_moves + self.parser.arc_moves

            x_coords = []
            y_coords = []
            z_coords = []

            for move in all_moves:
                x_coords.extend([move['start']['X'], move['end']['X']])
                y_coords.extend([move['start']['Y'], move['end']['Y']])
                z_coords.extend([move['start']['Z'], move['end']['Z']])

            info.append("=== Bounding Box ===\n")
            info.append(f"X: {min(x_coords):.3f} to {max(x_coords):.3f} ({max(x_coords)-min(x_coords):.3f})\n")
            info.append(f"Y: {min(y_coords):.3f} to {max(y_coords):.3f} ({max(y_coords)-min(y_coords):.3f})\n")
            info.append(f"Z: {min(z_coords):.3f} to {max(z_coords):.3f} ({max(z_coords)-min(z_coords):.3f})\n\n")

            # Calculate total distance
            total_rapid = sum(
                math.sqrt((m['end']['X']-m['start']['X'])**2 +
                         (m['end']['Y']-m['start']['Y'])**2 +
                         (m['end']['Z']-m['start']['Z'])**2)
                for m in self.parser.rapid_moves
            )

            total_cut = sum(
                math.sqrt((m['end']['X']-m['start']['X'])**2 +
                         (m['end']['Y']-m['start']['Y'])**2 +
                         (m['end']['Z']-m['start']['Z'])**2)
                for m in self.parser.cut_moves
            )

            info.append("=== Distances ===\n")
            info.append(f"Rapid: {total_rapid:.3f} mm\n")
            info.append(f"Cutting: {total_cut:.3f} mm\n")
            info.append(f"Total: {total_rapid + total_cut:.3f} mm\n")

        self.info_text.insert(tk.END, ''.join(info))


def main():
    root = tk.Tk()
    app = GCodeVisualizer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
