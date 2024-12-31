import pygetwindow as gw
import ctypes
import mss
import numpy as np
import cv2
import time

# Set up scaling factor for high-DPI displays
scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

# Find the Bejeweled 3 game window
window_titles = gw.getAllTitles()
target_window = None
for title in window_titles:
    if "Bejeweled 3" in title:  
        target_window = gw.getWindowsWithTitle(title)[0]
        break

if target_window:
    tw_left = int(target_window.left * scaleFactor)
    tw_top = int(target_window.top * scaleFactor)
    tw_width = int(target_window.width * scaleFactor)
    tw_height = int(target_window.height * scaleFactor)
    print(f"Window Found: {target_window.title}")
    print(f"Top-left: ({tw_left}, {tw_top})")
    print(f"Size: {tw_width}x{tw_height}")
else:
    print("Game window not found. Make sure the game is running and visible.")
    exit()

monitor = {
    "top": tw_top,
    "left": tw_left,
    "width": tw_width,
    "height": tw_height
}

monitor_grid = {
    "top": tw_top + 175,
    "left": tw_left + 533,
    "width": 1026,
    "height": 1026
}

print("Monitor Grid:", monitor_grid)

grid_size = 8
cell_width = monitor_grid["width"] // grid_size
cell_height = monitor_grid["height"] // grid_size

grid_squares = []
for row in range(grid_size):
    for col in range(grid_size):
        top_left_x = monitor_grid["left"] + col * cell_width
        top_left_y = monitor_grid["top"] + row * cell_height
        bottom_right_x = top_left_x + cell_width
        bottom_right_y = top_left_y + cell_height

        grid_squares.append({
            "row": row,
            "col": col,
            "top_left": (top_left_x, top_left_y),
            "bottom_right": (bottom_right_x, bottom_right_y)
        })

def get_color_label(avg_color):
    return 'U'

# Video writer setup (optional: for saving the recording)
fps = 30
fourcc = cv2.VideoWriter_fourcc(*"XVID")  # Codec for AVI files
out = cv2.VideoWriter("game_recording.avi", fourcc, fps, (monitor_grid["width"], monitor_grid["height"]))

# Capture loop
with mss.mss() as sct:
    try:
        print("Recording started. Use Ctrl+C to stop.")
        start_time = time.time()
        while True:
            # Capture the game window
            screenshot = sct.grab(monitor_grid)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # Convert to BGR for OpenCV

            height, width, _ = img.shape
            grid_color = (0, 0, 255)  # Red color for the grid
            grid_thickness = 2
            grid_size = 8

            cell_width = width // grid_size
            cell_height = height // grid_size

            color_labels = [["" for _ in range(grid_size)] for _ in range(grid_size)]
            
            for square in grid_squares:
                row = square["row"]
                col = square["col"]
                top_left = (
                    square["top_left"][0] - monitor_grid["left"],
                    square["top_left"][1] - monitor_grid["top"]
                )
                bottom_right = (
                    square["bottom_right"][0] - monitor_grid["left"],
                    square["bottom_right"][1] - monitor_grid["top"]
                )

                # Calculate dimensions
                height = bottom_right[1] - top_left[1]
                width = bottom_right[0] - top_left[0]

                # Adjust coordinates for the cropped region
                cropped_top_left = (
                    top_left[0] + width // 4,
                    top_left[1] + height // 4
                )
                cropped_bottom_right = (
                    bottom_right[0] - width // 4,
                    bottom_right[1] - height // 4
                )

                # Draw rectangle using cropped coordinates
                cv2.rectangle(img, cropped_top_left, cropped_bottom_right, (0, 255, 0), 2)

                # Crop the square region using cropped coordinates
                square_img = img[cropped_top_left[1]:cropped_bottom_right[1], cropped_top_left[0]:cropped_bottom_right[0]]

                # Calculate the average color of the cropped region
                avg_color = np.mean(square_img, axis=(0, 1))  # BGR format
                avg_color_rgb = avg_color[::-1]  # Convert to RGB for labeling

                # Get the color label
                color_label = get_color_label(avg_color_rgb)
                color_labels[row][col] = color_label

            # Draw the labels on the image
            for square in grid_squares:
                top_left = (
                    square["top_left"][0] - monitor_grid["left"],
                    square["top_left"][1] - monitor_grid["top"]
                )
                bottom_right = (
                    square["bottom_right"][0] - monitor_grid["left"],
                    square["bottom_right"][1] - monitor_grid["top"]
                )

                 # Get the center of the square
                center_x = (top_left[0] + bottom_right[0]) // 2
                center_y = (top_left[1] + bottom_right[1]) // 2

                # Get the color label
                row = square["row"]
                col = square["col"]
                label = color_labels[row][col]

                  # Crop the square region to compute the average background color
                square_img = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                
                height, width, _ = square_img.shape
                center_crop = square_img[height//4:3*height//4, width//4:3*width//4]

                    # Calculate the average color for the central region
                avg_color = np.mean(center_crop, axis=(0, 1))  # Average over the cropped region

                avg_color_rgb = avg_color[::-1]  # Convert to RGB for dynamic text color

                inverted_color = (255 - int(avg_color[0]), 255 - int(avg_color[1]), 255 - int(avg_color[2]))

                # Render the label in the center of the square
                # cv2.putText(
                #     img, label, (center_x - 10, center_y + 10),  # Slight offset to center the text
                #     cv2.FONT_HERSHEY_SIMPLEX, 2, inverted_color, 4, cv2.LINE_AA
                # )

                print(f"Row {row}, Col {col}: Avg Color (RGB) = {avg_color_rgb}, Label = {label}")

            # Write the frame to the video file
            out.write(img)
            
            # Ensure 30 FPS (sleep if needed to maintain consistent frame rate)
            elapsed_time = time.time() - start_time
            time.sleep(max(1 / fps - elapsed_time, 0))
            start_time = time.time()
    except KeyboardInterrupt:
        print("Recording stopped by user.")
    finally:
        # Ensure resources are released properly
        print("Cleaning up...")
        out.release()
        cv2.destroyAllWindows()
