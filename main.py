import os
import json

import cv2



def cv_show(name, image):
    img_height, img_width = image.shape[:2]
    
    if img_width > screen_width or img_height > screen_height:
        resized_image = cv2.resize(image, (int(image.shape[1] / 2), int(image.shape[0] / 2)))
    else:
        resized_image = image
        
    cv2.imshow(name, resized_image)



config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as config_file:
    config = json.load(config_file)

screen_width = config['screen_width']
screen_height = config['screen_height']
accepted_extensions = config['accepted_extensions_for_images']
unprocessed_images_directory = config['unprocessed_images_directory']

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
    cv_show(image_filename, image)
    cv2.waitKey()
    cv2.destroyAllWindows()