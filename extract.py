import os
import shutil

def collect_square_files(src_dir: str, dest_dir: str, start: int, end: int, filename: str) -> None:
    """
    Collects specified files (e.g., `square_5_5.png`) from directories named frames_<n> 
    (where n is in the range [start, end]) and copies them into a destination directory.

    Args:
        src_dir (str): The root directory containing the frames directories.
        dest_dir (str): The destination directory to store the collected files.
        start (int): The starting index for the range of directories.
        end (int): The ending index for the range of directories.
        filename (str): The name of the file to collect from each directory.
    """
    # Ensure the destination directory exists
    os.makedirs(dest_dir, exist_ok=True)

    for i in range(start, end + 1):
        frame_dir = os.path.join(src_dir, f"frames_{i}")
        source_file = os.path.join(frame_dir, filename)

        if os.path.exists(source_file):
            dest_file = os.path.join(dest_dir, f"{filename}_frame_{i}.png")
            shutil.copy(source_file, dest_file)
            print(f"Copied: {source_file} -> {dest_file}")
        else:
            print(f"File not found: {source_file}")

# Example usage:
# Collect files named "square_5_5.png" from directories frames_1 to frames_5
# and place them in a new directory "collected_squares"
collect_square_files("frames", "collected_squares", 1, 5, "square_5_5.png")
