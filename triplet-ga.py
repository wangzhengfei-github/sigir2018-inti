import sys
import random
import copy
from multiprocessing import Process, Manager
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from environment import SumoEnvironment

template = [[0, 111, 9, 43, 37], [10, 28, 121, 13, 38], [10, 28, 134, 38], [10, 34, 75, 31, 19, 41],
           [134, 48, 89, 63], [105, 35, 67, 52, 46], [52, 30, 96, 74]]
sample = [[0, 111, 9, 43, 37], [10, 28, 121, 13, 38], [10, 28, 134, 38], [10, 34, 75, 31, 19, 41],
           [134, 48, 89, 63], [105, 35, 67, 52, 46], [52, 30, 96, 74]]
lower = [[0, 35, 8, 10, 35], [0, 8, 35, 8, 35], [0, 10, 35, 35], [0, 10, 35, 10, 8, 35],
            [0, 10, 35, 35], [0, 10, 35, 10, 35], [0, 10, 35, 35]]
min_cycle = max([sum(min_phase) for min_phase in lower])

env = SumoEnvironment()
n_iteration = []
score_history = []

N_TRAFFIC_LIGHT = 7
N_PROCESS = 4


class GA():
    def __init__(self, sigma, count, light_id):
        self.sigma = sigma  # truncnorm normal distribution parameter
        self.count = count
        self.light_id = light_id  # the traffic light need to be optimize
        self.cycles = [200 for i in range(3 * count)]
        self.population = [copy.deepcopy(template) for i in range(self.count)]

    def evolve(self, mutation_rate=0.01):
        parent = self.selection()
        self.crossover(parent)
        self.mutation(mutation_rate)

    def gen_chromosome(self, sigma):
        upper = self.gen_upper(self.cycles[0])
        chromosome = [[self.get_truncnorm_sample(lower[i][j], upper[i][j], gene, sigma, 1)
                       for j, gene in enumerate(genes)] for i, genes in enumerate(sample)]
        # chromosome = self.normalization(chromosome, self.cycles[0])
        return chromosome

    def gen_population(self, sigma, count):
        return [sample] + [self.gen_chromosome(sigma) for i in range(count-1)]

    def fitness(self, chromosomes):
        manager = Manager()
        scores_list = manager.dict()
        parallel_num = len(chromosomes)
        jobs = []
        for i in range(parallel_num):
            p = Process(target=env.run_simulation, args=(chromosomes[i], i, scores_list,))
            jobs.append(p)
            p.start()
        for p in jobs:
            p.join()
        fitnesses = [scores_list[i] for i in range(parallel_num)]
        return fitnesses

    def selection(self):
        unique_list = []
        for chromosome in self.population:
            valid_config = True
            for light_id in self.light_id:
                for phase in chromosome[light_id][1:]:
                    if int(phase) <= 0:
                        valid_config = False
                        break
            if valid_config is True and chromosome not in unique_list:
                unique_list.append(chromosome)

        # parallel
        graded = []
        i = 0
        while (i < len(unique_list)):
            if i + N_PROCESS < len(unique_list):
                parallel_num = N_PROCESS
            else:
                parallel_num = len(unique_list) - i

            fitnesses = self.fitness(unique_list[i : i + parallel_num])
            for fitness in fitnesses:
                graded.append((fitness, unique_list[i]))
                i += 1
        # serial
        #graded = [(self.fitness(chromosome), chromosome) for chromosome in unique_list]

        sorted_graded = sorted(graded)
        score_total = 0
        for item in sorted_graded[:self.count]:
            score_total += item[0]
            print(' -', item[0], ' ', item[1])
        score_total /= self.count
        graded = [x[1] for x in sorted_graded]
        print('The most suitable configuration score is ', sorted_graded[0][0])
        print('The average score in this generation is ', score_total)
        score_history.append(score_total)
        plt.plot(n_iteration, score_history)
        plt.savefig('log/double-light-fitness-iteration.png')
        parents = copy.deepcopy(graded[:self.count])
        self.cycles[:len(parents)] = [int(sum(chromosome[0])-chromosome[0][0]) for chromosome in parents]
        return parents

    def crossover(self, parents):
        children = []
        target_count = len(parents)
        while len(children) < target_count:
            male_cnt = random.randint(0, len(parents)-1)
            female_cnt = random.randint(0, len(parents)-1)
            if male_cnt != female_cnt:
                male = copy.deepcopy(parents[male_cnt])
                female = copy.deepcopy(parents[female_cnt])
                child = copy.deepcopy(male[:2] + female[2:])
                children.append(child)
        self.population = parents + children

    def mutation(self, rate, count=3):
        population_size = len(self.population)
        for i in range(population_size):
            if random.random() < rate:
                tmp = copy.deepcopy(self.population[i])
                cycle = self.get_truncnorm_sample(min_cycle, 400, self.cycles[i], 20, 1)
                # self.population[i] = self.normalization(self.population[i], cycle)
                self.cycles[i] = cycle
                upper = self.gen_upper(self.cycles[i])
                crossing = random.randint(0, 1)
                self.population[i][crossing][0] = self.get_truncnorm_sample(
                        lower[crossing][0], upper[crossing][0],
                        self.population[i][crossing][0], self.sigma, 1)
                self.population.append(tmp)

    def result(self):
        # parallel
        graded = []
        i = 0
        while (i < len(self.population)):
            if i + N_PROCESS < len(self.population):
                parallel_num = N_PROCESS
            else:
                parallel_num = len(self.population) - i
            fitnesses = self.fitness(self.population[i: i + parallel_num])
            for fitness in fitnesses:
                graded.append((fitness, self.population[i]))
                i += 1
        graded = [x[1] for x in sorted(graded)]
        return graded[0], self.fitness([graded[0]])[0]

    def get_truncnorm_sample(self, lower, upper=200, mu=0, sigma=1, n=1):
        X = truncnorm((lower - mu) / sigma, (upper - mu) / sigma, loc=mu, scale=sigma)
        samples = X.rvs(n)
        return int(samples)

    def normalization(self, chromosome, cycle=200):
        for i, genes in enumerate(chromosome):
            old_cycle = sum(genes)-genes[0]
            if old_cycle != cycle:
                time_sum = 0
                for j, gene in enumerate(genes):
                    if j != 0:
                        if j == len(genes)-1:
                            genes[j] = cycle - time_sum if cycle - time_sum >= lower[i][j] else lower[i][j]
                        else:
                            genes[j] = round((gene-lower[i][j])*(cycle-lower[i][j])/(old_cycle-lower[i][j]))+lower[i][j]
                            time_sum += genes[j]
                    else:
                        genes[j] = round(genes[j] / old_cycle * cycle)
        return chromosome

    def gen_upper(self, cycle=200):
        upper = [[cycle if j!=0 else cycle-1 for j in range(len(sample[i]))] for i in range(len(sample))]
        upper[0][0] = 0.01
        return upper


