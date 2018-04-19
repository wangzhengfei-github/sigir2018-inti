import time
import traci
from sumolib import checkBinary
from serial_utils import change_traffic_light
from serial_utils import calculate_waitsteps


class SumoEnvironment:
    def __init__(self):
        self.simulation_time = 2000

    def run_simulation(self, configuration):
        change_traffic_light(configuration)
        sumoBinary = checkBinary('sumo')
        traci.start([sumoBinary,
                     '--net-file', 'tmp/di-tech.net.xml',
                     '--route-files', 'tmp/di-tech.rou.xml',
                     '--begin', '0.0',
                     '--tripinfo-output', 'tmp/tripinfo.xml',
                     '--no-warnings', '--no-step-log'])
        for timestep in range(self.simulation_time):
            traci.simulationStep()
        traci.close()
        return calculate_waitsteps()


if __name__ == "__main__":
    env = SumoEnvironment()

    test_configuration = [
        [0, 111, 9, 43, 37], [22, 28, 121, 13, 38], [0, 18, 104, 36], [10, 34, 75, 31, 19, 41], [134, 48, 89, 63],
        [105, 35, 67, 52, 46], [52, 30, 96, 74]
    ]

    start_time = time.time()

    score = env.run_simulation(test_configuration)

    close_time = time.time()
    print('simulation time =', close_time - start_time)

    print('score:', score)
