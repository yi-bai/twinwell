JAMDENSITY = 12400

class Lane(object):
    # as it is lane, it has only one direction; this is the different part from link
    def __init__(self, id, type, link, freeSpeed, freeTravelTime, fixedCharge, speed, network):
        self.id = id
        self.type = type
        self.link = link

        self.length = None
        self.freeSpeed = int(freeSpeed)
        self.freeTravelTime = freeTravelTime
        self.fixedCharge = fixedCharge

        self.speed = speed

        self.countPcu = 0
        self.density = 0.1
        self.travelTime = 0.1
        self.charge = 0.1

        #self.timeSpeedMap = {}
        #self.timeCountMap = {}
        #self.timeDensityMap = {}

        self.network = network
        self.network.registerLane(self)

    def __repr__(self):
        return "<" + " ".join(["lane" + self.id, self.type, str(self.link.node1.id), str(self.link.node2.id), "density: "+str(self.density), "speed: "+str(self.speed), "travelTime: "+str(self.travelTime) ]) + ">"

    def freeTimeInSec(self):
        return self.link.lengthInKm / self.freeSpeed * 3600.0

    def travelTimeInSec(self):
        return self.freeTimeInSec() * 1.25 #magic number

    def updatePropertiesBasedOnPcu(self):
        def densitySpeed(density, freespeed):
            # this function returns the speed on a lane when inputting a density
            # negative linear relationship between density and speed is used
            # additional parameters of free speed and jam  density are needed.
            if density >= JAMDENSITY:  # to avoid getting 0 or minus speed
                speed = 0.001  # km/h
            else:
                speed = freespeed * (1.0 - 1.0 * density / JAMDENSITY)
            return speed

        self.density = self.countPcu / self.link.lengthInKm
        self.speed = densitySpeed(self.density, self.freeSpeed)
        self.travelTime = self.link.lengthInKm * 3600.0 / self.speed