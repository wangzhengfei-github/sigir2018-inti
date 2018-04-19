import random
import datetime
import copy
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from serial_environment import SumoEnvironment

sample = [[0, 111, 9, 43, 37], [10, 28, 121, 13, 38], [10, 28, 134, 38], [10, 34, 75, 31, 19, 41],
           [134, 48, 89, 63], [105, 35, 67, 52, 46], [52, 30, 96, 74]]
lower = [[0, 35, 8, 10, 35], [0, 8, 35, 8, 35], [0, 10, 35, 35], [0, 10, 35, 10, 8, 35],
            [0, 10, 35, 35], [0, 10, 35, 10, 35], [0, 10, 35, 35]]
min_cycle = max([sum(min_phase) for min_phase in lower])

env = SumoEnvironment()
n_iteration = []
score_history = []


class GA():
    def __init__(self, sigma, count):
        self.sigma = sigma  # truncnorm normal distribution parameter
        self.count = count
        self.cycles = [200 for i in range(3 * count)]
        self.population = self.gen_population(sigma, count)

    def evolve(self, mutation_rate=0.01):
        parent = self.selection()
        self.crossover(parent)
        self.mutation(mutation_rate)

    def gen_chromosome(self, sigma):
        upper = self.gen_upper(self.cycles[0])
        chromosome = [[self.get_truncnorm_sample(lower[i][j], upper[i][j], gene, sigma, 1)
                       for j, gene in enumerate(genes)] for i, genes in enumerate(sample)]
        chromosome = self.normalization(chromosome, self.cycles[0])
        return chromosome

    def gen_population(self, sigma, count):
        return [sample] + [self.gen_chromosome(sigma) for i in range(count-1)]

    def fitness(self, chromosome):
        return env.run_simulation(chromosome)

    def selection(self):
        unique_list = []
        for chromosome in self.population:
            tmp = copy.deepcopy(sample)
            tmp[0] = copy.deepcopy(chromosome[0])
            tmp[1] = copy.deepcopy(chromosome[1])
            tmp[2] = copy.deepcopy(chromosome[2])
            if tmp not in unique_list:
                unique_list.append(tmp)
        graded = [(self.fitness(chromosome), chromosome) for chromosome in unique_list]
        sorted_graded = sorted(graded)
        score_total = 0
        for item in sorted_graded[:self.count]:
            score_total += item[0]
            print(' -', item[0], ' ', item[1])
        score_total /= self.count
        graded = [x[1] for x in sorted_graded]
        print('The most suitable configuration score is ', self.fitness(graded[0]))
        print('The average score in this generation is ', score_total)
        score_history.append(score_total)
        plt.plot(n_iteration, score_history)
        plt.savefig('fitness-iteration.png')
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
                cross_pos = random.randint(0, len(sample))
                male = copy.deepcopy(parents[male_cnt])
                female = copy.deepcopy(parents[female_cnt])
                child = male[:cross_pos] + female[cross_pos:]
                cycle = self.cycles[male_cnt] if cross_pos > len(sample) / 2 else self.cycles[female_cnt]
                child = self.normalization(child, cycle)
                self.cycles[len(parents)+len(children)] = cycle
                children.append(child)
        self.population = parents + children

    def mutation(self, rate, count=3):
        population_size = len(self.population)
        for i in range(population_size):
            if random.random() < rate:
                tmp = copy.deepcopy(self.population[i])
                cycle = self.get_truncnorm_sample(min_cycle, 400, self.cycles[i], 20, 1)
                self.population[i] = self.normalization(self.population[i], cycle)
                self.cycles[i] = cycle
                upper = self.gen_upper(self.cycles[i])
                mutant_crossings = random.sample(range(len(sample)), count)
                for crossing in mutant_crossings:
                    phase_count = len(sample[crossing])
                    mutant_phases = random.sample(range(phase_count), int(phase_count * 0.5))
                    for phase in mutant_phases:
                        self.population[i][crossing][phase] = self.get_truncnorm_sample(
                            lower[crossing][phase], upper[crossing][phase],
                            self.population[i][crossing][phase], self.sigma, 1)

                self.population[i] = self.normalization(self.population[i], cycle)
                self.population.append(tmp)

    def result(self):
        graded = [(self.fitness(chromosome), chromosome) for chromosome in self.population]
        graded = [x[1] for x in sorted(graded)]
        return graded[0], self.fitness(graded[0])

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
    start_time = datetime.datetime.now()
    ga = GA(sigma=10, count=20)
    print(format_output(ga.population[0]))
    print('sample configuration score is ', ga.fitness(ga.population[0]))

    for iteration in range(500):
        n_iteration.append(iteration)
        print('---------- Iteration %d ----------' % iteration)
        ga.evolve(mutation_rate=0.5)

    best_configuration, best_score = ga.result()
    print(format_output(best_configuration))
    print('the score of best configuration is ', best_score)
    close_time = datetime.datetime.now()
    print('simulation time=' + str((close_time - start_time) / 60))

    n_iteration.append(1500)
    results = ga.selection()
    print('training result: ')
    for single in results:
        print(single)
