import time
import traci
from sumolib import checkBinary
from approximation_utils import change_traffic_light
from approximation_utils import calculate_waitsteps


class SumoEnvironment:
    def __init__(self):
        self.simulation_time = 2000
        self.edge_list = []
        for edge_id in range(1, 22 + 1):
            self.edge_list.append('e' + str(edge_id) + '0')
            self.edge_list.append('e' + str(edge_id) + '1')
        self.vehicles = {edge: 0 for edge in self.edge_list}
        self.mean_speed = {edge: 0.0 for edge in self.edge_list}
        self.occupancy = {edge: 0.0 for edge in self.edge_list}
        self.waiting_time = {edge: 0.0 for edge in self.edge_list}

    def run_simulation(self, configuration, process_id=0):
        current_port = 8814 + process_id + 10
        change_traffic_light(configuration, process_id)
        sumoBinary = checkBinary('sumo')
        traci.start([sumoBinary,
                     '--net-file', 'tmp/di-tech-' + str(process_id) + '.net.xml',
                     '--route-files', 'tmp/di-tech-' + str(process_id) + '.rou.xml',
                     '--begin', '0.0',
                     '--tripinfo-output', 'tmp/tripinfo-' + str(process_id) + '.xml',
                     '--no-warnings', '--no-step-log'], port=current_port)

        states = []

        # run sumo simulation
        for timestep in range(self.simulation_time):
            if timestep % 10 == 0:
                state = []
                for edge in self.edge_list:
                    state.append(self.vehicles[edge])
                    state.append(self.mean_speed[edge])
                    state.append(self.occupancy[edge])
                    state.append(self.waiting_time[edge])
                states.append(state)

                self.vehicles = {edge: 0 for edge in self.edge_list}
                self.mean_speed = {edge: 0.0 for edge in self.edge_list}
                self.occupancy = {edge: 0.0 for edge in self.edge_list}
                self.waiting_time = {edge: 0.0 for edge in self.edge_list}

            traci.simulationStep()
            for edge in self.edge_list:
                self.vehicles[edge] += traci.edge.getLastStepVehicleNumber(edge)
                self.mean_speed[edge] += traci.edge.getLastStepMeanSpeed(edge)
                self.occupancy[edge] += traci.edge.getLastStepOccupancy(edge)
                self.waiting_time[edge] += traci.edge.getWaitingTime(edge)
        traci.close()

        return states, calculate_waitsteps(process_id)


if __name__ == '__main__':
    env = SumoEnvironment()
    tls_config = [[0, 102, 26, 39, 35], [12, 22, 523, 17, 38], [10, 30, 121, 49], [2, 28, 73, 34, 9, 56],
                  [182, 39, 88, 73], [106, 37, 72, 48, 43], [61, 26, 89, 85]]

    start_time = time.time()
    states, wait_steps = env.run_simulation(tls_config)
    end_time = time.time()
    print('simulation time:', end_time - start_time)
    print('waitSteps:', wait_steps)
    print('states size:', len(states))
