'''
Created on 2018/07/09

@author: gong
'''
class Node(object):
    def __init__(self,line):
        #record=line.split(",")
        record=line
        self.nodeid=str(record[0])# node ID
        self.nodetype=int(record[1])# node type: centroid, signalized intersection(long duration or short duration, unsignalized intersection;currently only centroid or not is used
        self.coortype=int(record[2])# coordinate system type, either Cartesian or geographic, the later needs to be transformed to the former for calculation
        self.coorX=int(record[3])# X coordinate, can be transformed from longitude-latitude
        self.coorY=int(record[4])# Y coordinate, can be transformed from longitude-latitude       