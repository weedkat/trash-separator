from PIL import Image
import numpy as np
import time
import tensorflow as tf
import math
import os

class ImageClassifier:
    def __init__(self, path = None, model_name = None, label_name = "labelmap.txt", category_name = "category.txt"):
        try:
            # Set path
            label_path = f"{path}/{label_name}"
            category_path = f"{path}/{category_name}"
            model_path = f"{path}/{model_name}"
            
            if model_name == None:
                for file in os.listdir(path):
                    if file.endswith(".tflite"):
                        model_path = f"{path}/{file}"
                        break
            
            # Check if path exist
            if not (os.path.exists(model_path)) :
                raise FileNotFoundError(model_path, "doesn't exist")
            if not (os.path.exists(label_path)) :
                raise FileNotFoundError(label_path, "doesn't exist")
            if not (os.path.exists(category_path)) :
                raise FileNotFoundError(category_path, "doesn't exist")
            
            # Import Model
            self.interpreter = tf.lite.Interpreter(model_path)
            
            # Read class labels
            self.labels = load_labels(label_path)
            
            # Read Category
            self.categories = load_labels(category_path)
            
            # Try allocating tensors
            try:
                self.interpreter.allocate_tensors()
                _, self.height, self.width, _ = self.interpreter.get_input_details()[0]['shape']
                print("Image Shape (", self.width, ",", self.height, ")")
            except:
                print("Something went wrong")
            else:
                print("Model and labels are loaded successfully")
        except:
                print("Something went wrong")    
        else:
            print("Ready to classify")
    
    def get_input_shape(self):
        # Get input shape for model
        return (self.height, self.width)
    
    def set_input_tensor(self, image):
        # Select first layer of tensor
        tensor_index = self.interpreter.get_input_details()[0]['index']
        input_tensor = self.interpreter.tensor(tensor_index)()[0]
        # Put the image on tensor's input
        input_tensor[:, :] = image
        input_tensor /= 255.0

    def predict_image(self, image, top_k=1):
        self.set_input_tensor(image)
        # Predicting
        self.interpreter.invoke()
        # Get result
        output_details = self.interpreter.get_output_details()[0]
        output = np.squeeze(self.interpreter.get_tensor(output_details['index']))
        ordered = np.argpartition(-output, 1)
        # Return label's index + probability
        return [(i, output[i]) for i in ordered[:top_k]]

    def classify_image(self, image):
        # Classify the image.
        time1 = time.time()
        label_id, prob = self.predict_image(image)[0]
        time2 = time.time()
        
        result = {
            'category' : self.categories[label_id],
            'sub_category' : self.labels[label_id],
            'probability' : prob,
            'time' : np.round(time2-time1, 3)
            }
        
        return result

# Read the labels from the text file as a Python list
def load_labels(path):
    with open(path, 'r') as f:
        return [line.strip() for i, line in enumerate(f.readlines())]

# Preprocess image to match tensor's input
# 1. Crop the image to the middle according to ratio
# 2. Resize the image to desired size
def preprocess_img(image, size):
    w_target, h_target = size
    w_img, h_img = image.size
    ratio = w_target / h_target
    if(w_img < w_target or h_img < h_target):
        if(w_img < h_img):
            image = image.resize((w_target, int(w_target*ratio)))
        else:
            image = image.resize((int(math.ceil(h_target/ratio)), h_target))
    if w_img > ratio * h_img:
        x, y = (w_img - ratio * h_img) // 2, 0
    else:
        x, y = 0, (h_img - w_img / ratio) // 2
    if w_img % 2 != h_img % 2:
        if w_img < h_img: 
            h_img -= 1
        else:
            h_img += 1
    image = image.crop((x, y, w_img - x, h_img - y))
    image.thumbnail(size, Image.ANTIALIAS)
    return image

# Just for testing
def main():
    image_classifier = ImageClassifier("model")
    image = preprocess_img(Image.open("image_test_from_module.jpg"), image_classifier.get_input_shape())
    result = image_classifier.classify_image(image)
    print(result)
    
if __name__ == "__main__":
    main()
    