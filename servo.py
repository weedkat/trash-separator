import RPi.GPIO as GPIO
import time
import asyncio
import numpy as np

class DumpTrashPrototype:
    def __init__(self, door_sensor_pin = 12, top_servo_pin = 16, bottom_servo_pin = 20, mode = 'BCM'):
        try:
            self.DOOR_SENSOR = door_sensor_pin
            self.loop = asyncio.get_event_loop()
            
            # Speed value is between 8 to 12 (slow to fast)
            self.top_servo_duty = {
                'fast_counter' : 1,
                'slow_counter' : 6,
                'fast_clockwise' : 12,
                'slow_clockwise' : 8,
                'very_slow_counter' : 6.7,
                'very_slow_clockwise' : 7.4,
                'stop' : 7,
                }
            
            # Duty angle for bottom servo
            self.bottom_servo_duty = {
                'default' : 6.75,
                'clockwise': 2.8,
                'counter' : 10.49,
                }
            
             # Use BCM GPIO references
            if mode == 'BCM':
                GPIO.setmode(GPIO.BCM)
            elif mode == 'BOARD':
                GPIO.setmode(GPIO.BOARD)
            else:
                raise ValueError(f"Mode '{mode}' is not valid")
            GPIO.setwarnings(False)
            
            # Set door sensor
            GPIO.setup(self.DOOR_SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Set top servo
            GPIO.setup(top_servo_pin, GPIO.OUT)
            self.top_servo = GPIO.PWM(top_servo_pin, 50)
            self.top_servo.start(0)

            # Set bottom servo
            GPIO.setup(bottom_servo_pin, GPIO.OUT)
            self.bottom_servo = GPIO.PWM(bottom_servo_pin, 50)
            self.bottom_servo.start(0)
            
            #self.direction = True
            
            # Time for top servo to complete one turn
            self.time_for_one_spin = self.test_top_servo_one_spin_time()
            print(f"top servo took {self.time_for_one_spin} second for one spin")
            
            asyncio.run(self.top_servo_default_pos())
            
        except:
            print("Something went wrong")
            
        else:
            print("Servo Initialized")
    
    def test_top_servo_one_spin_time(self):
        time1 = time.time()
        asyncio.run(self.top_servo_clockwise())
        time2 = time.time()
        return np.round(time2-time1, 3)

    def check_door_sensor(self):
        # True if circuit closed
        return not GPIO.input(self.DOOR_SENSOR)
    
    def wait_for_default_pos(self, refresh = 0.01, delay = 0.2):
        # Add delay before checking, otherwise, the servo won't turn
        time.sleep(delay)
        while not self.check_door_sensor():
            time.sleep(refresh)

    def soft_stop_top_servo(self):
        stop_duty = self.top_servo_duty['stop']
        #slow_duty = self.top_servo_duty['very_slow_clockwise']
        counter_duty = self.top_servo_duty['slow_counter']
        if not self.direction:
            counter_duty = self.top_servo_duty['slow_clockwise']
            #slow_duty = self.top_servo_duty['very_slow_counter']
        
        #self.top_servo.ChangeDutyCycle(slow_duty)
        #time.sleep(0.01)
            
        self.top_servo.ChangeDutyCycle(stop_duty)
        time.sleep(0.08)
        self.top_servo.ChangeDutyCycle(counter_duty)
        time.sleep(0.02)
    
    def hard_stop_top_servo(self):
        stop_duty = self.top_servo_duty['stop']
        self.top_servo.ChangeDutyCycle(stop_duty)
        time.sleep(0.1)
        
    async def top_servo_clockwise(self, spin_time = 0):
        # Direction True = clockwise, False = counter
        # Set the status of current servo direction
        self.direction = True
        
        fast_duty = self.top_servo_duty['fast_clockwise']
        
        self.spin_top_servo(fast_duty, spin_time = spin_time)
        
    async def top_servo_counter(self, spin_time = 0):
        # Direction True = clockwise, False = counter
        # Set the status of current servo direction
        self.direction = False
        
        fast_duty = self.top_servo_duty['fast_counter']
        
        self.spin_top_servo(fast_duty, spin_time = spin_time)
    
    def spin_top_servo(self, duty, spin_time = 0):
        # Spin top servo
        self.top_servo.ChangeDutyCycle(duty)
        
        # Spin as long as spin_time
        time.sleep(spin_time)
            
        # If no spin_time then wait until door sensor circuit's closed
        if spin_time == 0:
            self.wait_for_default_pos()
        
        # Use soft stop because fast spin
        self.soft_stop_top_servo()
        
    async def top_servo_default_pos(self, n_recursion = 0, direction = None):
        # Set servo to default position
        if(self.check_door_sensor()):
            # If servo already in default position then return.
            self.direction = direction or True # for consistency
            return None
        
        # Counter the current servo direction
        slow_duty = self.top_servo_duty['very_slow_clockwise']
        very_slow_duty = self.top_servo_duty['very_slow_clockwise']
        
        if self.direction:
            slow_duty = self.top_servo_duty['slow_counter']
            very_slow_duty = self.top_servo_duty['very_slow_counter']
         
        self.top_servo.ChangeDutyCycle(very_slow_duty)
        
        # For faster return to default position
        if n_recursion < 1:
            self.top_servo.ChangeDutyCycle(slow_duty)
            
        # Delay 0 asumming the servo currently not in range for door sensor
        self.wait_for_default_pos(delay = 0)
        
        # Because slow speed
        self.hard_stop_top_servo()
        
        # Flip direction in case the servo overshoot the default position
        self.direction = not self.direction
        
        return await self.top_servo_default_pos(n_recursion = n_recursion + 1)

    async def bottom_servo_default_pos(self, spin_time = 2):
        self.bottom_servo.ChangeDutyCycle(self.bottom_servo_duty['default'])
        await asyncio.sleep(spin_time)
    
    async def bottom_servo_clockwise_pos(self, spin_time = 2):
        self.bottom_servo.ChangeDutyCycle(self.bottom_servo_duty['clockwise'])
        await asyncio.sleep(spin_time)
        
    async def bottom_servo_counter_pos(self, spin_time = 2):
        self.bottom_servo.ChangeDutyCycle(self.bottom_servo_duty['counter'])
        await asyncio.sleep(spin_time)
    
    async def servo_default_pos(self):
        tasks = [self.bottom_servo_default_pos(), self.top_servo_default_pos()]
        await asyncio.gather(*tasks)
        await self.top_servo_default_pos()
     
    async def _dump_trash_front(self):
        pass
        
    async def _dump_trash_front_left(self):
        pass
    
    
    # Work around so asynchronous function can run synchronously (normal)
    def dump_trash_front(self):
        return self.loop.run_until_complete(self._dump_trash_front())
    
    def dump_trash_front_left(self):
        return self.loop.run_until_complete(self._dump_trash_front_left())
    
    def shutdown_servo(self):
        self.top_servo.stop()
        self.bottom_servo.stop()
'''
        *  *
     * bl  br *
    *          *
    * fl    fr *
     *    f   *
        *  *
    Trash Dumping Position
'''
def main():
    prototype_trash = DumpTrashPrototype()
    prototype_trash.dump_trash_front()
    prototype_trash.dump_trash_front_left()
    #prototype_trash.dump_trash_front_left()
    prototype_trash.shutdown_servo()

    
if __name__ == "__main__":
    main()