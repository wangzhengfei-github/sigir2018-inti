import random


class ConfigGenerator:
    def __init__(self, cycle=200):
        self.cycle = cycle
        self.n_phases = [4, 4, 3, 5, 3, 4, 3]

    def random_single(self, n_phase=4):
        """random generlate a configuration for single light.

        Args:
            n_phases: the number of the light's phase.

        Returns:
            A list [offset, phases1, phases2, ...]
        """
        pivots = []
        # offset should less than cycle
        pivots.append(random.randint(0, self.cycle - 1))
        while len(pivots) < n_phase + 1:
            random_pivot = random.randint(1, self.cycle - 1)
            if random_pivot not in pivots:
                pivots.append(random_pivot)
        return pivots

    def generate_config(self):
        """generate the whole configurations for all lights.

        Returns:
            A list, each element is another list representing the light's configuration.
        """
        config = []
        for n_phase in self.n_phases:
            current_config = self.random_single(n_phase)
            config.append(current_config)
        return config


if __name__ == '__main__':
    G = ConfigGenerator(200)
    for i in range(10):
        print('test #' + str(i + 1))
        config = G.generate_config()
        for tmp in config:
            print(tmp)
        print('\n')
