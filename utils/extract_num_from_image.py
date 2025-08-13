import cv2
import pytesseract
import numpy as np
from tqdm import tqdm

'''
Args:
    image_path(str): A path of the analyzed image file
Returns:
    list[int]: A list of the extracted numbers
               Returns an empty list on failure
'''
def extract_num_from_img(image_path):
    # 1. Load the image
    try:
        image = cv2.imread(image_path)
        if image is None:
            print(f"Error: Could not load the image. FILE: {image_path}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

    # 2. Find yellow rectangles
    # lower_yellow and upper_yellow are based on HSV
    # Hue 20~30, Saturation 40~255, Value 150~255
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_yellow = np.array([20, 40, 150])
    upper_yellow = np.array([30, 255, 255])
    mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)

    # 3. Detect and sort contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    number_rects = []

    for contour in contours:
        # Filter out small noise
        if cv2.contourArea(contour) < 100:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        number_rects.append((x, y, w, h))

    number_rects.sort(key=lambda x: (x[1], x[0]))

    # 4. Perform OCR on each number area
    extracted_numbers = []
    
    # Loop through each rectange to process and visualize
    for i, (x, y, w, h) in tqdm(enumerate(number_rects), total=len(number_rects), desc=f"Processing Numbers of '{image_path}'"):
        padding = 5
        y_start, y_end = max(0, y - padding), min(image.shape[0], y + h + padding)
        x_start, x_end = max(0, x - padding), min(image.shape[1], x + w + padding)
        roi = image[y_start:y_end, x_start:x_end]

        if roi.size == 0:
            print(f"Image: {image_path}, #{i} is empty.")
            continue

        # Resize ROI for optimizing OCR
        target_height = 100
        aspect_ratio = roi.shape[1] / roi.shape[0]
        target_width = int(target_height * aspect_ratio)
        resized_roi = cv2.resize(roi, (target_width, target_height), interpolation=cv2.INTER_CUBIC)
        
        # Preprocessing
        gray_roi = cv2.cvtColor(resized_roi, cv2.COLOR_BGR2GRAY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 20))
        blackhat = cv2.morphologyEx(gray_roi, cv2.MORPH_BLACKHAT, kernel)
        _, thresh_blackhat = cv2.threshold(blackhat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh_roi = cv2.bitwise_not(thresh_blackhat)

        # blurred_roi = cv2.medianBlur(gray_roi, 3)
        # _, thresh_roi = cv2.threshold(blurred_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        cleaned_number = ""
        custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'

        # Detect most numbers
        text1 = pytesseract.image_to_string(thresh_roi, config=custom_config).strip()

        if text1.isdigit():
            cleaned_number = text1
        else:
            # Try using square dilation
            kernel_v1 = np.ones((3, 3), np.uint8)
            thinned_roi_v1 = cv2.dilate(thresh_roi, kernel_v1, iterations=1)
            text2 = pytesseract.image_to_string(thinned_roi_v1, config=custom_config).strip()
            if text2.isdigit():
                cleaned_number = text2
            else:
                # Try using Cross dilation
                kernel_v2 = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
                thinned_roi_v2 = cv2.dilate(thresh_roi, kernel_v2,iterations=1)
                text3 = pytesseract.image_to_string(thinned_roi_v2, config=custom_config).strip()
                if text3.isdigit():
                    cleaned_number = text3

        # kernel_v1 = np.ones((3, 3), np.uint8)
        # thinned_roi_v1 = cv2.dilate(thresh_roi, kernel_v1, iterations=1)
        # number_text_v1 = pytesseract.image_to_string(thinned_roi_v1, config=custom_config)

        # if number_text_v1.strip().isdigit():
        #     cleaned_number = number_text_v1.strip()
        # else:
        #     # Detect other numbers to using cross kernel
        #     kernel_v2 = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))
        #     thinned_roi_v2 = cv2.dilate(thresh_roi, kernel_v2, iterations=1)
        #     number_text_v2 = pytesseract.image_to_string(thinned_roi_v2, config=custom_config)

        #     if number_text_v2.strip().isdigit():
        #         cleaned_number = number_text_v2.strip()

        if cleaned_number:
            try:
                num = int(cleaned_number)
                extracted_numbers.append(num)

            except ValueError:
                print(f"Warning: Could not convert {cleaned_number} to an integer.")

    return extracted_numbers