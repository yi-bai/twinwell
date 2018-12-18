'''
Created on 2018/07/02
This module is used to read the OD matrices from csv files.

csv file of OD matrix should be named as the time slot with beginning and ending time;
names following the above rule is to suit the loading of traffic demand to the road network;
all csv files for one road network or a possible scenario should be put in one folder.

The format of OD demand in the csv file consists of the following columns:
time slot, vehicle type, origin ID, destination ID,vehicle volume

currently, we use a time slot of 5 minutes. vehicles generated during this time slot are put randomly onto the road network.

done and checked on 2018/7/4

module of generating vehicles is also included in this module as vehicle-generation is just the next step of reading OD-matrix; and these two modules cannot be separated.

@author: gong
'''
import time, datetime
import random

random.seed(10)
import numpy as np
from z_ExistingPackages.Dijkstra2 import *
from c_TimeCalculation.time_calculation import *
from math import ceil, floor
import csv
import os
from a_ReadRoadNetwork.class_lane import *
from ..model.vehicle import Vehicle

def timeslot2tsPair(timeslot):
    tlist = [t.split(".") for t in timeslot.split("-")]
    return datetime.datetime(2019, 1, 1, int(tlist[0][0]), int(tlist[0][1]), 0), datetime.datetime(2019, 1, 1, int(tlist[1][0]), int(tlist[1][1]))

def vehicleMaxSpeed(type):
    random.seed(10)
    maxSpeedInterval = {"car": [70, 80], "truck": [50, 70], "bus": [40, 60]}
    return random.randint(maxSpeedInterval[type][0], maxSpeedInterval[type][1])

def genDriverType():
    return random.randint(0, 1)

def genDriverValueTimeGen(medianValueTime):
    sigma = medianValueTime / 5.0
    return np.random.normal(medianValueTime, sigma, 1)[0]

def genProbLaneChange(type):
    if type == 0:
        return random.randint(0, 5) / 10.0
    elif type == 1:
        return random.randint(6, 10) / 10.0

def readOd(path):
    filenames = os.listdir(path)

    tsPairNodePairTypeMap = {}
    for filename in filenames:
        pathfile = path + "/" + filename
        f = open(pathfile)
        f.readline()
        r = csv.reader(f)
        for row in r:
            (timeslot, vehicleType, origin, dest, volume) = (row[0], row[1], row[2], row[3], row[4])
            tsPair = timeslot2tsPair(timeslot)

            if tsPair not in tsPairNodePairTypeMap: tsPairNodePairTypeMap[tsPair] = {}
            if (origin, dest) not in tsPairNodePairTypeMap[tsPair]: tsPairNodePairTypeMap[tsPair][(origin, dest)] = {}
            if vehicleType not in tsPairNodePairTypeMap[tsPair][(origin, dest)]: tsPairNodePairTypeMap[tsPair][(origin, dest)][vehicleType] = 0

            tsPairNodePairTypeMap[tsPair][(origin, dest)][vehicleType] += volume

    return tsPairNodePairTypeMap

def genVehicle(tsPairNodePairTypeMap, distribution, vehicleId, medianValueTime, network):
    if distribution == "uniform":
        for tsPair in tsPairNodePairTypeMap.keys():
            for nodePair in tsPairNodePairTypeMap[tsPair].keys():
                for vehicleType in tsPairNodePairTypeMap[tsPair][nodePair].keys():
                    vehicleVolume = tsPairNodePairTypeMap[tsPair][nodePair][vehicleType]
                    startTs, endTs = tsPair[0], tsPair[1]
                    duration = endTs - startTs
                    origin, dest = nodePair[0], nodePair[1]

                    if not vehicleVolume: continue

                    interval = 1.0 * duration / vehicleVolume
                    for i in range(vehicleVolume):
                        vehicleStartTs = startTs + int(ceil(interval * i))
                        vehicleId += 1
                        maxSpeed = vehicleMaxSpeed(vehicleType)
                        driverType = genDriverType()
                        valueTime = genDriverValueTimeGen(medianValueTime)
                        probLaneChange = genProbLaneChange(driverType)

                        Vehicle(vehicleId, vehicleType, driverType, maxSpeed, valueTime, probLaneChange, vehicleStartTs, origin, dest, network)