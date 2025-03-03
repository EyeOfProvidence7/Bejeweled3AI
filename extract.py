import os
import shutil

import cv2
import numpy as np

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
# collect_square_files("frames", "collected_squares", 1, 5, "square_5_5.png")

# -------------------------------------------------------------------------------------------

# Augmentation Functions
def random_brightness_contrast(image):
    """ Adjust brightness and contrast randomly. """
    alpha = np.random.uniform(0.8, 1.2)  # Contrast
    beta = np.random.randint(-30, 30)    # Brightness
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def add_salt_pepper_noise(image, amount=0.02):
    """ Add salt & pepper noise to simulate sparkle effects. """
    noisy_image = image.copy()
    num_salt = np.ceil(amount * image.size * 0.5)
    coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape[:2]]
    noisy_image[coords[0], coords[1]] = 255  # White pixels (salt)
    return noisy_image

# Define Paths
input_root = "dataset"  # Folder containing {gem_color}_example/ directories
output_root = "augmented_dataset"  # Output folder

# Augmentations Per Image
num_augmentations = 1000  # Generate this many per gem

# Process Each Example Folder
for example_folder in os.listdir(input_root):
    if not example_folder.endswith("_example"):
        continue
    
    gem_color = example_folder.replace("_example", "")
    input_folder = os.path.join(input_root, example_folder)
    output_folder = os.path.join(output_root, gem_color)

    # Ensure Output Directory Exists
    os.makedirs(output_folder, exist_ok=True)

    # Find the single gem image inside
    gem_files = [f for f in os.listdir(input_folder) if f.endswith(".png")]
    if len(gem_files) == 0:
        print(f"Skipping {example_folder}, no image found.")
        continue
    
    gem_image_path = os.path.join(input_folder, gem_files[0])
    original_img = cv2.imread(gem_image_path)

    # Generate Augmented Images
    for i in range(num_augmentations):
        img = original_img.copy()
        
        # Apply Random Transformations
        if np.random.rand() > 0.2: img = random_brightness_contrast(img)
        if np.random.rand() > 0.3: img = add_salt_pepper_noise(img)
        
        # Save Augmented Image
        output_filename = os.path.join(output_folder, f"{gem_color}_{i}.png")
        cv2.imwrite(output_filename, img)

    print(f"Generated {num_augmentations} images for {gem_color}")

print("Data augmentation complete!")
