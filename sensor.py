import RPi.GPIO as GPIO
import time
from statistics import median, mean

class DistanceSensor:
    def __init__(self, trigger_pin = 23, echo_pin = 24, mode = 'BCM', temp = 32):
        try :
            # Define GPIO to use for SRF05
            self.GPIO_TRIGGER = trigger_pin
            self.GPIO_ECHO = echo_pin
            
            # Use BCM GPIO references
            if mode == 'BCM':
                GPIO.setmode(GPIO.BCM)
            elif mode == 'BOARD':
                GPIO.setmode(GPIO.BOARD)
            else:
                raise ValueError(f"Mode '{mode}' is not valid")
            GPIO.setwarnings(False)

            # Speed of sound in cm/s at temperature
            self.speedSound = 33100 + (0.6*temp)

            print("Ultrasonic Measurement")
            print("Speed of sound is",self.speedSound/100,"m/s at",temp,"C")

            # Set pins as output and input
            GPIO.setup(self.GPIO_TRIGGER,GPIO.OUT)
            GPIO.setup(self.GPIO_ECHO,GPIO.IN)

            # Set trigger to False (Low)
            GPIO.output(self.GPIO_TRIGGER, False)

            # Allow module to settle
            time.sleep(0.5)
            
            # Average distance after n times reading for more accurate default distance
            self.update_default()
        
        except:
            print("Something went wrong")
        
        else:
            print("Distance sensor initialized")
            
    def check_distance(self):
        # Send 10us pulse to trigger
        GPIO.output(self.GPIO_TRIGGER, True)
        
        # Wait 10us then turn off trigger
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)
        start = time.time()

        # Start time before echo picked up sounds
        while GPIO.input(self.GPIO_ECHO)==0:
            start = time.time()

        # Stop time after echo picked up sounds
        while GPIO.input(self.GPIO_ECHO)==1:
            stop = time.time()
          
        # Calculate pulse length
        elapsed = stop-start

        # Distance pulse travelled in that time is time
        # Multiplied by the speed of sound
        # Sound (cm/s)
        distance = elapsed * self.speedSound

        # That was the distance there and back so halve the value
        distance = distance / 2
        
        # Need time for the sensors to settle down
        time.sleep(0.1)
        
        return distance	

    def check_object(self, error_margin = 0.4, n_check = 10):
        # The reading is volatile, need error margin to compensate
        # Pick the middle value from distance reading
        dist = median([self.check_distance() for _ in range(n_check)])
        
        # dist < default if the distance sensor bounce of the object
        # dist > default if the distance sensor bounce of the platform
        # both condition indicates that there is an object present
        is_object_present = dist < self.DEFAULT_DIST - error_margin or dist > self.DEFAULT_DIST + error_margin
            
        # Update default distance if there is no object present
        if abs(self.DEFAULT_DIST - dist) < error_margin:
            self.update_default()
            
        return is_object_present

    def update_default(self, n_check = 10):
        self.DEFAULT_DIST = mean([self.check_distance() for _ in range(n_check)])

class IRSensor:
    def __init__(self, ir_pin = 26, mode = 'BCM'):
        try:
            # Define GPIO to use for IR sensor
            self.GPIO_IR = ir_pin
            
            # Use BCM GPIO references
            if mode == 'BCM':
                GPIO.setmode(GPIO.BCM)
            elif mode == 'BOARD':
                GPIO.setmode(GPIO.BOARD)
            else:
                raise ValueError(f"Mode '{mode}' is not valid")
            GPIO.setwarnings(False)
            
            # Set infrared pin
            GPIO.setup(self.GPIO_IR, GPIO.IN)
            
            # Allow module to settle
            time.sleep(0.5)
            
        except:
            print("Something went wrong")
            
        else:
            print("Infrared sensor initialized")

    def check_object(self):
        # GPIO.input(GPIO_IR) true when there is no object
        return not GPIO.input(self.GPIO_IR)

# Just for testing
def main():
    ir_sensor = IRSensor()
    distance_sensor = DistanceSensor()
    i = 0
    while True:
        print(f'{i}|', "object on platform", distance_sensor.check_object())
        print(f'{i}|', "infrared sensor", ir_sensor.check_object())
        time.sleep(1)
        i += 1

if __name__ == "__main__":
    main()

