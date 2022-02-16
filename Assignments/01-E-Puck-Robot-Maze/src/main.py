'''
River Kelly
Kyler Gappa
CSCI-455: Embedded Systems (Robotics)
Assignment 01 - Webots E-Puck Robot Maze
Spring 2022
'''
from controller import Robot
from enum import Enum
import math


class Direction(Enum):
    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'
    Left = 'Left'
    Right = 'Right'


class RobotState(Enum):
    FindWall = 'Find Wall'
    MountWall = 'Mount Wall'
    FollowWall = 'Follow Wall - Right-Hand Rule'
    TurnCorner = 'Turn Corner'
    CorrectTurn = 'CorrectTurn'


TIME_STEP = 64
MAX_SPEED = 6.28


class EPuck:
    # properties
    robot = None
    ps = []
    leftMotor = None
    rightMotor = None
    leftMotorSensor = None
    rightMotorSensor = None
    compass = None
    touchSensor = None

    GameOver = False
    # state = RobotState.FindWall
    state = RobotState.FollowWall

    rightCornerPeak = None

    # constructor
    def __init__(self, robot):
        self.robot = robot

        # get and enable ultrasound sensors
        for i in range(8):
            sensorName = "ps{!s}".format(i)
            sensor = self.robot.getDevice(sensorName)
            sensor.enable(TIME_STEP)
            self.ps.append(sensor)

        # Setup left and right motors
        self.leftMotor = self.robot.getDevice('left wheel motor')
        self.rightMotor = self.robot.getDevice('right wheel motor')
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        self.leftMotor.setVelocity(0.0)
        self.rightMotor.setVelocity(0.0)

        # wheel sensors
        self.leftMotorSensor = self.robot.getDevice('left wheel sensor')
        self.rightMotorSensor = self.robot.getDevice('left wheel sensor')
        self.leftMotorSensor.enable(TIME_STEP)
        self.rightMotorSensor.enable(TIME_STEP)

        # compass
        self.compass = self.robot.getDevice('compass')
        self.compass.enable(TIME_STEP)

        self.setSpeed(50)

        # self.touchSensor = self.robot.getDevice('touch sensor')
        # self.touchSensor.enable(TIME_STEP)

    def step(self):
        if self.robot.step(TIME_STEP) != -1:
            # if self.touchSensor.getValue() > 0:
            #     self.GameOver = True
            return True
        return False

    @property
    def bearing(self):
        dir = self.compass.getValues()
        if math.isnan(dir[0]):
            return None
        rad = math.atan2(dir[0], dir[1])
        bearing = (rad - 1.5708) / math.pi * 180.0
        if bearing < 0.0:
            bearing = bearing + 360.0
        return bearing

    @property
    def direction(self):
        bearing = self.bearing
        if bearing is None:
            return None
        if 45 < bearing <= 135:
            return Direction.West
        elif 135 < bearing <= 225:
            return Direction.South
        elif 225 < bearing <= 315:
            return Direction.East
        else:
            return Direction.North

    # setSpeed()
    # -------------------------------------------
    # Set the robots wheel speed based on a
    # percentage of the MAX_SPEED.
    #
    # Example: self.setSpeed(50)
    # sets wheel velocity to 50% of the MAX_SPEED
    # -------------------------------------------
    def setSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.leftMotor.setVelocity(speed)
        self.rightMotor.setVelocity(speed)

    # setLeftWheelSpeed()
    def setLeftWheelSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.leftMotor.setVelocity(speed)

    # setRightWheelSpeed()
    def setRightWheelSpeed(self, speed):
        speed = MAX_SPEED * (speed / 100)
        self.rightMotor.setVelocity(speed)

    def __str__(self):
        str = "{!s:-^40}\n"
        str += "{!s:<20}{!s} - ({:.2f})\n"
        str += "{!s:-^40}"
        return str.format(
            'Robot',
            'Direction:', self.direction.name, self.bearing,
            '')

    def travel(self):
        front_left = self.ps[7].getValue()
        front_right = self.ps[0].getValue()
        right_corner = self.ps[1].getValue()
        right_side = self.ps[2].getValue()

        # l_speed = MAX_SPEED
        # r_speed = MAX_SPEED

        print("front_left: {:.2f} - front_right: {:.2f} - right_corner: {:.2f} - right_side: {:.2f}".format(front_left, front_right, right_corner, right_side))

        # ------------------------------------------------------------
        # Find Wall
        # ------------------------------------------------------------
        if self.state == RobotState.FindWall:
            self.setSpeed(100)
            if front_left < 200 and front_right < 200:
                return
            self.state = RobotState.MountWall
            self.setSpeed(0)
            print('Mount Wall')
        # ------------------------------------------------------------
        # Mount Wall
        # ------------------------------------------------------------
        elif self.state == RobotState.MountWall:
            self.setLeftWheelSpeed(-35)
            self.setRightWheelSpeed(35)
            if front_left > 80 or front_right > 80:
                return
            if right_side < 200:
                return
            if right_corner > 150:
                return
            # We are adjusted
            self.setSpeed(0)
            self.state = RobotState.FollowWall
            print('Follow Wall')
        # ------------------------------------------------------------
        # Follow Wall
        # ------------------------------------------------------------
        elif self.state == RobotState.FollowWall:
            # Facing Wall
            # if front_left > 100 and front_right > 100:
            #     self.setSpeed(50)
            #     self.state = RobotState.FindWall
            
            # Turn Corner
            # if right_corner < 80 and right_side > 300:
                # self.state = RobotState.TurnCorner
                # self.setSpeed(0)


            # Adjust left
            if right_corner > 300: # and right_side > 200
                print('adjust left')
                self.setLeftWheelSpeed(90)
                self.setRightWheelSpeed(100)
            # Adjust right
            elif right_corner < 150: # and right_side > 200
                print('adjust right')
                self.setLeftWheelSpeed(100)
                self.setRightWheelSpeed(90)
            # elif right_side < 80:
            #     self.setSpeed(0)
            else:
                self.setSpeed(100)
        # ------------------------------------------------------------
        # Turn Corner
        # ------------------------------------------------------------
        elif self.state == RobotState.TurnCorner:

            if self.rightCornerPeak is None or right_side > self.rightCornerPeak:
                self.rightCornerPeak = right_side

            if self.rightCornerPeak > right_side and self.rightCornerPeak > 500 and right_side < 180:
                self.state = RobotState.CorrectTurn
                print("Correct Turn")
                return

            if right_side > 200 and right_corner < 80:
                self.setLeftWheelSpeed(80)
                self.setRightWheelSpeed(55)
                return
            elif right_side < 80:
                self.setSpeed(0)
        # ------------------------------------------------------------
        # Correct Turn
        # ------------------------------------------------------------
        elif self.state == RobotState.CorrectTurn:
            self.setLeftWheelSpeed(30)
            self.setRightWheelSpeed(0)
            if right_corner > 140:
                self.state = RobotState.FollowWall
                self.setSpeed(50)


print("Starting")
robot = EPuck(Robot())

while robot.step() and not robot.GameOver:
    robot.travel()

print("Found Trophy")

# END
