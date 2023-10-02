import RPi.GPIO as GPIO
import time
import asyncio

class DumpTrash:
    def __init__(self, door_sensor_pin = 12, top_servo_pin = 16, bottom_servo_pin = 20, mode = 'BCM'):
        try:
            self.DOOR_SENSOR = door_sensor_pin
            self.loop = asyncio.get_event_loop()
            
            # Speed settings for top servo
            self.top_servo_duty = {
                'fast_counter' : 1,
                'slow_counter' : 6.2,
                'fast_clockwise' : 12,
                'slow_clockwise' : 7.8,
                'very_slow_counter' : 6.78,
                'very_slow_clockwise' : 7.43,
                'stop' : 7.0,
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
            
            # Set default current top servo duty information
            self.current_top_servo_duty = self.top_servo_duty['stop']
            
            #self.loop.run_until_complete(self.top_servo_clockwise(spin_time = 120))
            
            # If top servo does't come back for n second, assume it is stuck
            self.stuck_time = 5.0
            
            # Set all servo to default positions
            self.loop.run_until_complete(self.bottom_servo_default_pos())
            self.loop.run_until_complete(self.top_servo_default_pos())
            
        except:
            # Not very helpful, sorry :(
            print("Something went wrong")
            
        else:
            print("Servo Initialized")
    
    def change_duty_top_servo(self, duty):
        
        self.current_top_servo_duty = duty
        
        if duty == self.top_servo_duty['stop']:
            self.top_servo.ChangeDutyCycle(0)
        else:
            self.top_servo.ChangeDutyCycle(duty)

    def check_door_sensor(self):
        # True if circuit closed
        return not GPIO.input(self.DOOR_SENSOR)
    
    def wait_for_default_pos(self, refresh = 0.01, delay = 0.0):
        # Add delay before checking, otherwise, the servo won't turn
        time.sleep(delay)
        max_iter = self.stuck_time / refresh
        i = 0
        while not self.check_door_sensor() and i < max_iter:
            time.sleep(refresh)
            i += 1
  
        # Top servo stuck
        if i >= max_iter:
            self.unstuck_top_servo()
            
    def soft_stop_top_servo(self):
        stop_duty = self.top_servo_duty['stop']
        
        # If servo going clockwise, then counter, vice versa
        counter_duty = self.top_servo_duty['slow_counter']
        if self.current_top_servo_duty < stop_duty:
            counter_duty = self.top_servo_duty['slow_clockwise']
        
        # Stop > counter > stop
        self.change_duty_top_servo(stop_duty)
        time.sleep(0.07)
        self.change_duty_top_servo(counter_duty)
        time.sleep(0.02)
        self.change_duty_top_servo(stop_duty)
        time.sleep(0.01)
    
    def hard_stop_top_servo(self):
        stop_duty = self.top_servo_duty['stop']
        self.change_duty_top_servo(stop_duty)
        time.sleep(0.1)
        
    async def top_servo_clockwise(self, spin_time = 0.2, mode = 'fast'):
        # Select top servo clockise spin speed mode
        duty = 0.0
        
        if mode == 'fast':
            duty = self.top_servo_duty['fast_clockwise']
        elif mode == 'slow':
            duty = self.top_servo_duty['slow_clockwise']
        elif mode == 'very_slow':
            duty = self.top_servo_duty['very_slow_clockwise']
        else:
            raise ValueError(f'Mode {mode} is not available')
        
        return self.spin_top_servo(duty, spin_time = spin_time)
        
    async def top_servo_counter(self, spin_time = 0.2, mode = 'fast'):
        # Select top servo counter spin speed mode
        duty = 0.0
        
        if mode == 'fast':
            duty = self.top_servo_duty['fast_counter']
        elif mode == 'slow':
            duty = self.top_servo_duty['slow_counter']
        elif mode == 'very_slow':
            duty = self.top_servo_duty['very_slow_counter']
            self.direction = True
        else:
            raise ValueError(f'Mode {mode} is not available')
        
        return self.spin_top_servo(duty, spin_time = spin_time)
    
    def spin_top_servo(self, duty, spin_time = 0):
        # Spin top servo
        self.change_duty_top_servo(duty)
        
        # Spin as long as spin_time
        time.sleep(spin_time)
            
        self.wait_for_default_pos()
        
        # Use soft stop while spinning fast
        '''
        if duty < self.top_servo_duty['fast_counter'] or duty > self.top_servo_duty['fast_clockwise']:
            self.soft_stop_top_servo()
        else:
            self.hard_stop_top_servo()
        '''
    
    async def top_servo_default_pos(self, n_recursion = 0):
        # Set servo to default position
        if(self.check_door_sensor()):
            # Check twice wether the top servo is in default position.
            self.temp_duty = self.current_top_servo_duty
            self.hard_stop_top_servo()
            if(self.check_door_sensor()):
                #print('ready')
                return True
            self.current_top_servo_duty = self.temp_duty
        
        # Counter the current servo direction
        stop_duty = self.top_servo_duty['stop']
        slow_duty = self.top_servo_duty['slow_clockwise']
        very_slow_duty = self.top_servo_duty['very_slow_clockwise']
        
        if self.current_top_servo_duty >= stop_duty:
            slow_duty = self.top_servo_duty['slow_counter']
            very_slow_duty = self.top_servo_duty['very_slow_counter']
         
        # For faster return to default position
        if n_recursion < 1:
            self.change_duty_top_servo(slow_duty)
        else:
            self.change_duty_top_servo(very_slow_duty)
            
        # Delay 0 asumming the servo currently not in range of door sensor
        self.wait_for_default_pos(delay = 0)
        
        # Recursive
        await self.top_servo_default_pos(n_recursion = n_recursion + 1)

    async def bottom_servo_default_pos(self, spin_time = 2):
        self.bottom_servo.ChangeDutyCycle(self.bottom_servo_duty['default'])
        await asyncio.sleep(spin_time)
        self.bottom_servo.ChangeDutyCycle(0)
        
    async def bottom_servo_clockwise_pos(self, spin_time = 2):
        self.bottom_servo.ChangeDutyCycle(self.bottom_servo_duty['clockwise'])
        await asyncio.sleep(spin_time)
        self.bottom_servo.ChangeDutyCycle(0)
        
    async def bottom_servo_counter_pos(self, spin_time = 2):
        self.bottom_servo.ChangeDutyCycle(self.bottom_servo_duty['counter'])
        await asyncio.sleep(spin_time)
        self.bottom_servo.ChangeDutyCycle(0)
    
    async def servo_default_pos(self):
        tasks = [self.bottom_servo_default_pos(), self.top_servo_default_pos()]
        await asyncio.gather(*tasks)
        await self.top_servo_default_pos()
     
    async def _dump_trash_front(self):
        # To hold trash
        async def hold_top_servo():
            await asyncio.sleep(1)
            if not self.check_door_sensor():
                await self.top_servo_counter(mode = 'slow')
        
        tasks = [self.bottom_servo_clockwise_pos(), hold_top_servo()]
        await asyncio.gather(*tasks)
        await self.servo_default_pos()
        
    async def _dump_trash_front_left(self):
        tasks = [self.bottom_servo_counter_pos(), self.top_servo_clockwise(mode = 'slow')]
        await asyncio.gather(*tasks)
        await self.servo_default_pos()
    
    async def _dump_trash_front_right(self):
        await self.top_servo_counter(mode = 'slow')
        await self.top_servo_default_pos()
    
    async def _dump_trash_back_left(self):
        await self.top_servo_clockwise(mode = 'slow')
        await self.top_servo_default_pos()
    
    async def _dump_trash_back_right(self):
        tasks = [self.bottom_servo_counter_pos(), self.top_servo_counter(mode = 'slow')]
        await asyncio.gather(*tasks)
        await self.servo_default_pos()
    
    def unstuck_top_servo(self):
        stop_duty = self.top_servo_duty['stop']
        slow_counter_duty = self.top_servo_duty['slow_clockwise']
        fast_duty = self.top_servo_duty['fast_counter']
        current_duty = self.current_top_servo_duty
        
        if current_duty >= stop_duty:
            slow_counter_duty = self.top_servo_duty['slow_counter']
            fast_duty = self.top_servo_duty['fast_clockwise']
        
        self.change_duty_top_servo(slow_counter_duty)
        time.sleep(0.4)
        self.change_duty_top_servo(fast_duty)
        time.sleep(1)
               
    # Work around so asynchronous function can be called synchronously (normal)
    def dump_trash_front(self):
        return self.loop.run_until_complete(self._dump_trash_front())
    
    def dump_trash_front_left(self):
        return self.loop.run_until_complete(self._dump_trash_front_left())
    
    def dump_trash_front_right(self):
        return self.loop.run_until_complete(self._dump_trash_front_right())
    
    def dump_trash_back_left(self):
        return self.loop.run_until_complete(self._dump_trash_back_left())
    
    def dump_trash_back_right(self):
        return self.loop.run_until_complete(self._dump_trash_back_right())
    
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
    prototype_trash = DumpTrash()
    time.sleep(5)
    #prototype_trash.dump_trash_front()
    prototype_trash.dump_trash_front_left()
    #prototype_trash.dump_trash_front_right()
    #prototype_trash.dump_trash_back_left()
    #prototype_trash.dump_trash_back_right()
    prototype_trash.shutdown_servo()

    
if __name__ == "__main__":
    main()