def format_output(traffic_lights):
    format_str = ''
    for i, light in enumerate(traffic_lights):
        for j, phase in enumerate(light):
            format_str += str(phase)
            if j != len(light)-1:
                format_str += ','
        if i != len(traffic_lights)-1:
            format_str += ';'
    return format_str


if __name__ == '__main__':
    n_iteration = []
    score_history = []
    plt.figure()

    light1_seed = [
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41],
        [0, 61, 10, 13, 41]
    ]

    light2_seed = [
        [5, 27, 103, 26, 40],
        [75, 28, 121, 13, 38],
        [18, 29, 125, 13, 37],
        [19, 29, 125, 13, 37],
        [69, 27, 103, 26, 40],
        [94, 27, 103, 26, 40],
        [73, 27, 103, 26, 40],
        [119, 27, 103, 26, 40],
        [32, 27, 103, 26, 40],
        [114, 27, 103, 26, 40]
    ]

    light3_seed = [
        [19, 27, 120, 48],
        [0, 20, 136, 44],
        [20, 24, 121, 55],
        [1, 33, 114, 53],
        [6, 27, 121, 52],
        [2, 47, 88, 46],
        [5, 24, 140, 54],
        [4, 25, 98, 59],
        [0, 26, 127, 61],
        [0, 18, 104, 36]
    ]

    # ---------- (1+2) + 3 ----------
    print('training 1 and 2 light...')
    ga = GA(sigma=10, count=20, light_id=[1, 2, 3])
    for i in range(10):
        ga.population[i][0] = copy.deepcopy(light1_seed[i])
        ga.population[i][1] = copy.deepcopy(light2_seed[i])
        ga.population[i+10][2] = copy.deepcopy(light3_seed[i])

    for config in ga.population:
        print(config)

    for iteration in range(1000):
        n_iteration.append(iteration)
        print('---------- Iteration %d ----------' % iteration)
        ga.evolve(mutation_rate=0.5)

    tmp = sys.stdout
    sys.stdout = open('log/log-12-3.txt', 'w')
    print('population: ')
    for single in ga.population:
        print(single)
    sys.stdout = tmp
