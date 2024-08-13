import os
import time
import json

import cv2
import numpy as np
import pandas as pd



# File operation
def remove_extension(name):
    name = os.path.splitext(name)[0]
    return name

def add_timestamp_and_png(name):
    timestamp = int(time.time())
    file_name = f'{name}_{timestamp}.png'
    return file_name

def save_image(file_name, image, path, message):
    full_path = os.path.join(path, file_name)
    os.makedirs(path, exist_ok=True)
    cv2.imwrite(full_path, image)
    print(f'{message} {full_path}')



# Extract data
def get_min_feret(contour):
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)  
    box = np.intp(box)
    width, height = rect[1]
    return pixel_to_micrometer * min(width, height)

def get_max_feret(contour):
    
    def distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))
    
    def rotate_contour(contour, angle):
        M = cv2.moments(contour)
        if M['m00'] == 0:
            return contour  
        cX = int(M['m10'] / M['m00'])
        cY = int(M['m01'] / M['m00'])
        center = (cX, cY)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated_contour = cv2.transform(contour, rotation_matrix)
        return rotated_contour
    
    if len(contour.shape) == 2:
        contour = contour.reshape(-1, 1, 2)
    
    hull = cv2.convexHull(contour, returnPoints=True)
    
    max_distance = 0
    num_angles = 360
    angle_step = 360 / num_angles
    
    for angle in range(0, 360, int(angle_step)):
        rotated_contour = rotate_contour(hull, angle)
        for i in range(len(rotated_contour)):
            for j in range(i + 1, len(rotated_contour)):
                dist = distance(rotated_contour[i][0], rotated_contour[j][0])
                if dist > max_distance:
                    max_distance = dist
    
    return pixel_to_micrometer * max_distance

def get_roundness(contour):
    center, radius = cv2.minEnclosingCircle(contour)
    center = (int(center[0]), int(center[1]))
    roundness = cv2.contourArea(contour) / (np.pi * (radius ** 2))
    return roundness



# Excel
def ensure_excel_file_exists():
    if not os.path.exists(excel_file):
        df = pd.DataFrame(columns=required_columns)
        df.to_excel(excel_file, index=False)
    else:
        df = pd.read_excel(excel_file)
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = pd.NA
        
        df = df[required_columns]
        
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')

def append_row(photo_name, min_feret_diameter='N/A', max_feret_diameter='N/A', roundness='N/A'):
    ensure_excel_file_exists()
    
    new_data_df = pd.DataFrame({
        'Photo name': [photo_name],
        'Minimum feret diameter (μm)': [min_feret_diameter],
        'Maximum feret diameter (μm)': [max_feret_diameter],
        'Roundness': [roundness]
    })
    
    existing_df = pd.read_excel(excel_file)
    existing_df = existing_df[required_columns]
    new_data_df = new_data_df.dropna(axis=1, how='all')
    updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)
    
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        updated_df.to_excel(writer, index=False, sheet_name='Sheet1')
    
    print(f"Data has been appended to '{excel_file}'.")



# Image processing
def cv_show(name, image):
    global resized_image, resize_ratio
    img_height, img_width = image.shape[:2]
    if img_width > screen_width or img_height > screen_height:
        resize_ratio = 0.5
        resized_image = cv2.resize(image, (int(img_width * resize_ratio), int(img_height * resize_ratio)))
    else:
        resize_ratio = 1.0
        resized_image = image
    cv2.imshow(name, resized_image)

def detect_edges(image, binary_threshold_low):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (7, 7), 0)
    _, thresholded_image = cv2.threshold(blurred_image, binary_threshold_low, 255, cv2.THRESH_BINARY)
    canny = cv2.Canny(thresholded_image, 0, 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    return cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)

def setup_trackbar(window_name, initial_threshold_low=200):
    cv2.namedWindow(window_name)
    cv2.createTrackbar('Threshold Low', window_name, initial_threshold_low, 255, lambda x: None)

