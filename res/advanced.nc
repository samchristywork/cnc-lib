; Advanced G-code test file
; Demonstrates: square, rounded square, circle, and filled rectangle

; Initialize machine
G21 ; Set units to millimeters
G90 ; Absolute positioning mode
G17 ; XY plane selection

; ===== PATTERN 1: Simple Square =====
G0 X10 Y10 Z5 ; Move to starting position
G1 Z0 F500 ; Lower to work surface
G1 X40 Y10 F2000 ; Bottom edge
G1 X40 Y40 ; Right edge
G1 X10 Y40 ; Top edge
G1 X10 Y10 ; Left edge (back to start)
G0 Z5 ; Lift up

; ===== PATTERN 2: Square with Rounded Corners =====
G0 X60 Y15 Z5 ; Move to starting position
G1 Z0 F500 ; Lower to work surface
G1 X85 Y15 F2000 ; Bottom edge
G3 X90 Y20 I0 J5 ; Bottom-right corner (arc)
G1 X90 Y45 ; Right edge
G3 X85 Y50 I-5 J0 ; Top-right corner (arc)
G1 X60 Y50 ; Top edge
G3 X55 Y45 I0 J-5 ; Top-left corner (arc)
G1 X55 Y20 ; Left edge
G3 X60 Y15 I5 J0 ; Bottom-left corner (arc)
G0 Z5 ; Lift up

; ===== PATTERN 3: Circle =====
G0 X120 Y30 Z5 ; Move to starting position
G1 Z0 F500 ; Lower to work surface
G2 X120 Y30 I15 J0 F2000 ; Full circle (radius 15mm, center at X135 Y30)
G0 Z5 ; Lift up

; ===== PATTERN 4: Filled Rectangle (Raster Pattern) =====
; Rectangle from (10,60) to (50,100), step size 2mm
G0 X10 Y60 Z5 ; Move to starting corner
G1 Z0 F500 ; Lower to work surface

; Milling passes - back and forth
G1 X50 Y60 F2000 ; Pass 1: left to right
G1 X50 Y62 ; Step down
G1 X10 Y62 ; Pass 2: right to left
G1 X10 Y64 ; Step down
G1 X50 Y64 ; Pass 3: left to right
G1 X50 Y66 ; Step down
G1 X10 Y66 ; Pass 4: right to left
G1 X10 Y68 ; Step down
G1 X50 Y68 ; Pass 5: left to right
G1 X50 Y70 ; Step down
G1 X10 Y70 ; Pass 6: right to left
G1 X10 Y72 ; Step down
G1 X50 Y72 ; Pass 7: left to right
G1 X50 Y74 ; Step down
G1 X10 Y74 ; Pass 8: right to left
G1 X10 Y76 ; Step down
G1 X50 Y76 ; Pass 9: left to right
G1 X50 Y78 ; Step down
G1 X10 Y78 ; Pass 10: right to left
G1 X10 Y80 ; Step down
G1 X50 Y80 ; Pass 11: left to right
G1 X50 Y82 ; Step down
G1 X10 Y82 ; Pass 12: right to left
G1 X10 Y84 ; Step down
G1 X50 Y84 ; Pass 13: left to right
G1 X50 Y86 ; Step down
G1 X10 Y86 ; Pass 14: right to left
G1 X10 Y88 ; Step down
G1 X50 Y88 ; Pass 15: left to right
G1 X50 Y90 ; Step down
G1 X10 Y90 ; Pass 16: right to left
G1 X10 Y92 ; Step down
G1 X50 Y92 ; Pass 17: left to right
G1 X50 Y94 ; Step down
G1 X10 Y94 ; Pass 18: right to left
G1 X10 Y96 ; Step down
G1 X50 Y96 ; Pass 19: left to right
G1 X50 Y98 ; Step down
G1 X10 Y98 ; Pass 20: right to left
G1 X10 Y100 ; Step down
G1 X50 Y100 ; Pass 21: left to right (final pass)

G0 Z5 ; Lift up

; Return to origin
G0 X0 Y0 Z10

; Program end
M30
