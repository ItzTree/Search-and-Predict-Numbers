import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from urllib.parse import urljoin

'''
Args:
    url(str)
    group_id(int): The group ID from this page
    save_directory(str): A directory where images will be saved
'''
def scrape_images(url, group_id, save_directory):
    # Set header to mimic real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        group_id = int(group_id)
    except (ValueError, TypeError):
        print(f"Error: group_id must be a number-like value. Got: {group_id}")
        return

    try:
        # 1. Fetch and parse the webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 2. Find the div tag that include specific images.
        soup = BeautifulSoup(response.text, 'html.parser')
        target_div = soup.find('div', id='powerbbsContent')

        if not target_div:
            print(f"Error: Could not find a <div id='powerbbsContent'> ont the page: {url}")
            return

        # 3. Find all img tags
        image_tags = target_div.find_all('img')
        if not image_tags:
            print(f"Info: No <img> tags found inside the <div id='powerbbsContent'>.")
            return
        
        # 4. Create the save directory if it doesn't exist
        os.makedirs(save_directory, exist_ok=True)
        print(f"Found {len(image_tags)} images. Saving to '{save_directory}'...")

        # 5. Loop through each image tag to download and save
        for sub_id, img_tag in tqdm(enumerate(image_tags, 1), total=len(image_tags), desc=f"Downloading Group {group_id}"):
            # Get the image source URL from the 'src' attribute
            img_src = img_tag.get('src')

            if not img_src:
                print(f"Warning: Skipping an image tag with no 'src' attribute (Image #{sub_id})")
                continue

            # Convert relative URL to absolute URL
            # If img_src is absolute URL, urljoin() doesn't convert to new URL
            full_img_url = urljoin(url, img_src)

            try:
                # Remove URL query
                clean_img_url = full_img_url.split('?')[0]

                # Download the image
                img_response = requests.get(full_img_url, headers=headers, stream=True, timeout=10)
                img_response.raise_for_status()

                # Determine the file extension
                file_extension = os.path.splitext(clean_img_url)[1]

                # If no extension in URL, try to guess
                if not file_extension:
                    content_type = img_response.headers.get('content-type', '').lower()
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        file_extension = '.jpg'
                    elif 'png' in content_type:
                        file_extension = '.png'
                    elif 'gif' in content_type:
                        file_extension = '.gif'
                    else:
                        file_extension = '.jpg'
                
                # Construct the filename
                filename = f"{group_id}_{sub_id}{file_extension}"
                save_path = os.path.join(save_directory, filename)

                # Save the image
                with open(save_path, 'wb') as f:
                    for chunk in img_response.iter_content(1024):
                        f.write(chunk)
            
            except requests.exceptions.RequestException as e:
                print(f"Error downloading {full_img_url}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred for image {full_img_url}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage {url}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")