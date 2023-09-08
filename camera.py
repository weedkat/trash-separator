from picamera2 import Picamera2, Preview
import libcamera
import cv2
import numpy as np
import time

class Camera:
    def __init__(self, capture_size = (1080, 1080), preview_size = (480, 480)):
        self.preview_size = preview_size
        
        try:
            self.picam = Picamera2()
            
            # Set configuration for camera, main for captured imaged, lores for preview
            self.capture_config = self.picam.create_still_configuration(main={"size": capture_size})
            self.preview_config = self.picam.create_preview_configuration(lores={"size": preview_size}, display="lores")
    
            # Trasform image because the camera is flipped on the prototype
            self.capture_config['transform'] = libcamera.Transform(hflip=1, vflip=1)
            self.preview_config['transform'] = libcamera.Transform(hflip=1, vflip=1)
            
            # Turn on the camera
            self.picam.configure(self.preview_config)
            self.picam.start_preview(Preview.QTGL)
            self.picam.start()
            
        except:
            print("Something went wrong")
            
        else:
            print("Camera initialized")
    
    def capture_img(self):
        # Give time to camera to switch mode
        time.sleep(0.1)
        
        # Switch to capture mode for better picture
        self.picam.switch_mode(self.capture_config)
        image = self.picam.capture_image("main")
        
        # Switch back to preview mode to display overlay
        self.picam.switch_mode(self.preview_config)
        return image
    
    def display_text(self, text):
        # Give time to prepare for display
        time.sleep(0.2)
        color = (0, 255, 0, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2
       
        # Center the overlay
        textSize = cv2.getTextSize(text, font, 1, 2)[0]       
        origin = ((self.preview_size[0] - textSize[0]) // 2, 30)
        
        # Make overlay
        overlay = np.zeros((*self.preview_size, 4), dtype=np.uint8)
        cv2.putText(overlay, text, origin, font, scale, color, thickness)
        self.picam.set_overlay(overlay)

# Just for testing
def main():
    camera = Camera()
    image = camera.capture_img().convert('RGB')
    camera.display_text('bruh')
    image.save("image_test_from_module.jpg")
    #time.sleep(5)
    #camera.display_text('test')

if __name__ == "__main__":
    main()