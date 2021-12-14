# the interface module for the CSC110 Final project acts as a 'management system'
import math_module as mSim
from math_module import Sector as Sector
import matplotlib.pyplot as plt
import datetime as dt
import config as cfg
import map_module as map


import tkinter as tk


class math_module_processor:
    # variables
    
    simulation_state_dict = {}
    
    sim_system = mSim.simulation_system()
    
    provincial_stats = {}
    
    def __init__(self):
        # variables
        self.simulation_state_dict = {}
        self.provincial_stats = {}
        
    def run_simulation(self, epochs: int, vaccination_start: int):
        # run the simulation
        for i in range(epochs):
            if i == vaccination_start:
                self.sim_system.initialize_vaccination()
            self.simulation_state_dict[i] = self.sim_system.update_global_simulation()
            self.provincial_stats[i] = self.sim_system.fetch_global_stats()
        return (self.simulation_state_dict, self.provincial_stats)


class graphable_sector:
    s_proportion = 0
    i_proportion = 0
    r_proportion = 0
    v_proportion = 0
    longitude = 0
    latitude = 0
    density = 0
    total_population = 0
    sector_type = ""
    
    def __init__(self, sector: Sector):
        self.s_proportion = sector.susceptible_proportion
        self.i_proportion = sector.infectious_proportion
        self.r_proportion = sector.recovered_proportion
        self.v_proportion = sector.vaccinated_proportion
        self.total_population = sector.population
        self.sector_type = sector.type
        self.longitude = sector.longitude
        self.latitude = sector.latitude
        self.density = sector.density


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
    and graphs them using the map_module imported.
    """
    map.plot_sectors(input_dictionary[key])




def main():

    # GUI
    root=tk.Tk()
    
    # setting the windows size
    root.geometry("400x200")
    
    # declaring string variable
    epochs=tk.IntVar()
    vaccination_startDate = tk.IntVar()
    map_of_day = tk.IntVar()
    
    def submit():
        
        epoch_counter=epochs.get()
        v_day = vaccination_startDate.get()
        m_o_d = map_of_day.get()
        print("Input Value: " + str(epoch_counter))
        root.destroy()
        return (epoch_counter, v_day)
        
    name_label = tk.Label(root, text = 'Input epochs', font=('calibre',10, 'bold'))
    
    name_entry = tk.Entry(root,textvariable = epochs, font=('calibre',10,'normal'))
    
    name_label_2 = tk.Label(root, text = 'Input vaccination startdate (input -1 to disable)', font=('calibre',10, 'bold'))
    
    name_entry_2 = tk.Entry(root,textvariable = vaccination_startDate, font=('calibre',10,'normal'))

    name_label_3 = tk.Label(root, text='Pick a day to access its map(Must be smaller than Input Epoch)', font=('calibre', 10, 'bold'))

    name_entry_3 = tk.Entry(root, textvariable=map_of_day, font=('calibre', 10, 'normal'))
    
    sub_btn=tk.Button(root,text = 'Submit', command = submit)
    
    name_label.grid(row=0,column=0)
    name_entry.grid(row=0,column=1)
    name_label_2.grid(row=1,column=0)
    name_entry_2.grid(row=1,column=1)
    name_label_3.grid(row=2,column=0)
    name_entry_3.grid(row=2, column=1)
    sub_btn.grid(row=3,column=1)
    
    root.mainloop()

    mm = math_module_processor()
    
    # run the simulation, returning a dictionary of the simulation results
    
    # Initialize infection
    
    mm.sim_system.initialize_infection("Toronto City", 0.05)
        
    tuple_of_results = mm.run_simulation(epochs.get(), vaccination_startDate.get())
    
    sector_data = tuple_of_results[0]
    
    global_data = tuple_of_results[1]
    print(global_data)
    
    mappable_data = convert_sector_info_to_mappable_information(sector_data)
    
    xAxis = [key for key in global_data]
    yAxis = [global_data[key][0] for key in global_data]
    yAxis2 = [global_data[key][1] for key in global_data]
    yAxis3 = [global_data[key][2] for key in global_data]
    yAxis4 = [global_data[key][3] for key in global_data]
    
    plt.plot(xAxis,yAxis, label = 'susceptible_prop')
    plt.plot(xAxis,yAxis2, label = 'infectious_prop')
    plt.plot(xAxis,yAxis3, label = 'recovered_prop')
    plt.plot(xAxis,yAxis4, label = 'vaccinated_prop')    
    
    plt.title('Compartmental Modeling of SIR stats in Ontario')
    plt.xlabel('Date (epoch)')
    plt.ylabel('Proportion')
    plt.legend()
    plt.show()
    graph_results(mappable_data, map_of_day.get())

if __name__ == "__main__":
    main()
 
    
    
