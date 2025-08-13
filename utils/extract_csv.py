import os
import re
import pandas as pd
from .extract_num_from_image import extract_num_from_img

def filter_outliers(num_list):
    return num_list


'''
Args:
    process_group_id(int): The group ID of the images.
    image_dir(str): A path to the directory containing images.
    output_group_dir(str): A directory where CSV file will be saved.
'''
def create_csv(process_group_id, image_dir, output_group_dir):
    try:
        process_group_id = int(process_group_id)
    except (ValueError, TypeError):
        print(f"Error: process_group_id must be a number-like value. Got: {process_group_id}")
        return
    
    # Create the output directory for group CSV if it doesn't exist
    os.makedirs(output_group_dir, exist_ok=True)

    try:
        # Get all image files
        all_filenames = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        target_filenames = [f for f in all_filenames if f.startswith(f"{process_group_id}_")]
            
        if not target_filenames:
            print(f"Info: No image files found for group ID {process_group_id}")
            return
        
    except FileNotFoundError:
        print(f"Error: Directory not found at {image_dir}")
        return
    
    # Sort files into '1_1.png', '1_2.png', ..., '1_10.png'
    def sort_key(filename):
        parts = re.findall(r'\d+', filename)
        return [int(p) for p in parts]
    target_filenames.sort(key=sort_key)

    # Extract numbers from all target images
    all_new_numbers = []
    for filename in target_filenames:
        image_path = os.path.join(image_dir, filename)
        num_list = extract_num_from_img(image_path)

        if num_list:
            all_new_numbers.extend(num_list)
    
    if not all_new_numbers:
        print(f"Warning: No numbers were extracted for group {process_group_id}.")
        return
    
    # Filter outliers
    filtered_numbers = filter_outliers(all_new_numbers)

    new_data_df = pd.DataFrame({
        'group_id': [process_group_id] * len(filtered_numbers),
        'number': filtered_numbers
    })

    # The output path is now specific to the group
    output_file_path = os.path.join(output_group_dir, f"{process_group_id}.csv")

    # Always use write mode, which creates or overwrites the file
    new_data_df.to_csv(output_file_path, index=False)

    print(f"Group {process_group_id} data has been successfully saved to {output_file_path}")