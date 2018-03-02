import random

import os
import threading

from problem_data import Data, dist_v

# input_file = "a_example"
# input_file = "b_should_be_easy"
input_file = "c_no_hurry"
# input_file = "d_metropolis"
# input_file = "e_high_bonus"
out_dir = "out/"

class GA:
    population_size = 10
    selection_rate = 0.3
    mutation_rate = 0.01  # Mutation chance per gene
    terminated = False

    def __init__(self, problem_data, population_size=20, selection_rate=0.3, mutation_rate=0.1):
        self.data = problem_data

        if population_size < 2:
            raise AttributeError("Population size must be > 2.")
        self.population_size = population_size

        if any(x < 0 or x > 1 for x in [selection_rate, mutation_rate]):
            raise AttributeError("Rate must be in the interval [0, 1]")

        self.selection_rate = selection_rate
        self.mutation_rate = mutation_rate
        self.generation = 0

    def run(self):
        print("Initializing...")
        population = Population(self).init_random_population()
        print("Evaluating...")
        population.evaluate()
        while not self.terminated:
            self.generation += 1
            print("Selection ({})...".format(self.generation))
            parents = population.select()
            print("Crossover ({})...".format(self.generation))
            children = parents.crossover()
            print("Mutation ({})...".format(self.generation))
            children = children.mutate()
            print("Merging ({})...".format(self.generation))
            population = parents.merge(children)
            print("Evaluating ({})...".format(self.generation))
            population.evaluate()
            print(population)
            print(" ----------- ")
        return population.best


class Population:
    def __init__(self, ga, population=list()):
        self.ga = ga
        self.population = population
        self.best = None

    def init_random_population(self):
        self.population.clear()
        for _ in range(self.ga.population_size):
            self.population.append(Solution(self.ga).init_random_solution())
        return self

    # Returns a new population formed by the best solutions of this population.
    # Assumes current population is already sorted by decreasing fitness
    def select(self):
        elites = Population(self.ga, self.population[:int(self.ga.selection_rate * len(self.population))])
        if len(elites.population) > 0:
            elites.best = elites.population[0]
        return elites

    # Returns a new population formed by (population_size - current_population) children
    def crossover(self):
        children = []
        for _ in range(self.ga.population_size - len(self.population)):
            parent1 = random.choice(self.population)
            parent2 = random.choice(self.population)
            child = parent1.crossover(parent2)
            children.append(child)
        return Population(self.ga, children)

    # Mutates this population
    def mutate(self):
        for solution in self.population:
            solution.mutate()
        return self

    def evaluate(self):
        for solution in self.population:
            solution.evaluate()
        self.population = sorted(self.population, key=lambda s: s.fitness, reverse=True)
        if self.best is None or self.population[0].fitness > self.best.fitness:
            self.best = self.population[0]
        return self

    # Merges current population with another, altering this instance's state
    def merge(self, other):
        self.population.extend(other.population)

        # Declare best solution out of the two populations
        best_solutions = tuple(filter(lambda s: s is not None, (self.best, other.best)))
        if not best_solutions:
            self.best = None
        else:
            self.best = sorted(best_solutions, key=lambda s: s.fitness, reverse=True)[0]
        return self

    def __str__(self):
        return 'Best: {0}\n'.format(self.best.fitness) \
               + '\n'.join(map(str, self.population))


class Solution:
    def __init__(self, ga):
        self.ga = ga
        self.solution = dict()  # VehicleID -> [Drives]
        for v in range(self.ga.data.F):
            self.solution[v] = list()
        self.available_rides = set()  # {DriveID}
        for i in range(self.ga.data.N):
            self.available_rides.add(i)
        self.fitness = float("-inf")

    def init_random_solution(self):
        for v in range(self.ga.data.F):
            for _ in range(0, self.ga.data.N // self.ga.data.F):
                ride_id = random.sample(self.available_rides, 1)[0]
                self.add_ride_to_vehicle(ride_id, v)
        self.fix_solution()
        return self

    def fix_solution(self):
        pass  # While solutions may sometimes be late when reaching the destination, they are always valid
        return self

    # Returns a new solution by crossover
    def crossover(self, other):
        child = Solution(self.ga)
        for v in range(0, self.ga.data.F):
            min_length = min(len(self.solution[v]), len(other.solution[v]))
            split_idx = random.randint(0, min_length-1)
            for i in range(split_idx):
                child.add_ride_if_available_else_random(self.solution[v][i], v)
            for i in range(split_idx, len(other.solution[v])):
                child.add_ride_if_available_else_random(other.solution[v][i], v)
        return child.fix_solution()

    # Randomly mutate each gene in this solution with a probability of mutation_rate
    def mutate(self):
        for v in range(0, self.ga.data.F):
            for r_idx, r in enumerate(self.solution[v]):
                if random.uniform(0.0, 1.0) <= self.ga.mutation_rate:
                    random_v = random.randint(0, self.ga.data.F-1)
                    random_r = random.randint(0, len(self.solution[v])-1)
                    # Swap genes
                    self.solution[v][r_idx], self.solution[random_v][random_r] = self.solution[random_v][random_r], self.solution[v][r_idx]


    def evaluate(self):
        score = 0
        for v in self.solution.keys():
            vehicle_pos = (0,0)
            vehicle_time = 0
            for ride in self.solution[v]:
                arrival_time = vehicle_time + dist_v(vehicle_pos, ride)
                if arrival_time <= ride.ls:
                    score += ride.p
                    if arrival_time <= ride.s:
                        score += self.ga.data.B
                vehicle_time = ride.f
                vehicle_pos = (ride.x, ride.y)
        self.fitness = score
        return self

    def print(self):
        output = ''
        for vehicle in self.solution.keys():
            output += str(len(self.solution[vehicle]))
            for ride in self.solution[vehicle]:
                output += ' {}'.format(ride.id)
            output += '\n'
        return output

    def __str__(self):
        # return "Fitness: {0}; Solution: {1}".format(self.fitness, self.solution)
        return "Fitness: {0}".format(self.fitness)

    def add_ride_to_vehicle(self, ride_id, vehicle_id):
        assert ride_id in self.available_rides
        try:
            self.solution[vehicle_id].append(self.ga.data.rides[ride_id])
        except KeyError as e:
            print(e)
        self.available_rides.remove(ride_id)

    def add_ride_if_available_else_random(self, ride, vehicle_id):
        if ride in self.available_rides:
            self.add_ride_to_vehicle(ride.id, vehicle_id)
        else:
            ride_id = random.sample(self.available_rides, 1)[0]
            self.add_ride_to_vehicle(ride_id, vehicle_id)




if __name__ == '__main__':
    def receive_input(ga):
        input("Press any key to terminate.")
        print("Terminating...")
        ga.terminated = True

    data = Data('input/' + input_file + '.in')
    ga = GA(data)
    input_listener = threading.Thread(target=receive_input, args=(ga,))
    input_listener.start()

    solution = ga.run()
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    file = open(out_dir + input_file + '.txt', 'wb')
    file.write(solution.print().encode('utf-8'))
    print("Solution written to "+ out_dir + input_file + '.txt')
