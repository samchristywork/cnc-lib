class GCodeGenerator:
    def __init__(self):
        self.commands = []
        self.current_position = {'x': 0, 'y': 0, 'z': 0}
        self.path_history = []

    def add_comment(self, text):
        """
        Add a standalone comment line.

        Args:
            text: Comment text to add
        """
        if text:
            self.commands.append(f"; {text}")
        else:
            self.commands.append("")

    def set_units_metric(self):
        self.commands.append("G21 ; Set units to millimeters")

    def set_units_imperial(self):
        self.commands.append("G20 ; Set units to inches")

    def set_absolute_positioning(self):
        self.commands.append("G90 ; Set absolute positioning mode")

    def set_relative_positioning(self):
        self.commands.append("G91 ; Set relative positioning mode")

    def home_all_axes(self):
        self.commands.append("$H ; Home all axes")

    def rapid_move(self, x=None, y=None, z=None):
        """
        Rapid positioning move (G0).

        Args:
            x: X coordinate (optional)
            y: Y coordinate (optional)
            z: Z coordinate (optional)
        """
        coords = []
        comment_parts = []
        start_pos = dict(self.current_position)

        if x is not None:
            coords.append(f"X{x:.4f}")
            comment_parts.append(f"X={x:.4f}")
            self.current_position['x'] = x

        if y is not None:
            coords.append(f"Y{y:.4f}")
            comment_parts.append(f"Y={y:.4f}")
            self.current_position['y'] = y

        if z is not None:
            coords.append(f"Z{z:.4f}")
            comment_parts.append(f"Z={z:.4f}")
            self.current_position['z'] = z

        if coords:
            coord_str = " ".join(coords)
            comment = f"Rapid move to {', '.join(comment_parts)}"
            self.commands.append(f"G0 {coord_str} ; {comment}")
            self.path_history.append({
                'type': 'rapid',
                'start': start_pos,
                'end': dict(self.current_position)
            })

    def linear_move(self, x=None, y=None, z=None, feed_rate=None):
        """
        Linear interpolation move (G1).

        Args:
            x: X coordinate (optional)
            y: Y coordinate (optional)
            z: Z coordinate (optional)
            feed_rate: Feed rate in units per minute (optional)
        """
        coords = []
        comment_parts = []
        start_pos = dict(self.current_position)

        if x is not None:
            coords.append(f"X{x:.4f}")
            comment_parts.append(f"X={x:.4f}")
            self.current_position['x'] = x

        if y is not None:
            coords.append(f"Y{y:.4f}")
            comment_parts.append(f"Y={y:.4f}")
            self.current_position['y'] = y

        if z is not None:
            coords.append(f"Z{z:.4f}")
            comment_parts.append(f"Z={z:.4f}")
            self.current_position['z'] = z

        if feed_rate is not None:
            coords.append(f"F{feed_rate:.2f}")
            comment_parts.append(f"feed={feed_rate:.2f}")

        if coords:
            coord_str = " ".join(coords)
            comment = f"Linear move to {', '.join(comment_parts)}"
            self.commands.append(f"G1 {coord_str} ; {comment}")
            self.path_history.append({
                'type': 'linear',
                'start': start_pos,
                'end': dict(self.current_position)
            })
