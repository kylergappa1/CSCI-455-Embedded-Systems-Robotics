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
rightMotor.setVelocity(6.0)
leftMotor.setVelocity(6.0)

compass = robot.getDevice("compass")
compass.enable(TIME_STEP)

touch = robot.getDevice("touch sensor")
touch.enable(TIME_STEP)

while robot.step(TIME_STEP) >= 0:
    touched = touch.getValue()
    if touch.getValue() > 0:
        break
