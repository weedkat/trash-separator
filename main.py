from PIL import Image
from tensorflow.keras.utils import img_to_array, load_img
from pathlib import Path
import numpy as np
import time
import tensorflow as tf
import math
import os
import glob
import sensor
import oled
import camera
import servo
import classify

LOOPTIME = 1.0
i = 1

while True:
    # Update oled screen
    oled.update([("Ready...", 0, 8)])
    if sensor.check_obj() and sensor.check_obj(): # Check if there is an object, takes about a second
        
        # Update Status on oled
        oled.update([("Classifying...", 0, 8)])
        
        # Check if there is a hand in a way before classifying
        while sensor.check_ir() :
            time.sleep(0.5)
        
        # Get Image
        image = camera.capture_img().convert('RGB')

        # Predict Image Class
        image = classify.preprocessImg(image, (224,224))
        category, sub_category, prob, classification_time = classify.classify_image(image)

        # Save classified image on folders
        image_path = "classified-image"

        if not os.path.exists(image_path) :
            os.makedirs(image_path)

        save_img_path = f"{image_path}/{category}/{sub_category}"
        if not os.path.exists(save_img_path):
            os.makedirs(save_img_path)

        # File increment
        i = 0
        while glob.glob(f"{save_img_path}/{sub_category}({i})*.jpeg"):
            i += 1

        # Save Image
        image.save(f"{save_img_path}/{sub_category}({i})_{prob:.2f}.jpeg")
        print(f"{category}, {sub_category}, {prob}, {classification_time}")
        oled.update([(category, 0, 0), (f"{prob*100:.2f}%", 80, 0), (f"{classification_time*1000} ms", 0, 16)])
        
        if category == 'B3' :
            servo.dump_trash(pos = 'front')
        elif category == 'Daur Ulang':
            servo.dump_trash(pos = 'front_right')
        elif category == 'Organik':
            servo.dump_trash(pos = 'back_right')
        elif category == 'Residu':
            servo.dump_trash(pos = 'back_left')
        elif category == 'Guna Ulang':
            servo.dump_trash(pos = 'front_left')
        
        # Wait before another read
        time.sleep(1)
        sensor.update_default()