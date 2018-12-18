class Lane(object):
    # as it is lane, it has only one direction; this is the different part from link
    def __init__(self, id, type, link, freeSpeed, freeTravelTime, fixedCharge, speed, network):
        self.id = id
        self.type = type
        self.link = link

        self.length = None
        self.freeSpeed = freeSpeed
        self.freeTravelTim = freeTravelTime
        self.fixedCharge = fixedCharge

        self.speed = speed

        self.count = 0
        self.density = 0.1
        self.traveltime = 0.1
        self.charge = 0.1

        self.timeSpeedMap = {}
        self.timeCountMap = {}
        self.timeDensityMap = {}

        self.network = network
        self.network.registerLane(self)

    def freeTimeInSec(self):
        return self.link.lengthInKm / self.freeSpeed * 3600.0

    def travelTimeInSec(self):
        return self.freeTimeInSec() * 1.25 #magic number