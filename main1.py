import event, time, cyberpi, mbot2, mbuild

# === Robot Parameters ===
speed_base = 30
kp = 0
motor_left = 0
motor_right = 0

# === Utility Functions ===

def drive_adjust(offset_val, base_speed):
    global motor_left, motor_right
    correction = kp * offset_val
    motor_right = base_speed - correction
    motor_left = base_speed + correction
    motor_left = -motor_left  
    mbot2.drive_power(motor_right, motor_left)


def set_led_color(color_name):
    cyberpi.led.show(color_name * 5)

def print_msg(text):
    cyberpi.console.println(text)

# === Event Triggers ===

@event.start
def on_robot_start():
    cyberpi.console.set_font(12)
    print_msg("Press A: Stop Robot")
    print_msg("Press B: Start Line Following")
    print_msg("Middle Joystick: Color Debug Mode")

@event.is_press('a')
def handle_stop():
    cyberpi.stop_other()
    mbot2.drive_power(0, 0)

@event.is_press('b')
def handle_navigation():
    global speed_base, kp
    cyberpi.stop_other()
    speed_base = 30
    kp = 0.22

    while True:
        # Obstacle detection
        if mbuild.ultrasonic2.get(1) < 15:
            mbot2.EM_stop("all")
            print_msg("Obstacle ahead!")
            timer_start = time.time()
            tone_timer = timer_start
            while time.time() - timer_start <= 10:
                if mbuild.ultrasonic2.get(1) > 15:
                    break
                if time.time() - tone_timer >= 2:
                    cyberpi.audio.play_tone(440, 0.5)
                    tone_timer = time.time()
            else:
                mbot2.turn(180, 20)

        # Red color detected
        if mbuild.quad_rgb_sensor.is_color("red", "any"):
            mbot2.EM_stop("all")
            mbot2.backward(30, 0.5)
            set_led_color("red")
            print_msg("Red signal - paused")
            print_msg("Waiting for green...")

            wait_start = time.time()
            tone_time = wait_start
        
            while True:
                if mbuild.quad_rgb_sensor.is_color("green", "any"):
                    print_msg("Green detected - resuming")
                    
                    # Blink green for 2 seconds
                    blink_start = time.time()
                    cyberpi.audio.play_tone(523, 1.0)
                    while time.time() - blink_start < 3:
                        cyberpi.led.show("green green green green green")
                        time.sleep(0.2)
                        cyberpi.led.off()
                        time.sleep(0.2)


                    mbot2.forward(40, 1.0)
                    break
                if time.time() - wait_start > 10:
                    blink_start = time.time()
                    while time.time() - blink_start < 2:
                        cyberpi.led.show("red red red red red")
                        time.sleep(0.2)
                        cyberpi.led.off()
                        time.sleep(0.2)
                    mbot2.turn(180, 20)
                    break
                if time.time() - tone_time >= 2:
                    
                    cyberpi.audio.play_tone(440, 0.5)
                    tone_time = time.time()
                time.sleep(0.1)

        # Yellow - temporary slowdown
        if mbuild.quad_rgb_sensor.is_color("yellow", "any"):
            mbot2.forward(30, 1.5)
            set_led_color("yellow")
            print_msg("Yellow sign - reducing speed")
            speed_base = 10
            slow_time = time.time()
            tone_time = slow_time
            while time.time() - slow_time < 5:
                
                offset_slow = mbuild.quad_rgb_sensor.get_offset_track(1)
                drive_adjust(offset_slow, speed_base)
                if time.time() - tone_time >= 0.5:
                    cyberpi.audio.play_tone(330, 0.5)
                    tone_time = time.time()
                
                cyberpi.led.show("yellow yellow yellow yellow yellow")
                time.sleep(0.05)
            cyberpi.led.off()
            speed_base = 30

        # White path
        if mbuild.quad_rgb_sensor.is_color("white", "any"):
            offset_now = mbuild.quad_rgb_sensor.get_offset_track(1)
            drive_adjust(offset_now, speed_base)

        # Black line tracking
        if mbuild.quad_rgb_sensor.is_color("black", "L2"):
            offset = mbuild.quad_rgb_sensor.get_offset_track(1)
            correction = kp * offset
            motor_left = (speed_base + correction) * (-0.5)
            motor_right = speed_base - correction 
            mbot2.drive_power(motor_left, motor_right)
        if mbuild.quad_rgb_sensor.is_color("black", "R2"):
            offset = mbuild.quad_rgb_sensor.get_offset_track(1)
            correction = kp * offset
            motor_left = (speed_base + correction) 
            motor_right = (speed_base - correction) * 0.5
            mbot2.drive_power(motor_left, motor_right)
            

        time.sleep(0.05)

@event.is_press("middle")
def color_debug_mode():
    cyberpi.stop_other()
    mbot2.drive_power(0, 0)
    while not cyberpi.controller.is_press("a"):
        cyberpi.console.clear()
        color_left = mbuild.quad_rgb_sensor.get_color_sta("L1", 1)
        color_right = mbuild.quad_rgb_sensor.get_color_sta("R1", 1)
        print_msg(color_left)
        print_msg(color_right)
        time.sleep(0.1)
