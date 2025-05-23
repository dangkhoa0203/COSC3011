import time, event, cyberpi, mbot2, mbuild


def obstacle_detected(base_power):
    if mbuild.ultrasonic2.get(1) < 15:
        mbot2.EM_stop("all")
        cyberpi.console.println("Obstacle detected!")
        start_time = time.time()

        while True:
            if mbuild.ultrasonic2.get(1) > 15:
                break

            if time.time() - start_time > 5:
                mbot2.backward(50, 0.5)
                time.sleep(1.2)
                mbot2.turn(180, base_power)
                break

def red_dectected(base_power ,left_power, right_power):
    if mbuild.quad_rgb_sensor.is_color("red", "any"):
        mbot2.EM_stop("all")
        mbot2.backward(50, 0.5)
        cyberpi.led.show("red red red red red")
        cyberpi.console.println("Red detected - stopping")
        cyberpi.console.println("Waiting for green...")
        cyberpi.console.println("U turn after 10 seconds")
        start_time = time.time()

        while True:
            if time.time() - start_time > 10:
                mbot2.turn(180, base_power)
                break

            if mbuild.quad_rgb_sensor.is_color("green", "any"):
                mbot2.EM_stop("all")
                cyberpi.console.println("Green detected - resuming")
                # Call green_detected here
                green_detected(kp, left_power, right_power)
                break

            time.sleep(0.1)


def yellow_detected(left_power, right_power):
    if mbuild.quad_rgb_sensor.is_color("yellow", "any"):
        # Store original power
        original_left = left_power
        original_right = right_power

        # Slow down
        left_power = left_power / 2
        right_power = right_power / 2
        cyberpi.led.show("yellow yellow yellow yellow yellow")
        cyberpi.console.println("Yellow detected - slowing down")
        start_time = time.time()

        # Maintain slow speed for 5 seconds
        while time.time() - start_time < 5:
            mbot2.drive_power(right_power, left_power)
            time.sleep(0.1)

        # Restore original power
        left_power = original_left
        right_power = original_right
        mbot2.drive_power(right_power, left_power)

def green_detected(left_power, right_power):
    global kp  
    if mbuild.quad_rgb_sensor.is_color("green", "any"):
        original_left = left_power
        original_right = right_power
        original_kp = kp  # Save the original kp

        left_power = left_power * 1.5
        right_power = right_power * 1.5
        kp = kp / 1.5  # Reduce kp
        cyberpi.led.show("green green green green green")
        cyberpi.console.println("Green detected")
        start_time = time.time()

        while time.time() - start_time < 5:
            mbot2.drive_power(right_power, left_power)
            time.sleep(0.1)

        # Restore original power and kp
        left_power = original_left
        right_power = original_right
        kp = original_kp  # Restore kp
        mbot2.drive_power(right_power, left_power)
            

def black_detected(base_power, kp, left_power, right_power):
    if mbuild.quad_rgb_sensor.is_color("black", "L2"):
            cyberpi.led.show("black black black black black")
            offset = mbuild.quad_rgb_sensor.get_offset_track(1)
            right_power = (base_power - kp * offset)
            left_power = -1 * (base_power + kp * offset) * 0.7
            mbot2.drive_power(right_power, left_power)
    if mbuild.quad_rgb_sensor.is_color("black", "R2"):
            cyberpi.led.show("black black black black black")
            offset = mbuild.quad_rgb_sensor.get_offset_track(1)
            right_power = (base_power - kp * offset) * 0.7
            left_power = -1 * (base_power + kp * offset)
            mbot2.drive_power(right_power, left_power)        
            
    
def follow_line():
    global base_power, kp, left_power, right_power
    base_power = 30
    kp = base_power / 100
    

    while True:
        obstacle_detected(base_power)
        red_dectected(base_power, left_power, right_power)
        yellow_detected(left_power, right_power)
        green_detected(left_power, right_power)
        black_detected(base_power, kp, left_power, right_power)
        

        if mbuild.quad_rgb_sensor.is_color("white", "any"):
            offset = mbuild.quad_rgb_sensor.get_offset_track(1)
            right_power = (base_power - kp * offset)
            left_power = -1 * (base_power + kp * offset)
            mbot2.drive_power(right_power, left_power)
            

def color_checking():
    cyberpi.stop_other()
    mbot2.drive_power(0, 0)
    while not cyberpi.controller.is_press("a"):
        # Show colors from sensors for debugging
        l1_color = mbuild.quad_rgb_sensor.get_color_sta("L1", 1)
        l2_color = mbuild.quad_rgb_sensor.get_color_sta("L2", 1)
        r1_color = mbuild.quad_rgb_sensor.get_color_sta("R1", 1)
        r2_color = mbuild.quad_rgb_sensor.get_color_sta("R2", 1)

        cyberpi.console.clear()
        cyberpi.console.println(l2_color, l1_color, r1_color, r2_color)
        time.sleep(0.2)

@event.start
def on_start():
    cyberpi.console.set_font(12)
    cyberpi.console.println("Press A to start moving")
    cyberpi.console.println("Press B to stop")
    cyberpi.console.println("Press joystick to check colors")


@event.is_press('a')
def a_pressed():
    follow_line()

@event.is_press('b')
def b_pressed():
    cyberpi.stop_other()
    mbot2.drive_power(0, 0)
    cyberpi.console.println("Stopping all actions")

@event.is_press("middle")
def is_joy_press():
    color_checking()