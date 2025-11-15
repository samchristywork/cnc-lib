#!/usr/bin/env python3

import serial
import time
import tkinter as tk
from tkinter import filedialog, ttk
import threading
from datetime import datetime

class CNCController:
    def __init__(self, root):
        self.root = root
        self.root.title("CNC Controller")
        self.connection = None
        self.keyboard_mode = False
        self.command_history = []
        self.history_index = -1
        self.command_counter = 0
        self.keyboard_increment = 1.0
        self.keyboard_feed_rate = 2000

        self.create_widgets()
        self.connect_to_cnc()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = tk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))

        self.status_label = tk.Label(top_frame, text="Disconnected", fg="red", font=("Arial", 12, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=(0, 20))

        self.position_label = tk.Label(top_frame, text="Position: Unknown", font=("Arial", 10))
        self.position_label.pack(side=tk.LEFT)

        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        output_frame = tk.Frame(left_frame)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        columns = ("#", "Time", "Command", "Response", "Status")
        self.command_table = ttk.Treeview(output_frame, columns=columns, show="headings", height=15)

        self.command_table.heading("#", text="#")
        self.command_table.heading("Time", text="Time")
        self.command_table.heading("Command", text="Command")
        self.command_table.heading("Response", text="Response")
        self.command_table.heading("Status", text="Status")

        self.command_table.column("#", anchor=tk.CENTER)
        self.command_table.column("Time", anchor=tk.W)
        self.command_table.column("Command", anchor=tk.W)
        self.command_table.column("Response", anchor=tk.W)
        self.command_table.column("Status", anchor=tk.CENTER)

        self.command_table.tag_configure("OK", foreground="green")
        self.command_table.tag_configure("ERROR", foreground="red")
        self.command_table.tag_configure("WARN", foreground="orange")
        self.command_table.tag_configure("INFO", foreground="blue")

        self.command_table.bind('<ButtonRelease-1>', self.on_table_click)

        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.command_table.yview)
        self.command_table.configure(yscrollcommand=scrollbar.set)

        self.command_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        input_frame = tk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(0, 5))

        self.command_entry = tk.Entry(input_frame, font=("Arial", 10))
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.command_entry.bind('<Return>', lambda e: self.send_command())
        self.command_entry.bind('<Up>', lambda e: self.history_up())
        self.command_entry.bind('<Down>', lambda e: self.history_down())

        send_btn = tk.Button(input_frame, text="Send", command=self.send_command)
        send_btn.pack(side=tk.LEFT)

        button_frame = tk.Frame(left_frame)
        button_frame.pack(fill=tk.X)

        load_btn = tk.Button(button_frame, text="Load File", command=self.load_file)
        load_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.keyboard_btn = tk.Button(button_frame, text="Keyboard Mode", command=self.toggle_keyboard_mode)
        self.keyboard_btn.pack(side=tk.LEFT, padx=(0, 5))

        pos_btn = tk.Button(button_frame, text="Get Position", command=self.get_position)
        pos_btn.pack(side=tk.LEFT)

        keyboard_settings_frame = tk.Frame(left_frame)
        keyboard_settings_frame.pack(fill=tk.X, pady=(5, 0))

        tk.Label(keyboard_settings_frame, text="Keyboard Controls:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(keyboard_settings_frame, text="Increment:").pack(side=tk.LEFT, padx=(0, 2))
        self.increment_entry = tk.Entry(keyboard_settings_frame, width=6)
        self.increment_entry.insert(0, str(self.keyboard_increment))
        self.increment_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(keyboard_settings_frame, text="Feed Rate:").pack(side=tk.LEFT, padx=(0, 2))
        self.feed_rate_entry = tk.Entry(keyboard_settings_frame, width=6)
        self.feed_rate_entry.insert(0, str(self.keyboard_feed_rate))
        self.feed_rate_entry.pack(side=tk.LEFT, padx=(0, 10))

        update_btn = tk.Button(keyboard_settings_frame, text="Update", command=self.update_keyboard_settings)
        update_btn.pack(side=tk.LEFT)

        right_frame = tk.Frame(content_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        commands_canvas = tk.Canvas(right_frame, width=200)
        commands_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=commands_canvas.yview)
        commands_container = tk.Frame(commands_canvas)

        commands_container.bind(
            "<Configure>",
            lambda e: commands_canvas.configure(scrollregion=commands_canvas.bbox("all"))
        )

        commands_canvas.create_window((0, 0), window=commands_container, anchor="nw")
        commands_canvas.configure(yscrollcommand=commands_scrollbar.set)

        commands_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        commands_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        control_frame = tk.LabelFrame(commands_container, text="Control", padx=5, pady=5)
        control_frame.pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Feed Hold (!)", command=lambda: self.connection.write(b'!'), width=20).pack(fill=tk.X, pady=1)
        tk.Button(control_frame, text="Resume (~)", command=lambda: self.connection.write(b'~'), width=20).pack(fill=tk.X, pady=1)
        tk.Button(control_frame, text="Soft Reset", command=lambda: self.connection.write(b'\x18'), bg="orange", width=20).pack(fill=tk.X, pady=1)
        tk.Button(control_frame, text="Unlock ($X)", command=lambda: self.send_gcode("$X"), width=20).pack(fill=tk.X, pady=1)

        position_frame = tk.LabelFrame(commands_container, text="Position & Zero", padx=5, pady=5)
        position_frame.pack(fill=tk.X, pady=2)
        tk.Button(position_frame, text="Home (G28)", command=lambda: self.send_gcode("G28"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Set Zero All", command=lambda: self.send_gcode("G92 X0 Y0 Z0"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Set Z Zero", command=lambda: self.send_gcode("G92 Z0"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Go To Zero", command=lambda: self.send_gcode("G90\nG0 X0 Y0 Z0"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Go To Z0", command=lambda: self.send_gcode("G90\nG0 Z0"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Save Pos (G28.1)", command=lambda: self.send_gcode("G28.1"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Go Saved (G28)", command=lambda: self.send_gcode("G28"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Probe Z", command=lambda: self.send_gcode("G38.2 Z-25 F50"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Absolute (G90)", command=lambda: self.send_gcode("G90"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(position_frame, text="Relative (G91)", command=lambda: self.send_gcode("G91"), width=20).pack(fill=tk.X, pady=1)

        spindle_frame = tk.LabelFrame(commands_container, text="Spindle & Coolant", padx=5, pady=5)
        spindle_frame.pack(fill=tk.X, pady=2)
        tk.Button(spindle_frame, text="Spindle On (1000)", command=lambda: self.send_gcode("M3 S1000"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(spindle_frame, text="Spindle Off", command=lambda: self.send_gcode("M5"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(spindle_frame, text="S5000", command=lambda: self.send_gcode("M3 S5000"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(spindle_frame, text="S10000", command=lambda: self.send_gcode("M3 S10000"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(spindle_frame, text="Coolant On", command=lambda: self.send_gcode("M8"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(spindle_frame, text="Coolant Off", command=lambda: self.send_gcode("M9"), width=20).pack(fill=tk.X, pady=1)

        settings_frame = tk.LabelFrame(commands_container, text="Settings & Feed", padx=5, pady=5)
        settings_frame.pack(fill=tk.X, pady=2)
        tk.Button(settings_frame, text="Feed 500", command=lambda: self.send_gcode("F500"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(settings_frame, text="Feed 1000", command=lambda: self.send_gcode("F1000"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(settings_frame, text="Millimeters", command=lambda: self.send_gcode("G21"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(settings_frame, text="Inches", command=lambda: self.send_gcode("G20"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(settings_frame, text="Dwell 1s", command=lambda: self.send_gcode("G4 P1"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(settings_frame, text="Dwell 5s", command=lambda: self.send_gcode("G4 P5"), width=20).pack(fill=tk.X, pady=1)

        status_frame = tk.LabelFrame(commands_container, text="Status & Info", padx=5, pady=5)
        status_frame.pack(fill=tk.X, pady=2)
        tk.Button(status_frame, text="Status (?)", command=lambda: self.connection.write(b'?'), width=20).pack(fill=tk.X, pady=1)
        tk.Button(status_frame, text="Parser State", command=lambda: self.send_gcode("$G"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(status_frame, text="Settings ($$)", command=lambda: self.send_gcode("$$"), width=20).pack(fill=tk.X, pady=1)
        tk.Button(status_frame, text="Check Mode", command=lambda: self.send_gcode("$C"), width=20).pack(fill=tk.X, pady=1)

        self.root.bind('<KeyPress>', self.on_key_press)

    def connect_to_cnc(self):
        baudrates = [115200, 9600, 19200, 38400, 57600, 250000]

        for baudrate in baudrates:
            try:
                self.connection = serial.Serial(
                    port='/dev/ttyUSB0',
                    baudrate=baudrate,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    timeout=2
                )
                time.sleep(0.5)
                if self.connection.is_open:
                    self.status_label.config(text=f"Connected ({baudrate} baud)", fg="green")
                    self.log(f"Connected successfully at {baudrate} baud")
                    return
            except:
                continue

        self.status_label.config(text="Connection Failed", fg="red")
        self.log("Failed to connect to CNC")

    def log(self, message, command="", response="", status="INFO"):
        self.command_counter += 1
        timestamp = datetime.now().strftime("%H:%M:%S")

        if not command and not response:
            command = message
            response = ""

        self.command_table.insert("", tk.END, values=(
            self.command_counter,
            timestamp,
            command,
            response,
            status
        ), tags=(status,))
        self.command_table.yview_moveto(1.0)

    def send_gcode(self, gcode):
        if not self.connection or not self.connection.is_open:
            self.log("Not connected", status="ERROR")
            return

        try:
            self.connection.write((gcode + '\n').encode())
            time.sleep(0.1)
            responses = []
            while self.connection.in_waiting > 0:
                response = self.connection.readline().decode().strip()
                if response:
                    responses.append(response)

            if responses:
                for response in responses:
                    status = "OK" if response.lower() in ["ok", "ok\n"] else "INFO"
                    if "error" in response.lower():
                        status = "ERROR"
                    self.log("", command=gcode, response=response, status=status)
            else:
                self.log("", command=gcode, response="(no response)", status="WARN")
        except Exception as e:
            self.log("", command=gcode, response=str(e), status="ERROR")

    def send_command(self):
        command = self.command_entry.get().strip()
        if command:
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            self.send_gcode(command)
            self.command_entry.delete(0, tk.END)

    def on_table_click(self, event):
        selection = self.command_table.selection()
        if selection:
            item = self.command_table.item(selection[0])
            values = item['values']
            if values and len(values) > 2:
                command = values[2]
                if command:
                    self.command_entry.delete(0, tk.END)
                    self.command_entry.insert(0, command)
                    self.command_entry.focus()

    def history_up(self):
        if not self.command_history:
            return
        if self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])

    def history_down(self):
        if not self.command_history:
            return
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index == len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.command_entry.delete(0, tk.END)

    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Select G-code file",
            filetypes=[("G-code files", "*.nc *.gcode"), ("All files", "*.*")]
        )

        if filename:
            self.log(f"Loading file: {filename}")
            try:
                with open(filename, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith(';'):
                            self.send_gcode(line)
                            time.sleep(0.1)
            except Exception as e:
                self.log(f"Error loading file: {e}")

    def update_keyboard_settings(self):
        try:
            increment = float(self.increment_entry.get())
            feed_rate = int(self.feed_rate_entry.get())

            if increment <= 0 or feed_rate <= 0:
                self.log("Increment and feed rate must be positive values", status="ERROR")
                return

            self.keyboard_increment = increment
            self.keyboard_feed_rate = feed_rate
            self.log(f"Keyboard settings updated: Increment={increment}, Feed Rate={feed_rate}", status="OK")
            self.root.focus()
        except ValueError:
            self.log("Invalid increment or feed rate value", status="ERROR")
            self.root.focus()

    def toggle_keyboard_mode(self):
        self.keyboard_mode = not self.keyboard_mode

        if self.keyboard_mode:
            self.keyboard_btn.config(relief=tk.SUNKEN, bg="lightgreen")
            self.log("Keyboard mode enabled")
            self.send_gcode("G21")
            self.send_gcode("G91")
        else:
            self.keyboard_btn.config(relief=tk.RAISED)
            default_bg = self.root.cget("bg")
            self.keyboard_btn.config(bg=default_bg)
            self.log("Keyboard mode disabled")

    def on_key_press(self, event):
        if not self.keyboard_mode:
            return

        key = event.char.lower()
        inc = self.keyboard_increment
        feed = self.keyboard_feed_rate

        key_map = {
            'w': f'G1 Y{inc} F{feed}',
            's': f'G1 Y-{inc} F{feed}',
            'a': f'G1 X-{inc} F{feed}',
            'd': f'G1 X{inc} F{feed}',
            'q': f'G1 Z{inc} F{feed}',
            'e': f'G1 Z-{inc} F{feed}',
        }

        if key in key_map:
            self.send_gcode(key_map[key])

    def get_position(self):
        threading.Thread(target=self.get_position_async, daemon=True).start()

    def get_position_async(self):
        if not self.connection or not self.connection.is_open:
            return

        try:
            self.connection.reset_input_buffer()
            self.connection.write(b'?')
            time.sleep(0.1)

            while self.connection.in_waiting > 0:
                response = self.connection.readline().decode().strip()
                if response and response != 'ok':
                    self.root.after(0, lambda r=response: self.position_label.config(text=f"Position: {r}"))
                    self.root.after(0, lambda r=response: self.log("", command="?", response=r, status="INFO"))
                    break
        except Exception as e:
            self.root.after(0, lambda e=e: self.log("", command="?", response=str(e), status="ERROR"))

    def on_closing(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = CNCController(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
