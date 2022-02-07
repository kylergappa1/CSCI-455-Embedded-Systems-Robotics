
from controller import Robot, Motor, TouchSensor, DistanceSensor
import math
from enum import Enum
from os import system as osSystem, name as osName
import types

# define our clear function
def clear():
    # for windows
    if osName == 'nt':
        _ = osSystem('cls')
  
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = osSystem('clear')


class Direction(Enum):
    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'
    Left = 'Left'
    Right = 'Right'


MAX_SPEED = 6.28
psNames = ['ps0', 'ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7']
FAST_TURN_BUFFER_CUSION = 5
SLOW_TURN_BUFFER_CUSION = 0.5
FAST_TURNING_VELOCITY = 2.0
SLOW_TURNING_VELOCITY = 0.1
PS_SENSITIVITY = 1000


def adjustBearing(bearing):
    if bearing > 360:
        bearing -= 360
    elif bearing < 0:
        bearing += 360
    return bearing

def poleBearing(direction):
    if direction == Direction.North:
        return 0.00
    elif direction == Direction.South:
        return 180.00
    elif direction == Direction.East:
        return 270.00
    elif direction == Direction.West:
        return 90.00

class MyRobot:

    robot = None
    timestep = 64
    timestep_count = 0
    ps = []
    leftMotor = None
    rightMotor = None
    compass = None
    
    traveling_direction = None
    found_wall = False
    # found_wall = True

    def __init__(self, robot, timestep):
        self.robot = robot
        self.timestep = timestep

        for i in psNames:
            sensor = robot.getDevice(i)
            sensor.enable(timestep)
            self.ps.append(sensor)
        # Setup left and right motors
        leftMotor = robot.getDevice('left wheel motor')
        rightMotor = robot.getDevice('right wheel motor')

        leftMotor.setVelocity(0.0)
        rightMotor.setVelocity(0.0)

        leftMotor.setPosition(float('inf'))
        rightMotor.setPosition(float('inf'))

        self.leftMotor = leftMotor
        self.rightMotor = rightMotor

        # self.touch = self.robot.getDevice('touch sensor')
        # self.touch.enable(self.timestep)

        # Setup Compass
        compass = robot.getDevice('compass')
        compass.enable(timestep)
        self.compass = compass

        for i in range(8):
            self.ps.append(robot.getDevice(psNames[i]))
            self.ps[i].enable(timestep)

        self.current_instructions = 'find wall'

        if self.step():
            self.traveling_direction = self.direction

    def step(self):
        if self.robot.step(self.timestep) != -1:
            self.timestep_count += 1
            return True
        else:
            return False

    def stop(self):
        self.leftMotor.setVelocity(0.0)
        self.rightMotor.setVelocity(0.0)

    @property
    def bearing(self):
        dir = self.compass.getValues()
        rad = math.atan2(dir[0], dir[1])
        bearing = (rad - 1.5708) / math.pi * 180.0
        if bearing < 0.0:
            bearing = bearing + 360.0
        return bearing

    @property
    def direction(self):
        bearing = self.bearing
        if bearing < 315 and bearing > 225:
            return Direction.East
        elif bearing < 225 and bearing > (135):
            return Direction.South
        elif bearing < 135 and bearing > 45:
            return Direction.West
        else:
            return Direction.North
    
    def psValue(self, sensor_num):
        return self.ps[sensor_num].getValue()

    @property
    def ps0(self):
        return self.psValue(0)
    @property
    def ps1(self):
        return self.psValue(1)
    @property
    def ps2(self):
        return self.psValue(2)
    @property
    def ps3(self):
        return self.psValue(3)
    @property
    def ps4(self):
        return self.psValue(4)
    @property
    def ps5(self):
        return self.psValue(5)
    @property
    def ps6(self):
        return self.psValue(6)
    @property
    def ps7(self):
        return self.psValue(7)

    def setSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.leftMotor.setVelocity(speed)
        self.rightMotor.setVelocity(speed)

    def setLeftWheelSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.leftMotor.setVelocity(speed)

    def setRightWheelSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.rightMotor.setVelocity(speed)

    def _setTurnVelocity(self, dir, speed):
        if dir == Direction.Left:
            self.leftMotor.setVelocity(-speed)
            self.rightMotor.setVelocity(speed)
        elif dir == Direction.Right:
            self.leftMotor.setVelocity(speed)
            self.rightMotor.setVelocity(-speed)

    def faceNorth(self):
        bearing = self.bearing
        turningDirection = Direction.Right
        if bearing > 180:
            turningDirection = Direction.Left
        turnFast = False
        if turningDirection == Direction.Left and bearing < 360 - FAST_TURN_BUFFER_CUSION:
            turnFast = True
        elif turningDirection == Direction.Right and bearing > 0 + FAST_TURN_BUFFER_CUSION:
            turnFast = True
        if turnFast:
            while self.step() != -1:
                bearing = self.bearing
                # print(bearing)
                self._setTurnVelocity(turningDirection, FAST_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 360 - FAST_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 0 + FAST_TURN_BUFFER_CUSION:
                    break
            # self.stop()
            # self.step()
        turnSlow = False
        if turningDirection == Direction.Left and bearing < 360 - SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        elif turningDirection == Direction.Right and bearing > 0 + SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        if turnSlow:
            while self.step() != -1:
                bearing = self.bearing
                # print(bearing)
                self._setTurnVelocity(turningDirection, SLOW_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 360 - SLOW_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 0 + SLOW_TURN_BUFFER_CUSION:
                    break
        self.stop()
        self.step()
        # print(bearing)

    def faceSouth(self):
        bearing = self.bearing
        turningDirection = Direction.Right
        if bearing < 180:
            turningDirection = Direction.Left
        turnFast = False
        if turningDirection == Direction.Left and bearing < 180 - FAST_TURN_BUFFER_CUSION:
            turnFast = True
        elif turningDirection == Direction.Right and bearing > 180 + FAST_TURN_BUFFER_CUSION:
            turnFast = True
        if turnFast:
            while self.step() != -1:
                bearing = self.bearing
                # print(bearing)
                self._setTurnVelocity(turningDirection, FAST_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 180 - FAST_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 180 + FAST_TURN_BUFFER_CUSION:
                    break
            # self.stop()
            # self.step()
        turnSlow = False
        if turningDirection == Direction.Left and bearing < 180 - SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        elif turningDirection == Direction.Right and bearing > 180 + SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        if turnSlow:
            while self.step() != -1:
                bearing = self.bearing
                # print(bearing)
                self._setTurnVelocity(turningDirection, SLOW_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 180 - SLOW_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 180 + SLOW_TURN_BUFFER_CUSION:
                    break
        self.stop()
        self.step()
        # print(bearing)
    
    def faceEast(self):
        bearing = self.bearing
        turningDirection = Direction.Right
        if bearing < 270 and bearing > 90:
            turningDirection = Direction.Left
        turnFast = False
        if turningDirection == Direction.Left and bearing > 90 and bearing < 270 - FAST_TURN_BUFFER_CUSION:
            turnFast = True
        elif turningDirection == Direction.Right and (bearing < 90 or bearing > 270 + FAST_TURN_BUFFER_CUSION):
            turnFast = True
        if turnFast:
            while self.step() != -1:
                bearing = self.bearing
                # print(bearing)
                self._setTurnVelocity(turningDirection, FAST_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 270 - FAST_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 270 + FAST_TURN_BUFFER_CUSION and bearing > 270:
                    break
            # self.stop()
            # self.step()
        turnSlow = False
        if turningDirection == Direction.Left and bearing < 270 - SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        elif turningDirection == Direction.Right and bearing > 270 + SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        if turnSlow:
            while self.step() != -1:
                bearing = self.bearing
                print(bearing)
                self._setTurnVelocity(turningDirection, SLOW_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 270 - SLOW_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 270 + SLOW_TURN_BUFFER_CUSION:
                    break
        self.stop()
        self.step()
        # print(bearing)

    def faceWest(self):
        bearing = self.bearing
        turningDirection = Direction.Right
        if bearing < 90 or bearing > 270:
            turningDirection = Direction.Left
        turnFast = False
        if turningDirection == Direction.Right and bearing > 90 + FAST_TURN_BUFFER_CUSION:
            turnFast = True
        elif turningDirection == Direction.Left and (bearing > 270 or bearing < 90 - FAST_TURN_BUFFER_CUSION):
            turnFast = True
        if turnFast:
            while self.step() != -1:
                bearing = self.bearing
                # print(bearing)
                self._setTurnVelocity(turningDirection, FAST_TURNING_VELOCITY)
                if turningDirection == Direction.Right and bearing < 90 + FAST_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Left and bearing < 90 and bearing > 90 - FAST_TURN_BUFFER_CUSION:
                    break
            # self.stop()
            # self.step()
        turnSlow = False
        if turningDirection == Direction.Left and bearing < 90 and bearing < 90 - SLOW_TURN_BUFFER_CUSION:
            turnSlow = True
        elif turningDirection == Direction.Right and bearing > 90 + SLOW_TURN_BUFFER_CUSION and bearing < 270:
            turnSlow = True
        if turnSlow:
            while self.step() != -1:
                bearing = self.bearing
                print(bearing)
                self._setTurnVelocity(turningDirection, SLOW_TURNING_VELOCITY)
                if turningDirection == Direction.Left and bearing > 90 - SLOW_TURN_BUFFER_CUSION:
                    break
                elif turningDirection == Direction.Right and bearing < 90 + SLOW_TURN_BUFFER_CUSION:
                    break
        self.stop()
        self.step()
        # print(bearing)

class EPuck(MyRobot):

    running = True
    wall_ending = False

    def run(self):
        self.setSpeed(50)
        while self.step() > 0 and self.running:
            self.travel()
    
    def travel(self):

        print(self.bearing)
        self.showRightSensors()

        if self.ps0 > PS_SENSITIVITY and self.ps7 > PS_SENSITIVITY:
            self.found_wall = True
            self.stop()
            self.mountWall()
            self.setSpeed(50)
            print(self)

        if self.found_wall:
            # self.showRightSensors()
            if self.ps2 < 500 and self.ps1 < 200:
                # self.setLeftWheelSpeed(40)
                self.setRightWheelSpeed(1)
                return

            self.setSpeed(50)

    def mountWall(self):
        dir = self.direction
        if dir == Direction.North:
            self.faceWest()
        elif dir == Direction.South:
            self.faceEast()
        elif dir == Direction.East:
            self.faceNorth()
        elif dir == Direction.West:
            self.faceSouth()

    def showRightSensors(self):
        print("ps0: {:.4f} - ps1: {:.4f} - ps2: {:.4f} - ps3: {:.4f}".format(self.ps0, self.ps1, self.ps2, self.ps3))

    def __str__(self):
        str = "{!s:-^40}\n"
        str += "{!s:<20}{!s} - ({:.2f})\n"
        str += "{!s:<20}{!s}\n"
        str += "{!s:<20}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:>5}:{:>23f}\n"
        str += "{!s:-^40}"
        return str.format(
            'Robot',
            'Direction:', self.traveling_direction.name, self.bearing,
            'Timestep Count:', self.timestep_count,
            'Sensors:',
            'ps0', self.ps0,
            'ps1', self.ps1,
            'ps2', self.ps2,
            'ps3', self.ps3,
            'ps4', self.ps4,
            'ps5', self.ps5,
            'ps6', self.ps6,
            'ps7', self.ps7,
            '')

clear()
print("Starting")
robot = Robot()
timestep = int(robot.getBasicTimeStep())

ePuck = EPuck(robot, timestep)
ePuck.run()
print(ePuck)
# robot.faceNorth()
# robot.faceNorth()
# robot.faceEast()
# robot.faceNorth()
# robot.faceWest()
# while robot.step() != -1:
    # print(robot.bearing)
# robot.faceSouth()
# robot.faceEast()
# robot.faceNorth()
# print(robot.bearing)
# robot.faceWest()
# print(robot.bearing)
# print(robot.direction)
# print(robot.bearing)
# robot.turn('left')
# robot.turn('right')
# robot.run()





# get the motor devices
# leftMotor = robot.getDevice('left wheel motor')
# rightMotor = robot.getDevice('right wheel motor')

# set the target position of the motors
# we want the motors to continue to run forever
# leftMotor.setPosition(float('inf'))
# rightMotor.setPosition(float('inf'))

# leftMotor.setVelocity(0.0)
# rightMotor.setVelocity(0.0)


# touch = robot.getDevice('touch sensor')
# touch.enable(timestep)

# compass = robot.getDevice('compass')
# compass.enable(timestep)

# leftE = robot.getDevice('left wheel sensor')
# leftE.enable(timestep)

# while robot.step(timestep) != -1:
#     if(touch.getValue() > 0):
#         break
#     leftMotor.setVelocity(MAX_SPEED * 0.5)
#     rightMotor.setVelocity(MAX_SPEED * 0.5)

# set up the motor speeds at 10% of the MAX_SPEED.
# leftMotor.setVelocity(0.1 * MAX_SPEED)
# rightMotor.setVelocity(0.1 * MAX_SPEED)


# def compassValues():
#     answer = compass.getValues()
#     if math.isnan(answer[0]):
#         print("Compass isnan")
#         return
#     angle = math.atan2(answer[0], answer[1])
#     # angle = (int(math.atan2(answer[0], answer[2]) * 100))
#     print(angle)

#     if angle < 0.77 and angle > -0.82:
#         print("West")
#     elif angle < -0.82 and angle > -2.4:
#         print("North")
#     elif angle < -2.41 and angle > 2.44:
#         print("East")
#     else:
#         print("South")




    # leftMotor.setVelocity(MAX_SPEED)
    # leftMotor.setVelocity(1)
    # rightMotor.setVelocity(MAX_SPEED)

    # print(leftE.getValue())

    # print("{:.2f} - {:.2f}".format(ps[0].getValue(), ps[7].getValue()))

    # if ps[0].getValue() > 100 or ps[7].getValue() > 100:
        # break
    # print(leftE.getValue())
    # compassValues()
    # print(compass.getValues())

    # if touch.getValue() > 0:
    #     break
