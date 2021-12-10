import math
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

    susceptible_proportion, infected_proportion, recovered_proportion, vaccinated_proportion = 1.0, 0.0, 0.0, 0.0

    recovered_infected_ratio = 0
    recovered_vaccination_ratio = 0

    travelRate: float
    density: float

    cases_cumulative: int
    cases_active: int

    def __init__(self, name, population, geographic_area, longitude, latitude, type):
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

        self.cases_cumulative = 0
        self.cases_active = 0

    def __str__(self):
        
        return '{} has a population of {} and an area of {} and a density of {}'.format(self.name, self.population, self.geographic_area, self.density)

    def debug_print(self):
        print("success")

    def get_status(self):
        return '{} statistics: S == {}, I == {}, R == {}, R-vaccinated = {}'.format(self.name, self.susceptible_proportion, self.infected_proportion, self.recovered_proportion, self.vaccinated_proportion)


    def rudimentary_test(self, iter) -> None:
        # debug script
        '''
        test_city = Sector("city", 100000, 100, 10, 10, 'urban')
        test_city.susceptible_proportion = 0.99
        test_city.infected_proportion = 0.01
        test_city.rudimentary_test(test_city, 100)
        '''
        f = open('output_test.csv', 'w')
        writer = csv.writer(f)
        
        for i in range(iter):
            contact_rate_β = self.per_capita_transmission_rate * config_settings.daily_infection_rate
            
            new_infected_pop = self.infected_proportion * contact_rate_β * self.susceptible_proportion
            self.susceptible_proportion = self.susceptible_proportion - new_infected_pop
            self.recovered_proportion = self.recovered_proportion + self.infected_proportion * config_settings.global_recovery_rate
            self.infected_proportion = self.infected_proportion + new_infected_pop - (self.infected_proportion * config_settings.global_recovery_rate)
        
            writer.writerow([self.name, self.susceptible_proportion, self.infected_proportion, self.recovered_proportion])
        print("current status: S = " + str(self.susceptible_proportion) + ", I = " + str(self.infected_proportion) + ", R = " + str(self.recovered_proportion) + ", Sum: " + str(self.susceptible_proportion + self.infected_proportion + self.recovered_proportion))
        f.close()

    def calculate_SIR(self):
        # calculate the proportion of people in the Sector that are susceptible, infected, and recovered
        '''
        self.susceptible_proportion = 100.0 - self.infected_proportion - self.recovered_proportion - self.vaccinated_proportion
        self.recovered_infected_ratio = self.recovered_proportion / self.infected_proportion
        self.recovered_vaccination_ratio = self.recovered_proportion / self.vaccinated_proportion
        '''
        neighbors = self.neighborProvinces
        incoming_noninfected_transfer = 0
        incoming_infected_transfer = 0

        print("calculate_SIR called")
        # algorithm for calculating the transfer of infected individuals from neighboring provinces
        
        
        for neighbor in neighbors:
            incoming_noninfected_transfer += ((neighbor.sector_total_population) * (self.travelRate / 1000) - neighbor.sector_total_population * self.travelRate * neighbor.infected_proportion / 1000) * max(2.0, 50 / self.distance_between_this_sector_and_other_sectors[neighbor.name])
            incoming_infected_transfer += (neighbor.sector_total_population * self.travelRate * neighbor.infected_proportion / 1000) * max(2.0, 50 / self.distance_between_this_sector_and_other_sectors[neighbor.name])
            # formula description: neighbor infected population, divided by one thousand, multiplied by travel rate, multiplied by a factor that depends on the distance between the two provinces
            neighbor.susceptible_proportion -= incoming_noninfected_transfer
            neighbor.infected_proportion -= incoming_infected_transfer

        # normalize the proportions
        self.susceptible_proportion = (self.susceptible_proportion * self.sector_total_population + incoming_noninfected_transfer)/ (self.sector_total_population + incoming_noninfected_transfer + incoming_infected_transfer)
        self.infected_proportion = (self.infected_proportion * self.sector_total_population + incoming_infected_transfer)/ (self.sector_total_population + incoming_noninfected_transfer + incoming_infected_transfer)
        # a portion of individuals in the 'RECOVERED' and 'VACCINATED' groups will be infected. 

        # calculate the new infected proportion

        contact_rate_β = self.per_capita_transmission_rate * config_settings.daily_infection_rate
            
        new_infected_pop = self.infected_proportion * contact_rate_β * self.susceptible_proportion
        self.susceptible_proportion = self.susceptible_proportion - new_infected_pop
        self.recovered_proportion = self.recovered_proportion + self.infected_proportion * config_settings.global_recovery_rate
        self.infected_proportion = self.infected_proportion + new_infected_pop - (self.infected_proportion * config_settings.global_recovery_rate)
        
        recovered_individuals_infected = self.recovered_proportion * config_settings.recovered_vulnerability * self.per_capita_transmission_rate * self.susceptible_proportion
        vaccinated_individuals_infected = self.vaccinated_proportion * config_settings.vaccinated_vulnerability * self.per_capita_transmission_rate * self.susceptible_proportion

        # proportion of infected that are not from the susceptible population

        self.recovered_vaccination_ratio = recovered_individuals_infected / self.sector_total_population
        self.recovered_infected_ratio = recovered_individuals_infected / self.sector_total_population

        # after taking in this data, calculate the new S/I/R values for this individual province.
        
        self.recovered_proportion -= recovered_individuals_infected
        self.vaccinated_proportion -= vaccinated_individuals_infected
        self.infected_proportion += recovered_individuals_infected + vaccinated_individuals_infected
       
        # a certain proportion of the infected population will be vaccinated; when these individuals recover, they move back into the vaccinated population.

        self.vaccinated_proportion += self.recovered_vaccination_ratio * config_settings.global_recovery_rate - self.recovered_proportion * config_settings.global_recovery_fall_rate

        if self.vaccination_program == True:
            self.local_vaccination_rollout_rate = config_settings.global_vaccination_rollout_rate * max(1.0, self.density / 100)
            # vaccination converts recovered and susceptible individuals to 'vaccinated'
            self.vaccinated_proportion += self.regional_vaccination_rollout_rate * (self.susceptible_proportion + self.recovered_proportion) 


    def update_sector_sim(self) -> None:
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
        else:
            print('Error: invalid policy')

        # calculate the new S/I/R values for this individual province, including effects from incoming transfers.
        
        self.calculate_SIR()


