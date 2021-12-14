# effectiveness factor of recovered status and vaccination status. These are derived from the Government
# of Canada's "Health and Human Services Canada" website.

vaccinated_vulnerability = 0.05
recovered_vulnerability = 0.12

# the average number of people a single infected individual infects over the course of the infectious period.
# in each sector, we count this factor as being influenced by density and interaction probability; it is not a static value.
global_r0 = 2.5

# how quickly an infected individual recovers from the infection, becoming noninfectious. These are
# derived from the CDC source
global_recovery_rate = 1.0/14.0

daily_infection_rate = global_r0 / 25.0

# rate at which the recovered proportion of a province becomes susceptible again
global_recovery_fall_rate = 0.01
global_vaccination_fall_rate = 0.005

#global vaccination rollout rate; This is an arbitrary constant.
global_vaccination_rollout_rate = 0.3

