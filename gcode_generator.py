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
