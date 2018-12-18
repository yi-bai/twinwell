class Node(object):
    def __init__(self, id, type, x, y, network):
        self.id = id
        self.type = type
        self.x = x
        self.y = y
        self.network = network

        self.network.registerNode(self)

    def dist(self, node):
        return ((self.x - node.x) ** 2 + (self.y - node.y) ** 2) ** 0.5