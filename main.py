from PIL import Image
import numpy as np
import pandas as pd
import time
import os
import glob

import sensor
import oled
import camera
import servo
import classify

# Function for dumping trash according to predicted category
def dump_trash_category(dump_trash, category):
    if category == "Daur Ulang":
        dump_trash.dump_trash_front()
    elif category == "Guna Ulang":
        dump_trash.dump_trash_front_right()
    elif category == "B3":
        dump_trash.dump_trash_back_right()
    elif category == "Organik":
        dump_trash.dump_trash_back_left()
    elif category == "Residu":
        dump_trash.dump_trash_front_left()
    else:
        raise ValueError(f"Cateogry {category} is not valid")

# Display result on the tiny oled screen
def oled_update_result(oled_screen, result):
    pred_category = result['category']
    pred_sub_category = result['sub_category']
    pred_prob = result['probability']
    pred_time = result['time']
    
    oled_screen.display_text(
        f"{pred_category} prob : {pred_prob}",
        f"{pred_sub_category} {pred_time} ms"
        )

# Save image and it's prediction result
def save_prediction_result(image, result, df, img_path, csv_path):
    if not os.path.exists(img_path) :
        os.makedirs(img_path)
    
    # File increment
    i = 0
    while os.path.exists(f"{img_path}/image-{i}.jpeg"):
        i += 1
    
    img_name = f"image-{i}.jpeg"
    image.save(f"{img_path}/{img_name}")
    columns = ['name', 'pred_category', 'pred_subcategory','probability', 'classifying_time_ms']
    
    pred_category = result['category']
    pred_sub_category = result['sub_category']
    pred_prob = result['probability']
    pred_time = result['time']    
    
    df.loc[i, columns] = [img_name, pred_category, pred_sub_category, pred_prob, pred_time]
    
    df.to_csv(csv_path, index = False)

# Load previous dataframe if exist
def load_dataframe(path = None):
    columns = ['name', 'pred_category', 'pred_subcategory','probability', 'classifying_time_ms']
    
    df = pd.DataFrame(columns = columns)
    
    if path and os.path.exists(path):
        df = pd.read_csv(path)
    
    return df

def main():
    try:
        dump_trash = servo.DumpTrash()
        dist_sensor = sensor.DistanceSensor()
        ir_sensor = sensor.IRSensor()
        picam = camera.Camera()
        oled_screen = oled.Oled()
        img_classifier = classify.ImageClassifier(path = "model")
        
        IMG_DIM = img_classifier.get_input_shape()
    except:
        print("Something went wrong")
    else:
        print("All module loaded")

    # Set up path for prediction results
    prediction_result_path = "classified-image"
    img_path = f"{prediction_result_path}/images"
    csv_path = f"{prediction_result_path}/img_metadata.csv"
    
    # Set up dataframe to save image's informations
    df = load_dataframe(csv_path)
    
    while True:
        #time1 = time.time()
        #oled_screen.display_hardware_info()
        
        if dist_sensor.check_object() or ir_sensor.check_object():
            print("Object Detected!")
            time.sleep(1)
            img = picam.capture_img().convert('RGB')
            
            img = classify.preprocess_img(img, IMG_DIM)
            
            result = img_classifier.classify_image(img)
            
            oled_update_result(oled_screen, result)
            
            dump_trash_category(dump_trash, result['category'])
            
            save_prediction_result(img, result, df, img_path, csv_path)
            
            time.sleep(0.5)
        
            dist_sensor.update_default()
            
            time.sleep(0.5)

        time.sleep(0.1)
        
        #print(np.round(time.time() - time1, 3))
        
if __name__ == "__main__":
    main()