import math
from os import system
import config as config_settings
import csv
import datetime as dt


class Sector():
    # A sector represents a city.
    
    name = "placeholder_name"
    population = 0
    geographic_area = 0
    longitude = 0.0
    latitude = 0.0
    coordinates = ()
    type = "placeholder_type"
    
    per_capita_transmission_rate: float
    vaccination_program = False
    policy = "placeholder_policy"

    susceptible_proportion, infectious_proportion, recovered_proportion, vaccinated_proportion = 1.0, 0.0, 0.0, 0.0

    recovered_infected_ratio = 0
    recovered_vaccination_ratio = 0

    travelRate: float
    density: float

    neighborProvinces = {}
    distance_to_neighbors = {}
    
    
    def __init__(self, name, population, geographic_area, longitude, latitude, type) -> None:
        self.name = name
        self.population = population
        self.geographic_area = geographic_area # kilometers squared
        self.longitude = longitude
        self.latitude = latitude
        self.coordinates = (longitude, latitude)
        self.type = type # large urban, urban, suburban, rural

        self.density = float(population) / float(geographic_area)

        self.travelRate = self.density / 100.0
        # travelRate is the likelihood that people from neighboring Sectors will travel to this Sector. For example, people are more likely to visit densely 
        # populated areas like cities. 

        # per_capita_transmission_rate is the rate at which people in a Sector will spread the virus; it is the product of the baseline infection rate and a factor adjusting for the population density
        self.per_capita_transmission_rate = max(math.log(self.density, 10), 0.6)
        # the infection rate is the product of the r0 value and the rate of contact within a population. These arbitrary values are chosen to limit the simulated spread of the virus to a reasonable level.
        

    def initialize_neighbors(self, neighbor_list) -> None:
        # initialize the neighbor list for this sector
        for neighbor in neighbor_list:
            dist = calculate_distance_between_Sectors(self, neighbor[0]) 
            if self.name != neighbor[0] and dist <= 500000:
                self.neighborProvinces[neighbor] = dist
    

    def __str__(self):
        return '{} has a population of {} and an area of {} and a density of {}'.format(self.name, self.population, self.geographic_area, self.density)


    def debug_print(self):
        print("success")


    def get_status(self):
        return '{} statistics: S == {}, I == {}, R == {}, R-vaccinated = {}'.format(self.name, self.susceptible_proportion, self.infectious_proportion, self.recovered_proportion, self.vaccinated_proportion)


    def rudimentary_test(self, iter) -> None:
        # debug script
        '''
        test_city = Sector("city", 100000, 100, 10, 10, 'urban')
        test_city.susceptible_proportion = 0.99
        test_city.infectious_proportion = 0.01
        test_city.rudimentary_test(test_city, 100)
        '''
        f = open('output_test.csv', 'w')
        writer = csv.writer(f)
        
        for i in range(iter):
            contact_rate_β = self.per_capita_transmission_rate * config_settings.daily_infection_rate
            
            new_infected_pop = self.infectious_proportion * contact_rate_β * self.susceptible_proportion
            self.susceptible_proportion = self.susceptible_proportion - new_infected_pop
            self.recovered_proportion = self.recovered_proportion + self.infectious_proportion * config_settings.global_recovery_rate
            self.infectious_proportion = self.infectious_proportion + new_infected_pop - (self.infectious_proportion * config_settings.global_recovery_rate)
        
            writer.writerow([self.name, self.susceptible_proportion, self.infectious_proportion, self.recovered_proportion])
        print("current status: S = " + str(self.susceptible_proportion) + ", I = " + str(self.infectious_proportion) + ", R = " + str(self.recovered_proportion) + ", Sum: " + str(self.susceptible_proportion + self.infectious_proportion + self.recovered_proportion))
        f.close()


    def calculate_SIR(self):
        # MUTATOR: calculate the NEW proportion of people in the Sector that are susceptible, infected, and recovered. 
        '''
        self.susceptible_proportion = 100.0 - self.infectious_proportion - self.recovered_proportion - self.vaccinated_proportion
        self.recovered_infected_ratio = self.recovered_proportion / self.infectious_proportion
        self.recovered_vaccination_ratio = self.recovered_proportion / self.vaccinated_proportion
        '''
        neighbors = self.neighborProvinces
        incoming_noninfected_transfer = 0
        incoming_infected_transfer = 0

        print("calculate_SIR called")
        # algorithm for calculating the transfer of infected individuals from neighboring provinces
        
        
        for neighbor in neighbors:
            incoming_noninfected_transfer += ((neighbor.population) * (self.travelRate / 1000) - neighbor.population * self.travelRate * neighbor.infectious_proportion / 1000) * max(2.0, 50 / self.distance_to_neighbors[neighbor.name])
            incoming_infected_transfer += (neighbor.population * self.travelRate * neighbor.infectious_proportion / 1000) * max(2.0, 50 / self.distance_to_neighbors[neighbor.name])
            # formula description: neighbor infected population, divided by one thousand, multiplied by travel rate, multiplied by a factor that depends on the distance between the two provinces
            neighbor.susceptible_proportion -= incoming_noninfected_transfer
            neighbor.infectious_proportion -= incoming_infected_transfer

        # normalize the proportions
        self.susceptible_proportion = (self.susceptible_proportion * self.population + incoming_noninfected_transfer)/ (self.population + incoming_noninfected_transfer + incoming_infected_transfer)
        self.infectious_proportion = (self.infectious_proportion * self.population + incoming_infected_transfer)/ (self.population + incoming_noninfected_transfer + incoming_infected_transfer)
        # a portion of individuals in the 'RECOVERED' and 'VACCINATED' groups will be infected. 

        # calculate the new infected proportion

        contact_rate_β = self.per_capita_transmission_rate * config_settings.daily_infection_rate
            
        new_infected_pop = self.infectious_proportion * contact_rate_β * self.susceptible_proportion
        self.susceptible_proportion = self.susceptible_proportion - new_infected_pop
        self.recovered_proportion = self.recovered_proportion + self.infectious_proportion * config_settings.global_recovery_rate
        self.infectious_proportion = self.infectious_proportion + new_infected_pop - (self.infectious_proportion * config_settings.global_recovery_rate)
        
        recovered_individuals_infected = self.recovered_proportion * config_settings.recovered_vulnerability * self.per_capita_transmission_rate * self.susceptible_proportion
        vaccinated_individuals_infected = self.vaccinated_proportion * config_settings.vaccinated_vulnerability * self.per_capita_transmission_rate * self.susceptible_proportion

        # proportion of infected that are not from the susceptible population

        self.recovered_vaccination_ratio = recovered_individuals_infected / self.population
        self.recovered_infected_ratio = recovered_individuals_infected / self.population

        # after taking in this data, calculate the new S/I/R values for this individual province.
        
        self.recovered_proportion -= recovered_individuals_infected
        self.vaccinated_proportion -= vaccinated_individuals_infected
        self.infectious_proportion += recovered_individuals_infected + vaccinated_individuals_infected
       
        # a certain proportion of the infected population will be vaccinated; when these individuals recover, they move back into the vaccinated population.

        self.vaccinated_proportion += self.recovered_vaccination_ratio * config_settings.global_recovery_rate

        # some proportion of the susceptible and vaccinated populations will return to the susceptible population, to simulate
        # the diminishing nature of immunity.
        
        self.recovered_proportion -= self.recovered_proportion * config_settings.global_recovery_fall_rate
        self.vaccinated_proportion -= self.vaccinated_proportion * config_settings.global_vaccination_fall_rate

        self.susceptible_proportion += self.recovered_proportion * config_settings.global_recovery_fall_rate + self.vaccinated_proportion * config_settings.global_vaccination_fall_rate

        
        if self.vaccination_program == True:
            self.local_vaccination_rollout_rate = config_settings.global_vaccination_rollout_rate * max(1.0, self.density / 100)
            # vaccination converts recovered and susceptible individuals to 'vaccinated'
            while self.vaccinated_proportion < 0.8:
                self.vaccinated_proportion += self.local_vaccination_rollout_rate * (self.susceptible_proportion + self.recovered_proportion) 
                self.susceptible_proportion -= self.local_vaccination_rollout_rate * (self.susceptible_proportion)
                self.recovered_proportion -= self.local_vaccination_rollout_rate * (self.recovered_proportion)


    def update_sector_sim(self) -> None:
        '''
        Implements simulated self.policy changes through mutating internal values
        >>> city = Sector(name='Toronto City', population=3000000, geographic_area=630, \
            longitude=43.6532, latitude=-79.3832, type='large urban')
        >>> city.policy = 'travel ban'
        >>> math.isclose(city.travelRate, 47.6190476)
        True
        >>> city.update_sector_sim()
        >>> math.isclose(city.travelRate, 4.76190476)
        True
        '''
        # implements simulated self.policy changes through mutating internal values
        if self.policy == 'lockdown':
            self.per_capita_transmission_rate = self.per_capita_transmission_rate * 0.25
            self.travelRate = self.travelRate / (2 + self.density / 100)
        elif self.policy == 'travel ban':
            self.travelRate = self.travelRate * 0.1
        elif self.policy == 'open':
            self.travelRate = self.density / 100
        elif self.policy == 'recover':
            self.per_capita_transmission_rate = 0.0
        # else:
            # print('Error: invalid policy')

        # calculate the new S/I/R values for this individual province, including effects from incoming transfers.
        
        self.calculate_SIR()


