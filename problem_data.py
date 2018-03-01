import math


class Data:
    def __init__(self, input_file):
        self.rides = list()
        self.read_data(input_file)
        pass

    def read_data(self, input_file):
        file = open(input_file, 'r')
        first_line = [int(x) for x in file.readline().split(' ')]
        self.R = first_line[0]  # Rows
        self.C = first_line[1]  # Columns
        self.F = first_line[2]  # Number of vehicles
        self.N = first_line[3]  # Number of rides
        self.B = first_line[4]  # Per-ride bonus
        self.T = first_line[5]  # Number of steps
        for i in range(self.N):
            ride_line = [int(x) for x in file.readline().split(' ')]
            a = ride_line[0]
            b = ride_line[1]
            x = ride_line[2]
            y = ride_line[3]
            s = ride_line[4]
            f = ride_line[5]
            ride = Ride(i, a, b, x, y, s, f)
            self.rides.append(ride)


def dist_v(vehicle_pos, ride):
    return math.fabs(ride.a - vehicle_pos[0]) + math.fabs(ride.b - vehicle_pos[1])

def dist(a, b, x, y):
    return math.fabs(x - a) + math.fabs(y - b)

class Ride:
    def __init__(self, id, a, b, x, y, s, f):
        self.id = id
        self.a = a  # Start position x
        self.b = b  # Start position y
        self.x = x  # Finish position x
        self.y = y  # Finish position y
        self.s = s  # Earliest start
        self.f = f  # Latest finish
        self.p = dist(a, b, x, y)  # Normal Score
        self.ls = f - self.p  # Latest start
        self.ef = s + self.p  # Earliest finish

    def __hash__(self):
        return self.id

    def __str__(self):
        return "a={}, b={}, x={}, y={}, s={}, f={}".format(self.a, self.b, self.x, self.y, self.s, self.f)
