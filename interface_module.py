# the interface module for the CSC110 Final project acts as a 'management system'
import math_module as mSim
from math_module import Sector as Sector
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


class graphable_sector:
    s_proportion = 0
    i_proportion = 0
    r_proportion = 0
    v_proportion = 0
    sector_type = ""
    
    def __init__(self, sector: Sector):
        self.s_proportion = sector.susceptible_proportion
        self.i_proportion = sector.infectious_proportion
        self.r_proportion = sector.recovered_proportion
        self.v_proportion = sector.vaccinated_proportion
        self.sector_type = sector.type


def convert_sector_info_to_mappable_information(input_dictionary: dict) -> dict:
    # variables
    dict_to_return = {}
    
    for key in input_dictionary:
        dict_to_return[key] = graphable_sector(input_dictionary[key])
        
    return dict_to_return


def graph_results(input_dictionary: dict):
    """
    Takes in a dictionary of the simulated results as graphical_sector objects
    and graphs them using the map_module imported.
    """
    return None


def main():
    # variables
    epochs = input("How many epochs would you like to run? ")
    # create a new instance of the math_module_processor class
    mm = math_module_processor()
    # run the simulation
    mm.run_simulation(epochs)
    # print the results
    