class simulation_system:
    system_sectors = []
    current_time = dt.datetime(2020, 1, 1)
    
    province_city_population: int
    total_s_proportion = 1.0
    total_i_proportion = 0.0
    total_r_proportion = 0.0
    total_v_proportion = 0.0
    
    def __init__(self) -> None:
        self.system_sectors = sector_setup()
        for sector in self.system_sectors:
            sector.initialize_neighbors(self.system_sectors)
            self.province_city_population += sector.population

    def update_global_simulation(self) -> list():
        for sector in self.system_sectors:
            sector.update_sector_sim()
        self.current_time += dt.timedelta(days=1)
        
        self.total_s_proportion = sum([sector.susceptible_proportion for sector in self.system_sectors])/self.province_city_population
        self.total_i_proportion = sum([sector.infectious_proportion for sector in self.system_sectors])/self.province_city_population
        self.total_r_proportion = sum([sector.recovered_proportion for sector in self.system_sectors])/self.province_city_population
        self.total_v_proportion = sum([sector.vaccinated_proportion for sector in self.system_sectors])/self.province_city_population
        return self.system_sectors
        

    def compute_and_return_sector_data(self) -> dict():
        sector_data = {sector:(sector.susceptible_proportion, sector.infectious_proportion, sector.recovered_proportion, sector.vaccinated_proportion) for sector in self.system_sectors}
        return sector_data

    def debug_print(self) -> None:
        print(self.current_time)
        for sector in self.system_sectors:
            print(sector.name)
        print()


