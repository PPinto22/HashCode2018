import os

from problem_data import Data, dist_v

# input_file = "a_example"
# input_file = "b_should_be_easy"
# input_file = "c_no_hurry"
# input_file = "d_metropolis"
# input_file = "e_high_bonus"
out_dir = "out/"


class Solver:
    def __init__(self, file):
        self.data = Data(file)
        self.vehicle_positions = dict()  # Map<Id, (x,y)>
        self.vehicle_availability = dict()  # Map<Id, int>
        self.vehicle_rides = dict()  # Map<Id, [Ride]>
        # Flags to force the vehicles to move, regardless of whether the ride can be finished on time
        self.vehicle_force = dict()  # Map<ID, Bool>
        for i in range(0, self.data.F):
            self.vehicle_positions[i] = (0, 0)
            self.vehicle_availability[i] = 0
            self.vehicle_rides[i] = list()
            self.vehicle_force[i] = False

    def solve(self):
        # Rides stores the list of available rides at each moment, ordered by starting time
        rides = list(sorted(self.data.rides, key=lambda r: (r.s, r.f)))
        for it in range(self.data.T):
            print(it)
            for v in range(self.data.F):
                if self.vehicle_availability[v] != 0:
                    self.vehicle_availability[v] -= 1
                else:
                    # Find best available ride
                    for r in rides:
                        # If ride finish is lower than current iteration, remove ride from available list and continue
                        if r.f < it:
                            rides.remove(r)
                            continue
                        # If force flag is true, take the ride regardless
                        if self.vehicle_force[v]:
                            ride = r
                            break

                        # If we can't finish the ride on time, try the next ride
                        if r.f < it + dist_v(self.vehicle_positions[v], r) + r.p:
                            continue
                        else:
                            ride = r
                            break
                    else:
                        # If we didn't find a valid ride
                        self.vehicle_force[v] = True
                        continue
                    force = False
                    rides.remove(ride)
                    self.vehicle_rides[v].append(ride)
                    self.vehicle_availability[v] = ride.p + dist_v(self.vehicle_positions[v], ride)
                    self.vehicle_positions[v] = (ride.x, ride.y)
        self.print_solution()

    def print_solution(self):
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        file = open(out_dir + input_file + '.txt', 'wb')
        output = ''
        for vehicle in self.vehicle_rides.keys():
            output += str(len(self.vehicle_rides[vehicle]))
            for ride in self.vehicle_rides[vehicle]:
                output += ' {}'.format(ride.id)
            output += '\n'
        file.write(output.encode("utf-8"))


if __name__ == '__main__':
    solver = Solver('input/' + input_file + '.in')
    solver.solve()
