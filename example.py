#!/usr/bin/env python3
"""
Convert Coin.png to G-code instructions.
Black regions are traced with spindle at -2mm, other regions at start height.
"""

from gcode_generator import GCodeGenerator
from PIL import Image
import sys

def is_black(pixel, threshold=128):
    if isinstance(pixel, (tuple, list)):
        r, g, b = pixel[0], pixel[1], pixel[2]
        brightness = (r + g + b) / 3
    else:
        brightness = pixel

    return brightness < threshold

def image_to_gcode(image_path, output_path, z_down=-2.0, z_up=0.0, feed_rate=500,
                   output_width_mm=50, output_height_mm=50, num_rows=500, num_cols=500):
    """
    Convert an image to G-code by tracing it line by line.

    Args:
        image_path: Path to input image file
        output_path: Path to output G-code file
        z_down: Z height for black regions (mm)
        z_up: Z height for non-black regions (mm)
        feed_rate: Feed rate for linear moves (mm/min)
        output_width_mm: Output width in millimeters
        output_height_mm: Output height in millimeters
        num_rows: Number of rows to sample from image
        num_cols: Number of columns to sample from image
    """
    print(f"Loading image: {image_path}")
    img = Image.open(image_path)
    width, height = img.size
    print(f"Image size: {width}x{height} pixels")

    step_size_x = width / num_cols
    step_size_y = height / num_rows

    scale_x = output_width_mm / num_cols
    scale_y = output_height_mm / num_rows

    print(f"Output size: {output_width_mm}x{output_height_mm} mm")
    print(f"Sampling: {num_cols}x{num_rows} points")
    print(f"Step size: {step_size_x:.2f}x{step_size_y:.2f} pixels")
    print(f"Resolution: {scale_x:.4f}x{scale_y:.4f} mm per point")

    if img.mode != 'RGB':
        img = img.convert('RGB')

    g = GCodeGenerator()

    g.add_comment("=" * 50)
    g.add_comment(f"G-code generated from {image_path}")
    g.add_comment(f"Image size: {width}x{height} pixels")
    g.add_comment(f"Output size: {output_width_mm}x{output_height_mm} mm")
    g.add_comment(f"Sampling grid: {num_cols}x{num_rows} points")
    g.add_comment(f"Z down (black): {z_down} mm")
    g.add_comment(f"Z up (non-black): {z_up} mm")
    g.add_comment("=" * 50)
    g.add_comment("")

    g.set_units_metric()
    g.set_absolute_positioning()
    g.add_comment("")

    g.add_comment("Move to start position")
    g.rapid_move(x=0, y=0, z=z_up)
    g.add_comment("")

    print("Generating G-code...")

    current_z = z_up
    total_moves = 0

    for row_idx in range(num_rows):
        if row_idx % 100 == 0:
            print(f"Processing row {row_idx}/{num_rows}")
            g.add_comment(f"Row {row_idx}")
        pixel_y = int(row_idx * step_size_y)
        if row_idx % 2 == 0:
            col_indices = range(num_cols)
        else:
            col_indices = range(num_cols - 1, -1, -1)

        for col_idx in col_indices:
            pixel_x = int(col_idx * step_size_x)
            pixel = img.getpixel((pixel_x, pixel_y))
            if is_black(pixel):
                desired_z = z_down
            else:
                desired_z = z_up
            out_x = col_idx * scale_x
            out_y = row_idx * scale_y

            if desired_z != current_z:
                g.linear_move(z=desired_z, feed_rate=feed_rate)
                current_z = desired_z

            g.linear_move(x=out_x, y=out_y, feed_rate=feed_rate)
            total_moves += 1

    print(f"Total moves: {total_moves}")

    g.add_comment("")
    g.add_comment("Return to safe position")
    g.linear_move(z=z_up, feed_rate=feed_rate)
    g.rapid_move(x=0, y=0)

    g.add_comment("")
    g.program_end()

    gcode = g.get_gcode()
    with open(output_path, 'w') as f:
        f.write(gcode)

    print(f"\nG-code written to: {output_path}")
    print(f"Total lines: {len(gcode.splitlines())}")

    svg_path = output_path.replace('.gcode', '.svg')
    svg = g.get_svg(width=1000, height=1000)
    with open(svg_path, 'w') as f:
        f.write(svg)
    print(f"SVG visualization written to: {svg_path}")


if __name__ == "__main__":
    IMAGE_PATH = "Coin.png"
    OUTPUT_PATH = "output.gcode"
    Z_DOWN = -2.0  # Height for black regions (mm)
    Z_UP = 0.0     # Start/safe height (mm)
    FEED_RATE = 500  # Feed rate (mm/min)
    OUTPUT_WIDTH_MM = 50   # Output width in mm
    OUTPUT_HEIGHT_MM = 50  # Output height in mm
    NUM_ROWS = 500  # Number of rows to sample
    NUM_COLS = 500  # Number of columns to sample

    try:
        img = Image.open(IMAGE_PATH)
        img.close()
    except FileNotFoundError:
        print(f"Error: Image file '{IMAGE_PATH}' not found!")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    image_to_gcode(
        image_path=IMAGE_PATH,
        output_path=OUTPUT_PATH,
        z_down=Z_DOWN,
        z_up=Z_UP,
        feed_rate=FEED_RATE,
        output_width_mm=OUTPUT_WIDTH_MM,
        output_height_mm=OUTPUT_HEIGHT_MM,
        num_rows=NUM_ROWS,
        num_cols=NUM_COLS
    )

    print("\nDone!")
