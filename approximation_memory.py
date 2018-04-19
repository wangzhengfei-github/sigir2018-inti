import random
from collections import deque


class Memory:
    def __init__(self, maxlen=2000):
        self.maxlen = maxlen
        self.memory_count = 0
        self.recent_records = deque(maxlen=self.maxlen)

    def append(self, observed_config, observed_states, observed_score):
        self.recent_records.append([observed_config, observed_states, observed_score])
        self.memory_count += 1

    def sample(self, batch_size):
        recent_config = []
        recent_states = []
        recent_scores = []
        samples = random.sample(self.recent_records, batch_size)
        for sample in samples:
            config, state, score = sample
            recent_config.append(config)
            recent_states.append(state)
            recent_scores.append(score)
        return recent_config, recent_states, recent_scores

    def clear(self):
        self.recent_records.clear()
        self.memory_count = 0
