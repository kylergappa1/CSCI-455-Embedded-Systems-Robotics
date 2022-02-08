'''
River Kelly
CSCI-455: Embedded Systems (Robotics)
Assignment 01 - Webots E-Puck Robot Maze
Spring 2022
'''
from controller import Robot
from enum import Enum
import math

TIME_STEP = 64
MAX_SPEED = 6.28

class Direction(Enum):
    North = 'North'
    South = 'South'
    East = 'East'
    West = 'West'
    Left = 'Left'
    Right = 'Right'

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

        self.touchSensor = self.robot.getDevice('touch sensor')
        self.touchSensor.enable(TIME_STEP)

    def step(self):
        if self.robot.step(TIME_STEP) != -1:
            return True
        return False

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
        if bearing > 45 and bearing <= 135:
            return Direction.West
        elif bearing > 135 and bearing <= 225:
            return Direction.South
        elif bearing > 225 and bearing <= 315:
            return Direction.East
        else:
            return Direction.North

    def __str__(self):
        str = "{!s:-^40}\n"
        str += "{!s:<20}{!s} - ({:.2f})\n"
        str += "{!s:-^40}"
        return str.format(
            'Robot',
            'Direction:', self.direction.name, self.bearing,
            '')

print("Starting")
robot = EPuck(Robot())

# END
