class Network(object):
    def __init__(self, ts):
        self.ts = ts
        self.idNodeMap = {}
        self.idLinkMap = {}
        self.idLaneMap = {}
        self.idVehicleMap = {}
        self.typeNodeLaneMap = {}

    def registerNode(self, node):
        if node.id in self.idNodeMap: raise("duplicated node id")
        self.idNodeMap[node.id] = node

    def registerLink(self, link):
        if link.id in self.idLinkMap: raise("duplicated link id")
        self.idLinkMap[link.id] = link

    def registerLane(self, lane):
        if lane.id in self.idLaneMap: raise("duplicated lane id")
        self.idLaneMap[lane.id] = lane
        if lane.type not in self.typeNodeLaneMap: self.typeNodeLaneMap[lane.type] = {}
        self.typeNodeLaneMap[lane.type][(lane.link.node1, lane.link.node2)] = lane

    def registerVehicle(self, vehicle):
        if vehicle.id in self.idVehicleMap: raise("duplicated vehicle id")
        self.idVehicleMap[vehicle.id] = vehicle