class simulation_system:
    system_sectors = []
    current_time = dt.datetime(2020, 1, 1)
    
    def __init__(self) -> None:
        self.system_sectors = setup()
        
    def __status__(self) -> None:
        return '{}'.format(self.system_sectors)

    def update_global_simulation(self) -> None:
        for sector in self.system_sectors:
            sector.update_sector_sim()
        self.current_time += dt.timedelta(days=1)

    def compute_and_return_sector_data(self) -> dict():
        sector_data = {sector:(sector.susceptible_proportion, sector.infected_proportion, sector.recovered_proportion, sector.vaccinated_proportion) for sector in self.system_sectors}
        return sector_data
    
    def debug_print(self) -> None:
        print(self.current_time)
        for sector in self.system_sectors:
            print(sector.name)
        print()


def setup() -> list[Sector]:
    # Create a list of cities
    regions = []
    with open('City_data_config.csv', 'r') as file:
        reader = csv.reader(file)

        iterCount = 0
        for row in reader:
            if iterCount > 0:
                print(row)
                new_sector = Sector(row[0], int(row[1]), int(row[2]), float(row[3]), float(row[4]), row[5])
                
                new_sector.distance_between_this_sector_and_other_sectors = {sect: calculate_distance_between_Sectors(new_sector, sect) for sect in regions}
                print(new_sector.density)
                regions.append(new_sector)
            iterCount += 1
    return regions


def calculate_distance_between_Sectors(province1: Sector , province2: Sector):
    # calculate the distance between two Sectors
    distance = math.sqrt((province1.coordinates[0] - province2.coordinates[0]) ** 2 + (province1.coordinates[1] - province2.coordinates[1]) ** 2)
    return distance


