import cv2
import os
import numpy as np


def overlay_images(image1, image2):
    # Ensure both images are the same size
    if image1.shape != image2.shape:
        raise ValueError("Both images must be of the same shape")

    # Create a mask where `image1` has BGR value (0, 0, 0)
    mask = (image1[:, :, 0] == 0) & (image1[:, :, 1] == 0) & (image1[:, :, 2] == 0)

    # Create a copy of image2 to overlay the result
    result = image2.copy()

    # For pixels where the mask is False (i.e., where image1 is not black),
    # copy the pixels from image1 to result
    result[~mask] = image1[~mask]

    return result


def images_to_video(folder_path, video_name="output_video.mp4", fps=30):
    # Get list of image files in the folder
    images = []
    for i in range(len(os.listdir(folder_path))):
        img_path = os.path.join(folder_path, f"{i}.jpg")
        if os.path.exists(img_path):
            images.append(img_path)
        else:
            break  # Stop if a numbered image is missing

    if not images:
        print("No images found in the specified format.")
        return

    # Read the first image to get the frame size
    frame = cv2.imread(images[0])
    height, width, layers = frame.shape
    size = (width, height)

    # Define the codec and create VideoWriter object
    video_path = os.path.join(folder_path, video_name)
    out = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    # Write each image to the video
    for image in images:
        frame = cv2.imread(image)
        out.write(frame)  # Add frame to the video

    out.release()
    print(f"Video saved successfully at {video_path}")