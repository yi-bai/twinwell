class Node(object):
    def __init__(self, id, type, x, y, network):
        self.id = id
        self.type = type
        self.x = float(x)
        self.y = float(y)
        self.network = network

        self.network.registerNode(self)

    def __repr__(self):
        return "<" + " ".join(["node" + self.id, self.type, str(self.x), str(self.y)]) + ">"

    def dist(self, node):
        return ((self.x - node.x) ** 2 + (self.y - node.y) ** 2) ** 0.5