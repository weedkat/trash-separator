import board
import digitalio

from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import subprocess

class Oled:
    def __init__(self, WIDTH = 128, HEIGHT = 32, font_size = 16):
        try:
            # Define the Reset Pin
            oled_reset = digitalio.DigitalInOut(board.D4)

            # Display Parameters
            #BORDER = 5

            # Display Refresh
            #LOOPTIME = 1.0

            # Use for I2C.
            i2c = board.I2C()
            self.oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3C, reset=oled_reset)

            # Clear display.
            self.oled.fill(0)
            self.oled.show()

            # Create blank image for drawing.
            # Make sure to create image with mode '1' for 1-bit color.
            self.image = Image.new("1", (self.oled.width, self.oled.height))

            # Get drawing object to draw on image.
            self.draw = ImageDraw.Draw(self.image)

            # Draw a white background
            self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=255, fill=255)

            # Load font
            self.font = ImageFont.truetype('PixelOperator.ttf', font_size)
        
        except:
            print("Something went wrong")
            
        else:
            print("Oled Initialized")
    
    def blank_oled(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.oled.width, self.oled.height), outline=0, fill=0)
    
    def show_oled(self):
        # Display image
        self.oled.image(self.image)
        self.oled.show()
    
    # Contents = array of tuple (text, x, y)
    def display_hardware_info(self):
        self.blank_oled()
        font = self.font
        # Update Display
        # Shell scripts for system monitoring from here : https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "top -bn2 | grep '%Cpu' | tail -1 | grep -P '(....|...) id,'|awk '{printf \"CPU:  %.0f%%\", 100-($8/4)}'"
        CPU = subprocess.check_output(cmd, shell = True )
        cmd = "free -m | awk 'NR==2{printf \"RAM: %.0f%%\", $3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell = True )
        cmd = "vcgencmd measure_temp |cut -f 2 -d '='"
        Temp = subprocess.check_output(cmd, shell = True )
        
        # Pi Stats Display
        self.draw.text((0, 0), str(CPU,'utf-8'), font=font, fill=255)
        self.draw.text((70, 0), str(Temp,'utf-8'), font=font, fill=255)
        self.draw.text((0, 16), str(MemUsage,'utf-8'), font=font, fill=255)
        self.draw.text((70, 16), "Ready :)" , font=font, fill=255)
        self.show_oled()
            
    
    def display_text(self, *argv):
        self.blank_oled()
        # Sart from y pixel 0
        y = 0
        for arg in argv:
            self.draw.text((0, y), arg, font=self.font, fill=255)
            y += self.font.size
        self.show_oled()

# Just for testing
def main():
    oled = Oled()
    oled.display_hardware_info()
    #oled.display_text("hello", "world")
    
if __name__ == "__main__":
    main()
