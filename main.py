import time
import ctypes

import cv2
import numpy as np
import mss
import pygetwindow as gw

def get_scale_factor() -> float:
    """
    Returns the Windows scale factor for high-DPI devices.
    """
    return ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

def find_bejeweled_window() -> gw.Win32Window:
    """
    Searches all open windows for a title containing 'Bejeweled 3'
    and returns the first matching window. Returns None if not found.
    """
    window_titles = gw.getAllTitles()
    for title in window_titles:
        if "Bejeweled 3" in title:
            return gw.getWindowsWithTitle(title)[0]
    return None

def create_monitor_region(window: gw.Win32Window, scale_factor: float) -> dict:
    """
    Given a window and the scale factor, returns the bounding region
    for the entire window as a dictionary with 'top', 'left', 'width', 'height'.
    """
    return {
        "top": int(window.top * scale_factor),
        "left": int(window.left * scale_factor),
        "width": int(window.width * scale_factor),
        "height": int(window.height * scale_factor)
    }

def create_grid_region(window_region: dict) -> dict:
    """
    Given the bounding region of the entire window, define the
    sub-region that corresponds to the 8x8 gem grid.

    Adjust offsets (175, 533, etc.) and dimensions (1026x1026) as needed.
    """
    return {
        "top": window_region["top"] + 175,
        "left": window_region["left"] + 533,
        "width": 1026,
        "height": 1026
    }

def create_grid_squares(grid_region: dict, grid_size: int = 8) -> list:
    """
    Creates a list of grid squares for the gem area. Each square is a dictionary
    containing the row, col, and pixel coordinates (top_left, bottom_right).
    """
    squares = []
    cell_width = grid_region["width"] // grid_size
    cell_height = grid_region["height"] // grid_size

    for row in range(grid_size):
        for col in range(grid_size):
            top_left_x = grid_region["left"] + col * cell_width
            top_left_y = grid_region["top"] + row * cell_height
            bottom_right_x = top_left_x + cell_width
            bottom_right_y = top_left_y + cell_height

            squares.append({
                "row": row,
                "col": col,
                "top_left": (top_left_x, top_left_y),
                "bottom_right": (bottom_right_x, bottom_right_y)
            })
    return squares

def identify_gem_type() -> str:
    pass

def capture_and_process_frame(
    sct: mss.mss,
    grid_region: dict,
    grid_squares: list,
    video_out: cv2.VideoWriter,
) -> None:
    """
    Captures a screenshot of the grid region, identifies each gem in
    the 8x8 cells, draws the gem label onto the frame, and writes
    the frame to the video output.
    """
    screenshot = sct.grab(grid_region)
    img = np.array(screenshot)

    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    grid_size = 8
    color_labels = [["" for _ in range(grid_size)] for _ in range(grid_size)]

    for square in grid_squares:
        row = square["row"]
        col = square["col"]

        # Adjust coordinates for the cropped region
        top_left = (
            square["top_left"][0] - grid_region["left"],
            square["top_left"][1] - grid_region["top"]
        )
        bottom_right = (
            square["bottom_right"][0] - grid_region["left"],
            square["bottom_right"][1] - grid_region["top"]
        )

        square_img = img[top_left[1]:bottom_right[1],
                         top_left[0]:bottom_right[0]]
        
        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 1)

        # Identify gem type
        #gem_type = identify_gem_type(square_img, reference_images)
        color_labels[row][col] = "U"

    # Draw labels on the image
    for square in grid_squares:
        row = square["row"]
        col = square["col"]
        label = color_labels[row][col]

        top_left = (
            square["top_left"][0] - grid_region["left"],
            square["top_left"][1] - grid_region["top"]
        )
        bottom_right = (
            square["bottom_right"][0] - grid_region["left"],
            square["bottom_right"][1] - grid_region["top"]
        )

        center_x = (top_left[0] + bottom_right[0]) // 2
        center_y = (top_left[1] + bottom_right[1]) // 2

        cv2.putText(
            img,
            label,
            (center_x - 20, center_y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            4,
            cv2.LINE_AA
        )

    # Write the labeled frame to the video file
    video_out.write(img)

def main():
    """
    Main function that sets up the environment, locates the Bejeweled 3 window,
    initializes the video writer, and runs the capture loop.
    """
    # Load reference gem images
    # reference_gems = load_reference_images("gems")

    # Get high-DPI scaling factor
    scale_factor = get_scale_factor()

    # Locate the Bejeweled 3 window
    target_window = find_bejeweled_window()
    if not target_window:
        print("Game window not found. Make sure Bejeweled 3 is running and visible.")
        return

    # Calculate monitor and grid region
    window_region = create_monitor_region(target_window, scale_factor)
    grid_region = create_grid_region(window_region)
    grid_squares = create_grid_squares(grid_region, grid_size=8)

    # Report found window and grid info
    print(f"Window Found: {target_window.title}")
    print(f"Top-left: ({window_region['left']}, {window_region['top']})")
    print(f"Size: {window_region['width']}x{window_region['height']}")
    print("Monitor Grid:", grid_region)

    # Set up video writer
    fps = 24
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("game_recording.avi", fourcc, fps, (grid_region["width"], grid_region["height"]))

    # Capture loop
    with mss.mss() as sct:
        try:
            print("Recording started. Press Ctrl+C to stop.")
            prev_time = time.time()
            frame_count = 0

            while True:
                start_time = time.time()

                # Capture and process the current frame
                capture_and_process_frame(sct, grid_region, grid_squares, out)

                # Calculate and print live FPS
                frame_time = time.time() - start_time
                fps_live = 1 / frame_time if frame_time > 0 else 0
                print(f"Live FPS: {fps_live:.2f}")

                # Ensure a steady frame rate
                elapsed_time = time.time() - prev_time
                time.sleep(max(1 / fps - elapsed_time, 0))
                prev_time = time.time()

                frame_count += 1

        except KeyboardInterrupt:
            print("Recording stopped by user.")
        finally:
            print("Cleaning up...")
            out.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
