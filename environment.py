import time
from multiprocessing import Process, Manager
import traci
from sumolib import checkBinary
from utils import change_traffic_light
from utils import calculate_waitsteps


class SumoEnvironment:
    def __init__(self):
        self.simulation_time = 2000

    def run_simulation(self, configuration, process_id, scores_list):
        # print('process', process_id, 'configuratoin is ', configuration)
        current_port = 8814 + process_id
        change_traffic_light(configuration, process_id)
        sumoBinary = checkBinary('sumo')
        traci.start([sumoBinary,
                     '--net-file', 'tmp/di-tech-' + str(process_id) + '.net.xml',
                     '--route-files', 'tmp/di-tech-' + str(process_id) + '.rou.xml',
                     '--begin', '0.0',
                     '--tripinfo-output', 'tmp/tripinfo-' + str(process_id) + '.xml',
                     '--no-warnings', '--no-step-log'], port=current_port)
        for timestep in range(self.simulation_time):
            traci.simulationStep()
        traci.close()
        scores_list[process_id] = calculate_waitsteps(process_id)


if __name__ == "__main__":
    env = SumoEnvironment()

    test_configuration = [
        [0, 102, 26, 39, 35],
        [12, 22, 123, 17, 38],
        [10, 30, 121, 49],
        [2, 28, 73, 34, 9, 56],
        [182, 39, 88, 73],
        [106, 37, 72, 48, 43],
        [61, 26, 89, 85]
    ]

    start_time = time.time()

    manager = Manager()
    scores_list = manager.dict()

    n_process = 8
    jobs = []
    for i in range(n_process):
        p = Process(target=env.run_simulation, args=(test_configuration, i, scores_list,))
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()

    close_time = time.time()
    print('simulation time =', close_time - start_time)

    for i in range(n_process):
        print('process ' + str(i) + ':', scores_list[i])
