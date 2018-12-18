class Vehicle(object):
    def __init__(self, id, type, driverType, maxSpeed, valueTime, probLaneChange, startTs, nodeOrigin, nodeDest, network):
        self.id = id
        self.type = type
        self.driverType = driverType
        self.maxSpeed = maxSpeed
        self.valueTime = valueTime
        self.probLaneChange = probLaneChange
        self.startTs = startTs
        self.nodeOrigin = nodeOrigin
        self.nodeDest = nodeDest

        self.network = network
        self.network.registerVehicle(self)

        # parameters below should be calculated on every tick
        #self.timeBudget = timeBudget
        #self.expectedEndTs = expectedEndTs
        #self.listTs = listTs
        #self.tsLocationMap = tsLocationMap
        #self.tsRouteMap = tsRouteMap

    def __repr__(self):
        return "<" + " ".join([str(self.id), self.type, str(self.driverType), str(self.maxSpeed),
                         str(self.valueTime), str(self.probLaneChange),
                         str(self.startTs), str(self.nodeOrigin), str(self.nodeDest)]) + ">"
