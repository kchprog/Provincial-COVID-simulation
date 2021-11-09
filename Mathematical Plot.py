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

    travelRate = 0.0

    neighborProvinces = []

    density = 0.0

    def __init__(self, name, population, area, neighborProvinces, type):
        self.name = name
        self.population = population
        self.area = area # kilometers squared
        self.type = type # large urban, urban, suburban, rural

        self.density = population / area

        self.travelRate = self.density / 100
        # travelRate is the likelihood that people from neighboring provinces will travel to this sector
        self.neighborProvinces = neighborProvinces

        # per_capita_transmission_rate is the rate at which people in a sector will spread the virus; it is the product of the baseline infection rate and a factor adjusting for the population density
        self.per_capita_transmission_rate = max(2.0 / 5 * math.log(self.density / 100.0, 2.71828), 1.0) * daily_infection_rate
        # the infection rate is the product of the r0 value and the rate of contact within a population. These arbitrary values are chosen to limit the simulated spread of the virus to a reasonable level.

    def __str__(self):
        return '{} has a population of {} and an area of {} and a density of {}'.format(self.name, self.population, self.area, self.density)

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

def updateSimulation(area: sector, policy: str):
    # implements simulated policy changes
    if policy == 'lockdown':
        area.per_capita_transmission_rate = area.per_capita_transmission_rate * 0.25
        area.travelRate = area.travelRate / (2 + area.density / 100)
    elif policy == 'travel ban':
        area.travelRate = area.travelRate * 0.1
    elif policy == 'open':
        area.per_capita_transmission_rate = max(2.0 / 5 * math.log(area.density / 100.0, 2.71828), 1.0) * daily_infection_rate
    elif policy == 'recover':
        area.per_capita_transmission_rate = 0.0
    else:
        print('Error: invalid policy')


    # calculate the transfer of infected individuals from neighboring provinces

    neighbors = area.neighborProvinces
    incoming_noninfected_Transfer = 0
    incomingInfectedTransfer = 0

    for neighbor in neighbors:
        incoming_noninfected_Transfer += (neighbor.totalPopulation) * area.travelRate / 1000 - neighbor.totalPopulation * area.travelRate * neighbor.infected_proportion / 1000
        incomingInfectedTransfer += neighbor.totalPopulation * area.travelRate * neighbor.infected_proportion / 1000

    
    area.susceptible_proportion = (area.susceptible_proportion + incoming_noninfected_Transfer) / area.totalPopulation + (area.recovered_proportion * recovered_vulnerability + area.vaccinated_proportion * vaccinated_vulnerability)

    # a portion of individuals in the 'RECOVERED' and 'VACCINATED' groups will be infected. 

    # calculate the new infected proportion

    susceptible_individuals_infected = area.infected_proportion * area.per_capita_transmission_rate * area.susceptible_proportion + incomingInfectedTransfer
    recovered_individuals_infected = area.recovered_proportion * recovered_vulnerability * area.per_capita_transmission_rate * area.susceptible_proportion
    vaccinated_individuals_infected = area.vaccinated_proportion * vaccinated_vulnerability * area.per_capita_transmission_rate * area.susceptible_proportion

    # proportion of infected that are not from the susceptible population

    area.recovered_vaccination_ratio = recovered_individuals_infected / area.totalPopulation
    area.recovered_infected_ratio = recovered_individuals_infected / area.totalPopulation

    # after taking in this data, calculate the new S/I/R values for this individual province.

    area.susceptible_proportion -= susceptible_individuals_infected + recovered_individuals_infected + vaccinated_individuals_infected

    area.infected_proportion += susceptible_individuals_infected + recovered_individuals_infected + vaccinated_individuals_infected - area.infected_proportion * global_recovery_rate
   
    area.recovered_proportion += (area.infected_proportion - area.recovered_vaccination_ratio) * global_recovery_rate - area.recovered_proportion * global_recovery_fall_rate

    area.susceptible_proportion = area.susceptible_proportion - susceptible_individuals_infected + area.recovered_proportion * global_recovery_fall_rate

    # a certain proportion of the infected population will be vaccinated; when these individuals recover, they move back into the vaccinated population.

    area.vaccinated_proportion += area.recovered_vaccination_ratio * global_recovery_rate - area.recovered_proportion * global_recovery_fall_rate


    if area.vaccinated_program == True:
        # vaccination converts recovered and susceptible individuals to 'vaccinated'
        area.vaccinated_proportion = area.vaccinated_proportion + area.recovered_proportion * global_recovery_fall_rate
    


def main():
    print('Hello, world!')


if __name__ == '__main__':
    main()