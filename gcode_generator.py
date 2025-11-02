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

    def arc_cw(self, x=None, y=None, z=None, i=None, j=None, k=None, feed_rate=None):
        """
        Clockwise arc move (G2).

        Args:
            x: X coordinate of arc endpoint (optional)
            y: Y coordinate of arc endpoint (optional)
            z: Z coordinate of arc endpoint (optional)
            i: X offset from current position to arc center (optional)
            j: Y offset from current position to arc center (optional)
            k: Z offset from current position to arc center (optional)
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

        if i is not None:
            coords.append(f"I{i:.4f}")
            comment_parts.append(f"I={i:.4f}")

        if j is not None:
            coords.append(f"J{j:.4f}")
            comment_parts.append(f"J={j:.4f}")

        if k is not None:
            coords.append(f"K{k:.4f}")
            comment_parts.append(f"K={k:.4f}")

        if feed_rate is not None:
            coords.append(f"F{feed_rate:.2f}")
            comment_parts.append(f"feed={feed_rate:.2f}")

        if coords:
            coord_str = " ".join(coords)
            comment = f"Clockwise arc to {', '.join(comment_parts)}"
            self.commands.append(f"G2 {coord_str} ; {comment}")
            self.path_history.append({
                'type': 'arc_cw',
                'start': start_pos,
                'end': dict(self.current_position),
                'center_offset': {'i': i or 0, 'j': j or 0, 'k': k or 0}
            })

    def arc_ccw(self, x=None, y=None, z=None, i=None, j=None, k=None, feed_rate=None):
        """
        Counter-clockwise arc move (G3).

        Args:
            x: X coordinate of arc endpoint (optional)
            y: Y coordinate of arc endpoint (optional)
            z: Z coordinate of arc endpoint (optional)
            i: X offset from current position to arc center (optional)
            j: Y offset from current position to arc center (optional)
            k: Z offset from current position to arc center (optional)
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

        if i is not None:
            coords.append(f"I{i:.4f}")
            comment_parts.append(f"I={i:.4f}")

        if j is not None:
            coords.append(f"J{j:.4f}")
            comment_parts.append(f"J={j:.4f}")

        if k is not None:
            coords.append(f"K{k:.4f}")
            comment_parts.append(f"K={k:.4f}")

        if feed_rate is not None:
            coords.append(f"F{feed_rate:.2f}")
            comment_parts.append(f"feed={feed_rate:.2f}")

        if coords:
            coord_str = " ".join(coords)
            comment = f"Counter-clockwise arc to {', '.join(comment_parts)}"
            self.commands.append(f"G3 {coord_str} ; {comment}")
            self.path_history.append({
                'type': 'arc_ccw',
                'start': start_pos,
                'end': dict(self.current_position),
                'center_offset': {'i': i or 0, 'j': j or 0, 'k': k or 0}
            })

    def spindle_on_cw(self, rpm=None):
        """
        Start spindle clockwise (M3).

        Args:
            rpm: Spindle speed in RPM (optional)
        """
        if rpm is not None:
            self.commands.append(f"M3 S{rpm} ; Start spindle clockwise at {rpm} RPM")
        else:
            self.commands.append("M3 ; Start spindle clockwise")

    def spindle_on_ccw(self, rpm=None):
        """
        Start spindle counter-clockwise (M4).

        Args:
            rpm: Spindle speed in RPM (optional)
        """
        if rpm is not None:
            self.commands.append(f"M4 S{rpm} ; Start spindle counter-clockwise at {rpm} RPM")
        else:
            self.commands.append("M4 ; Start spindle counter-clockwise")

    def spindle_off(self):
        self.commands.append("M5 ; Stop spindle")
