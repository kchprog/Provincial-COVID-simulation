import math
from config import *

class sector():
    # infection_rate is the rate at which people in a sector will spread the virus
    per_capita_transmission_rate = 0

    vaccination_program = False

    name, totalPopulation, density, type = '', 0, 0, "not set"

    susceptible_proportion, infected_proportion, recovered_proportion, vaccinated_proportion = 100.0, 0.0, 0.0, 0.0

    recovered_infected_ratio = 0
    recovered_vaccination_ratio = 0

    coordinates = (0, 0)
    travelRate = 0.0

    density = 0.0

    def __init__(self, name, population, geographic_area, coordinates, type):
        self.name = name
        self.population = population
        self.geographic_area = geographic_area # kilometers squared
        self.type = type # large urban, urban, suburban, rural

        self.density = population / self.geographic_area

        self.travelRate = self.density / 100
        # travelRate is the likelihood that people from neighboring provinces will travel to this sector. For example, people are more likely to visit densely 
        # populated areas like cities.

        self.coordinates = coordinates
        # per_capita_transmission_rate is the rate at which people in a sector will spread the virus; it is the product of the baseline infection rate and a factor adjusting for the population density
        self.per_capita_transmission_rate = max(2.0 / 5 * math.log(self.density / 100.0, 2.71828), 1.0) * daily_infection_rate
        # the infection rate is the product of the r0 value and the rate of contact within a population. These arbitrary values are chosen to limit the simulated spread of the virus to a reasonable level.

    def __str__(self):
        return '{} has a population of {} and an area of {} and a density of {}'.format(self.name, self.population, self.geographic_area, self.density)

    def __status__(self):
        return '{} statistics: S == {}, I == {}, R == {}, R-vaccinated = {}'.format(self.name, self.susceptible_proportion, self.infected_proportion, self.recovered_proportion, self.vaccinated_proportion)


def setup():
    # Create a list of provinces
    regions = []
    regions.append(sector('Toronto City', 3000000, 630, [], "large urban"))
    regions.append(sector('Ottawa-Gatineau', 1000000, 380, [], "large urban"))
    regions.append(sector('Hamilton', 700000, 1100, [], "suburban"))
    regions.append(sector('Kitchener', 	242000, 137, [], "large urban"))
    regions.append(sector('London', 400000, 420, [], "large urban"))
    regions.append(sector('Oshawa', 200000, 420, [], "urban"))
    regions.append(sector('Windsor', 230000, 150, [], "urban"))

    regions.append(sector('St. Catharines', 140000, 100, [], "urban"))

    regions.append(sector('Regional Municipality of Niagara', 300000, 1700, [], "suburban"))
    regions.append(sector('Barrie', 150000, 100, [], "urban"))
    regions.append(sector('Kingston', 140000, 450, [], "urban"))

    regions.append(sector('Milton', 100000, 366, [], "urban"))
    regions.append(sector('Thunder Bay', 110000, 450, [], "urban"))
    regions.append(sector('Sudbury', 165000, 350, [], "urban"))

    regions.append(sector('Peterborough', 85000, 65, [], "urban"))
    regions.append(sector('Guelph', 135000, 90, [], "urban"))

    regions.append(sector('Greater Toronto Area', 3000000, 7200, [], "suburban"))
    
    return regions


def calculate_distance_between_sectors(province1: sector , province2: sector):
    # calculate the distance between two sectors
    distance = math.sqrt((province1.coordinates[0] - province2.coordinates[0]) ** 2 + (province1.coordinates[1] - province2.coordinates[1]) ** 2)
    return distance


def updateSimulation(region: sector, policy: str):

    # implements simulated policy changes
    if policy == 'lockdown':
        region.per_capita_transmission_rate = region.per_capita_transmission_rate * 0.25
        region.travelRate = region.travelRate / (2 + region.density / 100)
    elif policy == 'travel ban':
        region.travelRate = region.travelRate * 0.1
    elif policy == 'open':
        region.travelRate = region.density / 100
        region.per_capita_transmission_rate = max(2.0 / 5 * math.log(region.density / 100.0, 2.71828), 1.0) * daily_infection_rate
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
        incoming_noninfected_Transfer += ((neighbor.totalPopulation) * (region.travelRate / 1000) - neighbor.totalPopulation * region.travelRate * neighbor.infected_proportion / 1000) * max(2.0, 50 / calculate_distance_between_sectors(region, neighbor))
        incomingInfectedTransfer += (neighbor.totalPopulation * region.travelRate * neighbor.infected_proportion / 1000) * max(2.0, 50 / calculate_distance_between_sectors(region, neighbor))
        # formula description: neighbor infected population, divided by one thousand, multiplied by travel rate, multiplied by a factor that depends on the distance between the two provinces
        neighbor.suseptible_proportion -= incoming_noninfected_Transfer
        neighbor.infected_proportion -= incomingInfectedTransfer

    
    region.susceptible_proportion = (region.susceptible_proportion + incoming_noninfected_Transfer) / region.totalPopulation + (region.recovered_proportion * recovered_vulnerability + region.vaccinated_proportion * vaccinated_vulnerability)

    # a portion of individuals in the 'RECOVERED' and 'VACCINATED' groups will be infected. 

    # calculate the new infected proportion

    susceptible_individuals_infected = region.infected_proportion * region.per_capita_transmission_rate * region.susceptible_proportion + incomingInfectedTransfer
    recovered_individuals_infected = region.recovered_proportion * recovered_vulnerability * region.per_capita_transmission_rate * region.susceptible_proportion
    vaccinated_individuals_infected = region.vaccinated_proportion * vaccinated_vulnerability * region.per_capita_transmission_rate * region.susceptible_proportion

    # proportion of infected that are not from the susceptible population

    region.recovered_vaccination_ratio = recovered_individuals_infected / region.totalPopulation
    region.recovered_infected_ratio = recovered_individuals_infected / region.totalPopulation

    # after taking in this data, calculate the new S/I/R values for this individual province.

    region.susceptible_proportion -= susceptible_individuals_infected + recovered_individuals_infected + vaccinated_individuals_infected

    region.infected_proportion += susceptible_individuals_infected + recovered_individuals_infected + vaccinated_individuals_infected - region.infected_proportion * global_recovery_rate
   
    region.recovered_proportion += (region.infected_proportion - region.recovered_vaccination_ratio) * global_recovery_rate - region.recovered_proportion * global_recovery_fall_rate

    region.vaccinated_proportion -= region.vaccinated_proportion * global_vaccination_fall_rate

    region.susceptible_proportion += region.susceptible_proportion - susceptible_individuals_infected - region.recovered_proportion * global_recovery_fall_rate + region.vaccinated_proportion * global_vaccination_fall_rate

    

    # a certain proportion of the infected population will be vaccinated; when these individuals recover, they move back into the vaccinated population.

    region.vaccinated_proportion += region.recovered_vaccination_ratio * global_recovery_rate - region.recovered_proportion * global_recovery_fall_rate


    if region.vaccination_program == True:
        regional_vaccination_rollout_rate = global_vaccination_rollout_rate * max(1.0, region.density / 100)
        # vaccination converts recovered and susceptible individuals to 'vaccinated'
        region.vaccinated_proportion += regional_vaccination_rollout_rate * (region.susceptible_proportion + region.recovered_proportion) 
    


def main():
    print('Hello, world!')


if __name__ == '__main__':
    main()
