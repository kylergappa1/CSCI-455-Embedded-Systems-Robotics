# maze.py

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

class RobotStates(Enum):
    FindWall = 'Find Wall'
    FollowWall = 'Follow Wall'


MAX_SPEED = 6.28
psNames = ['ps0', 'ps1', 'ps2', 'ps3', 'ps4', 'ps5', 'ps6', 'ps7']
FAST_TURN_BUFFER_CUSION = 15
SLOW_TURN_BUFFER_CUSION = 0.5
FAST_TURNING_VELOCITY = 2
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

class EPuck:

    robot = None
    timestep = 64
    timestep_count = 0
    ps = []
    leftMotor = None
    rightMotor = None
    leftMotorSensor = None
    rightMotorSensor = None
    compass = None
    
    running = True
    state = None #

    last_direction = None

    # traveling_direction = None
    # found_wall = True


    def __init__(self):
        robot = Robot()
        self.robot = robot

        timestep = int(robot.getBasicTimeStep())
        timestep = 64
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

        leftMotorSensor = robot.getDevice('left wheel sensor')
        rightMotorSensor = robot.getDevice('left wheel sensor')

        leftMotorSensor.enable(timestep)
        rightMotorSensor.enable(timestep)

        self.leftMotorSensor = leftMotorSensor
        self.rightMotorSensor = rightMotorSensor

        # self.touch = self.robot.getDevice('touch sensor')
        # self.touch.enable(self.timestep)

        # Setup Compass
        compass = robot.getDevice('compass')
        compass.enable(timestep)
        self.compass = compass

        for i in range(8):
            self.ps.append(robot.getDevice(psNames[i]))
            self.ps[i].enable(timestep)

        self.state = RobotStates.FindWall


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
        elif turningDirection == Direction.Right and bearing > 0 + SLOW_TURN_BUFFER_CUSION and bearing < 90:
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

    def run(self):
        # self.setSpeed(50)
        while self.step() and self.running:
            self.travel()
    
    def travel(self):

        if self.last_direction is None:
            self.last_direction = self.direction
        
        
        # print(self.bearing)
        # self.showRightSensors()

        if self.ps0 > PS_SENSITIVITY and self.ps7 > PS_SENSITIVITY:
            # self.found_wall = True
            self.stop()
            self.mountWall()
            self.last_direction = self.direction
            self.state = RobotStates.FollowWall
            # self.setSpeed(50)
            print(self)
            return

        if self.state == RobotStates.FollowWall:
            self.showRightSensors()
            if self.ps2 < 200:
                self.rightTurn()
                return
                # start = self.leftMotorSensor.getValue()
                # while self.step():
                #     if self.leftMotorSensor.getValue() - start > 1.65:
                #         self.faceEast()
                #         self.setSpeed(50)
                #         start = self.leftMotorSensor.getValue()
                #         while self.step():
                #             if self.leftMotorSensor.getValue() - start > 4:
                #                 self.showRightSensors()
                #                 self.running = False
                #                 return

            # print(self.leftMotorSensor.getValue())
            pass
            # self.showRightSensors()
            # if self.ps2 < 500 and self.ps1 < 200:
            #     self.setLeftWheelSpeed(50)
            #     self.setRightWheelSpeed(-10)
            #     if self.last_direction is not self.direction:
            #         self.faceEast()
            #     return
                # return
                # print('Lost Wall')
                # return
            # self.showRightSensors()
            # if self.ps2 < 500 and self.ps1 < 200:
            #     # self.setLeftWheelSpeed(40)
            #     self.setRightWheelSpeed(1)
            #     return
        self.setSpeed(100)

    def rightTurn(self):
        self.setSpeed(70)
        start = self.leftMotorSensor.getValue()
        while self.step():
            if self.leftMotorSensor.getValue() - start > 1.7:
                break
        if self.direction == Direction.North:
            self.faceEast()
        elif self.direction == Direction.East:
            self.faceSouth()
        elif self.direction == Direction.South:
            self.faceWest()
        else:
            self.faceNorth()
        self.setSpeed(100)
        while self.step():
            if self.ps2 > 200:
                return


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
            'Direction:', self.direction.name, self.bearing,
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
ePuck = EPuck()
ePuck.run()
print(ePuck)
# robot.faceNorth()
# robot.faceEast()
# robot.faceNorth()
# robot.faceWest()

# touch = robot.getDevice('touch sensor')
# touch.enable(timestep)

# END