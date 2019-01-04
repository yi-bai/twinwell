class Network(object):
    def __init__(self, ts):
        self.ts = ts
        self.idNodeMap = {}
        self.idLinkMap = {}
        self.idLaneMap = {}
        self.idVehicleMap = {}
        self.typeGraphMap = {}

    def registerNode(self, node):
        if node.id in self.idNodeMap: raise("duplicated node id")
        self.idNodeMap[node.id] = node

    def registerLink(self, link):
        if link.id in self.idLinkMap: raise("duplicated link id")
        self.idLinkMap[link.id] = link

    def registerLane(self, lane):
        if lane.id in self.idLaneMap: raise("duplicated lane id")
        self.idLaneMap[lane.id] = lane
        if lane.type not in self.typeGraphMap: self.typeGraphMap[lane.type] = {}
        if lane.link.node1.id not in self.typeGraphMap[lane.type]: self.typeGraphMap[lane.type][lane.link.node1.id] = {}
        self.typeGraphMap[lane.type][lane.link.node1.id][lane.link.node2.id] = lane

    def registerVehicle(self, vehicle):
        if vehicle.id in self.idVehicleMap: raise("duplicated vehicle id")
        self.idVehicleMap[vehicle.id] = vehicle

    def updateLanes(self):
        for lane in self.idLaneMap.values():
            lane.countPcu = 0
        for vehicle in [ v for v in self.idVehicleMap.values() if v.isRunning(self.ts) ]:
            pcu = {"car": 1.0, 0: 1.0, "bus": 3.5, 1: 3.5, "truck": 3.5, 2: 3.5}[vehicle.type]
            vehicle.currentLane.countPcu += pcu
        for lane in self.idLaneMap.values():
            lane.updatePropertiesBasedOnPcu()

    def runningVehicleCount(self):
        return len([None for v in self.idVehicleMap.values() if v.isRunning(self.ts)])

    def finishVehicleCount(self):
        return len([None for v in self.idVehicleMap.values() if v.isFinish(self.ts)])