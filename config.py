# effectiveness factor of recovered status and vaccination status

vaccinated_vulnerability = 0.15
recovered_vulnerability = 0.2

# the average number of people a single infected individual infects over the course of the infectious period.
# in each sector, we count this factor as being influenced by density and interaction probability; it is not a static value.
global_r0 = 2.0

# how quickly an infected individual recovers from the infection, becoming noninfectious
global_recovery_rate = 1.0/14.0

daily_infection_rate = global_r0 / 14.0

# rate at which the recovered proportion of a province becomes susceptible again
global_recovery_fall_rate = 0.04
global_vaccination_fall_rate = 0.03
