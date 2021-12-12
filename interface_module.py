# the interface module for the CSC110 Final project acts as a 'management system'
import math_module as mSim
from math_module import Sector as Sector
import datetime as dt
import config as cfg
import map_module as map


import tkinter as tk


class math_module_processor:
    # variables
    
    simulation_state_dict = {}

    sim_system = mSim.simulation_system()
    
    def __init__(self):
        # variables
        self.simulation_state_dict = {}
        
    def run_simulation(self, epochs: int) -> dict:
        # run the simulation
        for i in range(epochs):
            self.simulation_state_dict[i] = self.sim_system.update_global_simulation()
        return self.simulation_state_dict


class graphable_sector:
    s_proportion = 0
    i_proportion = 0
    r_proportion = 0
    v_proportion = 0
    
    total_population = 0
    sector_type = ""
    
    def __init__(self, sector: Sector):
        self.s_proportion = sector.susceptible_proportion
        self.i_proportion = sector.infectious_proportion
        self.r_proportion = sector.recovered_proportion
        self.v_proportion = sector.vaccinated_proportion
        self.total_population = sector.population
        self.sector_type = sector.type


def convert_sector_info_to_mappable_information(input_dictionary: dict) -> dict:
    # variables
    dict_to_return = {}
    
    for key in input_dictionary:
        
        list_of_graphable_sectors = []
        for sector in input_dictionary[key]:
            list_of_graphable_sectors.append(graphable_sector(sector))
        dict_to_return[key] = list_of_graphable_sectors
        
    return dict_to_return


def graph_results(input_dictionary: dict, key: int):
    """
    Takes in a dictionary of the simulated results as graphical_sector objects
    and graphs them using the map_module imported. It also takes a key to plot the specific
    epoch.
    """
    map.plot_sectors(input_dictionary, key)



def main():

    # GUI
    root=tk.Tk()
    
    # setting the windows size
    root.geometry("200x200")
    
    # declaring string variable
    epochs=tk.IntVar()
    
    
    def submit():
        
        temp=epochs.get()
            
        print("Input Value: " + str(temp))
        root.destroy()
        return temp
        
    name_label = tk.Label(root, text = 'Input epochs', font=('calibre',10, 'bold'))
    
    name_entry = tk.Entry(root,textvariable = epochs, font=('calibre',10,'normal'))
    
    sub_btn=tk.Button(root,text = 'Submit', command = submit)
    
    name_label.grid(row=0,column=0)
    name_entry.grid(row=0,column=1)

    sub_btn.grid(row=2,column=1)
    
    root.mainloop()


    mm = math_module_processor()
    
    # run the simulation, returning a dictionary of the simulation results
    
    data = mm.run_simulation(epochs.get())
    
    mappable_data = convert_sector_info_to_mappable_information(data)
    

if __name__ == "__main__":
    main()
    
    
 
    
    