def calculate_distance_between_Sectors(province1: Sector , province2: Sector) -> float:
    '''
    Return the distance between two Sectors in metres
    Formula taken from https://www.movable-type.co.uk/scripts/latlong.html and translated to Python
    >>> P1 = Sector(name='Toronto City', population=3000000, geographic_area=630, \
            longitude=43.6532, latitude=-79.3832, type='large urban')
    >>> P2 = Sector(name='Ottawa-Gatineau', population=1000000, geographic_area=380, \
            longitude=45.4215, latitude=-75.6972, type='large urban')
    >>> calculate_distance_between_Sectors(P1, P2)
    412006.926518153
    '''
    R = 6371000
    lat1 = province1.latitude * math.pi/180
    lat2 = province2.latitude * math.pi/180
    lat_difference = (province2.latitude-province1.latitude) * math.pi/180
    long_difference = (province2.longitude-province1.longitude) * math.pi/180

    a = math.sin(lat_difference/2) * math.sin(lat_difference/2) + math.cos(lat1) * math.cos(lat2) * math.sin(long_difference/2) * math.sin(long_difference/2)
    c = 2 * math.atan(math.sqrt(a) / math.sqrt(1-a))

    return R * c

    # Old Method
    # distance = math.sqrt((province1.coordinates[0] - province2.coordinates[0]) ** 2 + (province1.coordinates[1] - province2.coordinates[1]) ** 2)
    # return distance


def sector_setup() -> list[Sector]:
    regions = []
    with open('City_data_config.csv', 'r') as file:
        reader = csv.reader(file)

        iterCount = 0
        for row in reader:
            if iterCount > 0:
                print(row)
                new_sector = Sector(row[0], int(row[1]), int(row[2]), float(row[3]), float(row[4]), row[5])
                new_sector.distance_to_neighbors = {sect: calculate_distance_between_Sectors(new_sector, sect) for sect in regions}
                print(new_sector.density)
                regions.append(new_sector)
            iterCount += 1
    
    return regions

def main():
    # Use only for testing
    date = dt.datetime(2020, 1, 1)
    sim = simulation_system()


if __name__ == '__main__':
    main()
