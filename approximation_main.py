#import sys
#sys.path.append('/usr/share/sumo/tools')
import pickle
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Process, Manager
from approximation_environment import SumoEnvironment
from approximation_generator import ConfigGenerator
from approximation_memory import Memory
from approximation_model import state2score

N_PROCESS = 16
BATCH_SIZE = 128
N_EPOCH = 1
VAL_RATE = 0.2

env = SumoEnvironment()
G = ConfigGenerator(cycle=200)
memory = Memory(2000)


def sampling(process_id, samplings):
    config = G.generate_config()
    state, score = env.run_simulation(config, process_id)
    samplings[process_id] = [config, state, score]


def main():
    record_id = 0
    manager = Manager()
    function_f = state2score()

    function_f.summary()
    n_iteration = []
    train_loss = []
    val_loss =[]
    iter = 0

    while True:
        # multi-process to sample
        jobs = []
        samplings = manager.dict()
        for i in range(N_PROCESS):
            p = Process(target=sampling, args=(i, samplings, ))
            jobs.append(p)
            p.start()
        for p in jobs:
            p.join()

        for i in range(N_PROCESS):
            config, state, score = samplings[i]
            if memory.memory_count < memory.maxlen:
                memory.append(config, state, score)

        if memory.memory_count % 32 == 0:
            print('current memory size:', memory.memory_count)

        # experience is enough to train
        if memory.memory_count % BATCH_SIZE == 0:
            configs, states, scores = memory.sample(BATCH_SIZE)
            # train the funciton f: states -> scores
            #"""
            history = function_f.fit(np.array(states), np.array(scores),
                                     batch_size=BATCH_SIZE, epochs=N_EPOCH, validation_split=VAL_RATE)
            n_iteration.append(iter)
            train_loss.append(history.history['loss'][0])
            val_loss.append(history.history['val_loss'][0])
            iter += 1

            plt.figure()
            plt.plot(n_iteration, train_loss, label='train')
            plt.plot(n_iteration, val_loss, label='val')
            plt.ylabel('loss')
            plt.xlabel('iteration')
            plt.grid()
            plt.title('loss curve')
            plt.legend()
            plt.savefig('learning_curve.png', dpi=300)
            #"""
            # log out
            """
            for i in range(BATCH_SIZE):
                print('experience #' + str(i + 1))
                print('config:', configs[i])
                print('state:', states[i])
                print('score:', scores[i])
            """
        # experience is too much for memory, save and clear
        if memory.memory_count == memory.maxlen:
            print('memory is full, save and reset to empty...')
            pickle.dump(memory.recent_records, open('tmp/memory-' + str(record_id) + '.pkl', 'wb'))
            record_id += 1
            memory.clear()


if __name__ == '__main__':
    main()
