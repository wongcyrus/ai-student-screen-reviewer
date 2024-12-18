import os
import subprocess
from datetime import datetime, timedelta

# Create output folder if it does not exist
output_folder = 'output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)


def combine_images_to_mpg(student_id, image_folder, output_folder):
    # Ensure images are sorted
    images = sorted([img for img in os.listdir(
        image_folder) if img.endswith(".jpeg")])
    
    # Convert filenames to datetime objects
    timestamps = [datetime.strptime(img.split('.')[0], '%Y-%m-%d-%H-%M-%S') for img in images]
    # Sort timestamps
    timestamps.sort()

    # Group images by 10-second intervals
    grouped_timestamps = []
    current_group = []
    interval = timedelta(minutes=10)

    for i in range(len(timestamps)):
        if not current_group:
            current_group.append(i)
        else:
            if timestamps[i] - timestamps[i - 1] <= interval:
                current_group.append(i)
            else:
                grouped_timestamps.append(current_group)
                current_group = [i]

    if current_group:
        grouped_timestamps.append(current_group)

    # Convert grouped timestamps to a dictionary where the key is %Y-%m-%d-%H
    grouped_dict = {}
    for group in grouped_timestamps:
        key = "from " + timestamps[group[0]].strftime('%Y-%m-%d-%H-%M') + " to " + timestamps[group[-1]].strftime('%Y-%m-%d-%H-%M')
        grouped_dict[key] = group

    # Convert the timestamp list values in grouped_dict to str '%Y-%m-%d-%H-%M-%S'
    for key in grouped_dict:
        grouped_dict[key] = [timestamps[i].strftime('%Y-%m-%d-%H-%M-%S').replace('-0', '-') for i in grouped_dict[key]]
        grouped_dict[key] = [f'{ts}.jpeg' for ts in grouped_dict[key]]

        # Flatten the list of grouped images
        images = grouped_dict[key]

        # Create a text file with the list of images
        image_files = os.path.join(output_folder, f'{student_id}-{key}.txt')
        with open(image_files, "w") as file:
            for image in images:
                file.write(f"file '{os.path.join(image_folder, image)}'\n")

        video_path_name = os.path.join(output_folder, f'{student_id}-{key}.mp4')

        # Use ffmpeg to create the video
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', image_files, '-vsync', 'vfr', '-pix_fmt', 'yuv420p', video_path_name
        ])

        print(f"Video saved as {video_path_name}")


# Read student IDs from input/student_id.txt
student_ids_file = 'input/student_id.txt'
with open(student_ids_file, 'r') as file:
    student_ids = [line.strip() for line in file.readlines()]

# Process each student ID
for student_id in student_ids:
    image_folder = os.path.join(
        '/mnt/e/screens', student_id+"@stu.vtc.edu.hk")
    
    if not os.path.exists(image_folder):
        print(f"Image folder for student ID {student_id} does not exist: {image_folder}")
        continue

    # Extract student ID from the image folder path
    student_id = os.path.basename(image_folder).split('@')[0]
    print(f"Student ID: {student_id}")

    combine_images_to_mpg(student_id, image_folder, output_folder)
