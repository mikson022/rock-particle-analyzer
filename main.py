import os
import time
import json

import cv2



def cv_show(name, image):
    img_height, img_width = image.shape[:2]
    
    if img_width > screen_width or img_height > screen_height:
        resized_image = cv2.resize(image, (int(image.shape[1] / 2), int(image.shape[0] / 2)))
    else:
        resized_image = image
        
    cv2.imshow(name, resized_image)

def save_image(name, image, path, message):
    timestamp = int(time.time())
    name = os.path.splitext(name)[0]
    file_name = f'{name}_{timestamp}.png'
    full_path = os.path.join(path, file_name)
    os.makedirs(path, exist_ok=True)
    cv2.imwrite(full_path, image)
    print(f'{message} {full_path}')

def detect_edges(image, binary_threshold_low, binary_threshold_high):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (7, 7), 0)
    _, thresholded_image = cv2.threshold(blurred_image, binary_threshold_low, binary_threshold_high, cv2.THRESH_BINARY)
    canny = cv2.Canny(thresholded_image, 0, 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    return cv2.morphologyEx(canny, cv2.MORPH_CLOSE, kernel)





config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

screen_width = config['screen_width']
screen_height = config['screen_height']
accepted_extensions = config['accepted_extensions_for_images']
unprocessed_images_directory = config['unprocessed_images_directory']
detected_particles_directory = config['detected_particles_directory']

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
    image = detect_edges(image, 200, 255)
    save_image('Detect edges', image, detected_particles_directory, 'Edge detected image saved')
    cv_show(image_filename, image)
    cv2.waitKey()
    cv2.destroyAllWindows()