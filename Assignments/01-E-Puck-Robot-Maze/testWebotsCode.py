from controller import Robot, Motor

TIME_STEP = 64

# create the Robot instance.
robot = Robot()
print("Starting")

# get the motor devices
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
# set the target position of the motors
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))
rightMotor.setVelocity(0.0)
leftMotor.setVelocity(0.5)
compass = robot.getDevice("compass")
compass.enable(TIME_STEP)
leftE = robot.getDevice("left wheel sensor")
leftE.enable(TIME_STEP)


while robot.step(TIME_STEP) != -1:
    answer = compass.getValues()
    
    import math
    if not math.isnan(answer[0]):
        #print(answer)
        
        angle = (math.atan2(answer[0], answer[1]))
        #print(angle)
        if angle < .77 and angle > -.82:
            print("West")
        elif angle < -0.82 and angle > -2.4:
            print("North")
        elif angle < -2.41 or angle > 2.44 :
            print("East")
        else:
            print("South")
        
    else:
        print("Not")

    print(leftE.getValue())
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()

    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass

# Enter here exit cleanup code.
