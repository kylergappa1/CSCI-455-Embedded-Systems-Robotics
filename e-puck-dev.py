from controller import Robot, Motor, TouchSensor, DistanceSensor
# Import math Library
import math

robot = Robot()
timestep = int(robot.getBasicTimeStep())

leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')

leftMotor.setVelocity(0.0)
rightMotor.setVelocity(0.0)

leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

compass = robot.getDevice('compass')
compass.enable(timestep)

# print(math.pi)
# print(math.pi * 0.25)
# print(math.pi * 0.5)
# print(math.pi * 0.75)


def direction():
    compass_values = compass.getValues()
    rad = math.atan2(compass_values[0], compass_values[1])
    bearing = (rad - 1.5708) / math.pi * 180.0
    if bearing < 0.0:
        bearing = bearing + 360.0
    pole = 'none'
    if bearing < 315 and bearing > 225:
        pole = 'East'
    elif bearing < 225 and bearing > (135):
        pole = 'South'
    elif bearing < 135 and bearing > 45:
        pole = 'West'
    else:
        pole = 'North'
    print(pole, ' - ', bearing)

# direction()

while robot.step(timestep) != -1:
    # leftMotor.setVelocity(0.0)
    # rightMotor.setVelocity(0.0)
    direction()
    leftMotor.setVelocity(0.4)
    rightMotor.setVelocity(-0.4)
    # break