def updateSimulation(region: Sector, policy: str):

    # implements simulated policy changes
    if policy == 'lockdown':
        region.per_capita_transmission_rate = region.per_capita_transmission_rate * 0.25
        region.travelRate = region.travelRate / (2 + region.density / 100)
    elif policy == 'travel ban':
        region.travelRate = region.travelRate * 0.1
    elif policy == 'open':
        region.travelRate = region.density / 100
        region.per_capita_transmission_rate = max(2.0 / 5 * math.log(region.density / 100.0, 2.71828), 1.0) * cfg.daily_infection_rate
    elif policy == 'recover':
        region.per_capita_transmission_rate = 0.0
    else:
        print('Error: invalid policy')


    # calculate the transfer of infected individuals from neighboring provinces

    neighbors = region.neighborProvinces
    incoming_noninfected_Transfer = 0
    incomingInfectedTransfer = 0

    # algorithm for calculating the transfer of infected individuals from neighboring provinces
    
    for neighbor in neighbors:
        incoming_noninfected_Transfer += ((neighbor.totalPopulation) * (region.travelRate / 1000) - neighbor.totalPopulation * region.travelRate * neighbor.infected_proportion / 1000) * max(2.0, 50 / calculate_distance_between_Sectors(region, neighbor))
        incomingInfectedTransfer += (neighbor.totalPopulation * region.travelRate * neighbor.infected_proportion / 1000) * max(2.0, 50 / calculate_distance_between_Sectors(region, neighbor))
        # formula description: neighbor infected population, divided by one thousand, multiplied by travel rate, multiplied by a factor that depends on the distance between the two provinces
        neighbor.suseptible_proportion -= incoming_noninfected_Transfer
        neighbor.infected_proportion -= incomingInfectedTransfer

    
    region.susceptible_proportion = (region.susceptible_proportion + incoming_noninfected_Transfer) / region.totalPopulation + (region.recovered_proportion * cfg.recovered_vulnerability + region.vaccinated_proportion * cfg.vaccinated_vulnerability)

    # a portion of individuals in the 'RECOVERED' and 'VACCINATED' groups will be infected. 

    # calculate the new infected proportion

    susceptible_individuals_infected = region.infected_proportion * region.per_capita_transmission_rate * region.susceptible_proportion + incomingInfectedTransfer
    recovered_individuals_infected = region.recovered_proportion * cfg.recovered_vulnerability * region.per_capita_transmission_rate * region.susceptible_proportion
    vaccinated_individuals_infected = region.vaccinated_proportion * cfg.vaccinated_vulnerability * region.per_capita_transmission_rate * region.susceptible_proportion

    # proportion of infected that are not from the susceptible population

    region.recovered_vaccination_ratio = recovered_individuals_infected / region.totalPopulation
    region.recovered_infected_ratio = recovered_individuals_infected / region.totalPopulation

    # after taking in this data, calculate the new S/I/R values for this individual province.

    region.susceptible_proportion -= susceptible_individuals_infected + recovered_individuals_infected + vaccinated_individuals_infected

    region.infected_proportion += susceptible_individuals_infected + recovered_individuals_infected + vaccinated_individuals_infected - region.infected_proportion * cfg.global_recovery_rate
   
    region.recovered_proportion += (region.infected_proportion - region.recovered_vaccination_ratio) * cfg.global_recovery_rate - region.recovered_proportion * cfg.global_recovery_fall_rate

    region.vaccinated_proportion -= region.vaccinated_proportion * cfg.global_vaccination_fall_rate

    region.susceptible_proportion += region.susceptible_proportion - susceptible_individuals_infected - region.recovered_proportion * cfg.global_recovery_fall_rate + region.vaccinated_proportion * cfg.global_vaccination_fall_rate

    # update cases

    region.cases_cumulative = region.infected_proportion * region.population
    region.cases_active = (region.infected_proportion - region.recovered_proportion) * region.population

    # a certain proportion of the infected population will be vaccinated; when these individuals recover, they move back into the vaccinated population.

    region.vaccinated_proportion += region.recovered_vaccination_ratio * cfg.global_recovery_rate - region.recovered_proportion * cfg.global_recovery_fall_rate


    if region.vaccination_program == True:
        regional_vaccination_rollout_rate = cfg.global_vaccination_rollout_rate * max(1.0, region.density / 100)
        # vaccination converts recovered and susceptible individuals to 'vaccinated'
        region.vaccinated_proportion += regional_vaccination_rollout_rate * (region.susceptible_proportion + region.recovered_proportion) 
    


def main():
    date = dt.datetime(2020, 1, 1)
    sim = simulation_system()


if __name__ == '__main__':
    main()
