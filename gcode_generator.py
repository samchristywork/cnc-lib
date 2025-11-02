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

    def dwell(self, seconds):
        """
        Dwell/pause (G4).

        Args:
            seconds: Duration in seconds
        """
        self.commands.append(f"G4 P{seconds:.2f} ; Dwell for {seconds:.2f} seconds")

    def program_end(self):
        self.commands.append("M30 ; End program")

    def get_gcode(self):
        """
        Get the generated G-code as a string.

        Returns:
            String containing all G-code commands
        """
        return "\n".join(self.commands)

    def get_svg(self, width=800, height=600, margin=50):
        """
        Generate an SVG visualization of the tool path.

        Args:
            width: SVG width in pixels
            height: SVG height in pixels
            margin: Margin around the path in pixels

        Returns:
            String containing SVG markup
        """
        if not self.path_history:
            return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"></svg>'

        # Find bounds of the path
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')

        for move in self.path_history:
            for point in [move['start'], move['end']]:
                min_x = min(min_x, point['x'])
                max_x = max(max_x, point['x'])
                min_y = min(min_y, point['y'])
                max_y = max(max_y, point['y'])

            # For arcs, also check the bounding box of the full arc
            if move['type'] in ['arc_cw', 'arc_ccw']:
                import math
                center_x = move['start']['x'] + move['center_offset']['i']
                center_y = move['start']['y'] + move['center_offset']['j']
                radius = math.sqrt(move['center_offset']['i']**2 + move['center_offset']['j']**2)

                # The arc could potentially reach center ± radius in each direction
                # Check if these extremes are actually part of the arc
                min_x = min(min_x, center_x - radius)
                max_x = max(max_x, center_x + radius)
                min_y = min(min_y, center_y - radius)
                max_y = max(max_y, center_y + radius)

        # Calculate scale and offset
        path_width = max_x - min_x
        path_height = max_y - min_y

        if path_width == 0:
            path_width = 1
        if path_height == 0:
            path_height = 1

        drawable_width = width - 2 * margin
        drawable_height = height - 2 * margin

        scale = min(drawable_width / path_width, drawable_height / path_height)

        def transform_x(x):
            return margin + (x - min_x) * scale

        def transform_y(y):
            # Flip Y axis (SVG Y increases downward)
            return height - margin - (y - min_y) * scale

        # Build SVG
        svg_lines = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'  <rect width="{width}" height="{height}" fill="white"/>',
            f'  <g stroke-width="2">',
        ]

        # Draw paths
        for move in self.path_history:
            x1 = transform_x(move['start']['x'])
            y1 = transform_y(move['start']['y'])
            x2 = transform_x(move['end']['x'])
            y2 = transform_y(move['end']['y'])

            if move['type'] == 'rapid':
                # Rapid moves in light gray, dashed
                svg_lines.append(
                    f'    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                    f'stroke="#cccccc" stroke-dasharray="5,5"/>'
                )
            elif move['type'] in ['arc_cw', 'arc_ccw']:
                # Arc moves
                # Calculate center point
                center_x = move['start']['x'] + move['center_offset']['i']
                center_y = move['start']['y'] + move['center_offset']['j']
                cx = transform_x(center_x)
                cy = transform_y(center_y)

                # Calculate radius
                import math
                radius = math.sqrt(move['center_offset']['i']**2 + move['center_offset']['j']**2) * scale

                # Calculate angles
                start_angle = math.atan2(move['start']['y'] - center_y, move['start']['x'] - center_x)
                end_angle = math.atan2(move['end']['y'] - center_y, move['end']['x'] - center_x)

                # Determine sweep flag (1 for CW in SVG coordinates, 0 for CCW)
                # Note: SVG Y-axis is flipped, so we need to invert the sweep direction
                sweep_flag = 1 if move['type'] == 'arc_cw' else 0

                # Determine if this is a large arc
                if move['type'] == 'arc_cw':
                    # Clockwise in G-code
                    angle_diff = start_angle - end_angle
                else:
                    # Counter-clockwise in G-code
                    angle_diff = end_angle - start_angle

                # Normalize angle difference
                while angle_diff < 0:
                    angle_diff += 2 * math.pi
                while angle_diff > 2 * math.pi:
                    angle_diff -= 2 * math.pi

                large_arc_flag = 1 if angle_diff > math.pi else 0

                # Choose color based on Z depth
                if move['end']['z'] < 0:
                    color = "#0066cc"  # Blue for cutting
                else:
                    color = "#00cc66"  # Green for non-cutting moves

                # Draw arc using SVG path
                svg_lines.append(
                    f'    <path d="M {x1:.2f},{y1:.2f} A {radius:.2f},{radius:.2f} 0 '
                    f'{large_arc_flag},{sweep_flag} {x2:.2f},{y2:.2f}" '
                    f'fill="none" stroke="{color}"/>'
                )
            else:
                # Linear moves in blue, solid
                # Check if this is a cutting move (Z below 0)
                if move['end']['z'] < 0:
                    color = "#0066cc"  # Blue for cutting
                else:
                    color = "#00cc66"  # Green for non-cutting moves
                svg_lines.append(
                    f'    <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
                    f'stroke="{color}"/>'
                )

        # Draw start point
        start = self.path_history[0]['start']
        svg_lines.append(
            f'    <circle cx="{transform_x(start["x"]):.2f}" '
            f'cy="{transform_y(start["y"]):.2f}" r="5" fill="green"/>'
        )

        # Draw end point
        end = self.path_history[-1]['end']
        svg_lines.append(
            f'    <circle cx="{transform_x(end["x"]):.2f}" '
            f'cy="{transform_y(end["y"]):.2f}" r="5" fill="red"/>'
        )

        svg_lines.append('  </g>')
        svg_lines.append('</svg>')

        return '\n'.join(svg_lines)

    def clear(self):
        """Clear all generated commands."""
        self.commands = []
        self.current_position = {'x': 0, 'y': 0, 'z': 0}
        self.path_history = []
