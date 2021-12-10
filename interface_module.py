# the interface module for the CSC110 Final project acts as a 'management system'

import math_module as mSim
import datetime as dt
# import map_module

class math_module_processor:
    # variables
    
    simulation_state_dict = {}

    sim_system = mSim.simulation_system()
    
    def __init__(self):
        # variables
        self.simulation_state_dict = {}
        
    def run_simulation(self, epochs: int):
        # run the simulation
        for i in range(epochs):
            self.simulation_state_dict[i] = self.sim_system.update_global_simulation()
        return self.simulation_state_dict


def main():
    # variables
    epochs = input("How many epochs would you like to run? ")
    # create a new instance of the math_module_processor class
    mm = math_module_processor()
    # run the simulation
    mm.run_simulation(epochs)
    # print the results
    
