'''
Created on 2018/07/10

@author: gong
'''
from ..model.node import Node
from ..model.link import Link
from ..model.lane import Lane
import csv
import copy

def readNodes(nodefile, network):
    f = csv.reader(nodefile)
    for row in f:
        (id, type, x, y) = (row[0], row[1], row[3], row[4])
        Node(id, type, x, y, network)

def readLanes(lanefile, network):
    f = csv.reader(lanefile)
    for row in f:
        linkId = row[4]
        if linkId in network.idLaneMap:
            link = network.idLaneMap[linkId]
        else:
            link = Link(row[4], row[5], row[2], row[3], network)
        Lane(row[1], row[0], link, row[6], row[7], row[8], None, network)