def get_trackbar_value(window_name):
    threshold_low = cv2.getTrackbarPos('Threshold Low', window_name)
    return threshold_low

def process_with_scrollbar(image, image_filename):
    setup_trackbar(image_filename)
    
    processed_image = image.copy()
    contours = []
    
    cv_show(image_filename, processed_image)
    cv2.moveWindow(image_filename, -1, 1)
    
    prev_threshold_low = get_trackbar_value(image_filename)
    
    while True:
        threshold_low = get_trackbar_value(image_filename)
        
        if threshold_low != prev_threshold_low:
            processed_image = image.copy()
            edges_image = detect_edges(processed_image, threshold_low)
            contours, _ = cv2.findContours(edges_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(processed_image, contours, -1, (0, 0, 255), 1)
            cv_show(image_filename, processed_image)
            cv2.moveWindow(image_filename, 1, 1)
            
            prev_threshold_low = threshold_low
            
        cv2.setMouseCallback(image_filename, mouse_callback, (image_filename, processed_image, contours,))
        
        key = cv2.waitKey(100) & 0xFF  
        if key == ord('q'):  
            break

    cv2.destroyAllWindows()

def mouse_callback(event, x, y, flags, param):
    image_filename, image, contours = param
    if event == cv2.EVENT_LBUTTONDOWN:
        original_x = int(x / resize_ratio)
        original_y = int(y / resize_ratio)
        #print(f"Mouse clicked at: ({original_x}, {original_y})")
        
        for contour in contours:
            if cv2.pointPolygonTest(contour, (original_x, original_y), False) >= 0:
                x, y, w, h = cv2.boundingRect(contour)
                cropped_image = image[y:y+h, x:x+w]
                
                image_filename = remove_extension(image_filename)
                image_filename = add_timestamp_and_png(f'{image_filename}_particle')
                save_image(f'{image_filename}', cropped_image, detected_particles_directory, 'Particle image saved:')
                
                
                
                min_feret, max_feret, roundness = 'N/A'
                if min_feret_bool:
                    min_feret = get_min_feret(contour)
                    print(f'Minimum feret: {get_min_feret(contour)}μm')
                if max_feret_bool:
                    max_feret = get_max_feret(contour)
                    print(f'Maximum feret: {get_max_feret(contour)}μm')
                if roundness_bool:
                    roundness = get_roundness(contour)
                    print(f'Roundness: {get_roundness(contour)}%\n')
                    
                append_row(image_filename, min_feret, max_feret, roundness)
                
                break





# Load user configuration from config.json
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

screen_width = config['screen_width']
screen_height = config['screen_height']

accepted_extensions = config['accepted_extensions_for_images']
unprocessed_images_directory = config['unprocessed_images_directory']

detected_particles_directory = config['detected_particles_directory']
excel_file = config['excel_file']
required_columns = ['Photo name', 'Minimum feret diameter (μm)', 'Maximum feret diameter (μm)', 'Roundness']

scale_bar_width_pixels = config['scale_bar_width_pixels']
scale_bar_value_micrometers = config['scale_bar_value_micrometers']
pixel_to_micrometer = scale_bar_value_micrometers / scale_bar_width_pixels

min_feret_bool = config['min_feret_diameter']
max_feret_bool = config['max_feret_diameter']
roundness_bool = config['roundness']





# Detect images and process them one by one
unprocessed_image_files = [
    file for file in os.listdir(unprocessed_images_directory)
    if os.path.isfile(os.path.join(unprocessed_images_directory, file))
    and os.path.splitext(file)[1].lower() in accepted_extensions  
]
print(f'Detected: {len(unprocessed_image_files)} images')

if not unprocessed_image_files:
    print("No unprocessed images found")
    exit()
    
for image_filename in unprocessed_image_files:
    path = os.path.join(unprocessed_images_directory, image_filename)
    print("Displaying image:", path)
    image = cv2.imread(path)
    
    process_with_scrollbar(image, image_filename)
    
    cv2.waitKey()
    cv2.destroyAllWindows()