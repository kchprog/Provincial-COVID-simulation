import csv
from dataclasses import dataclass
import datetime


@dataclass
class CovidCases:
    """
    A class containing the date and the number of recorded covid cases in Ontario on that date.

    Instance Attributes:
        - date: The given date in datetime.date
        - cases: The number of covid cases on the given date.

    Representation Invariants:
        - datetime.date(2020, 1, 1) < self.date < datetime.date(2022, 1, 1)
        - 0 <= self.cases
    """
    date: datetime.date
    cases: int

@dataclass
class VaccinationRate:
    """
    A class dontaing the date, the number of people who became fully vaccinated on that date
    and the number of people who recieved their first dose on that date

    Instance Attributes:
        - date: The given date in datetime.date
        - first_dose: The number of people who recieved their first dose on the given date.
        - fully_vacc: The number of people who became fully vaccinated on the given date.

    Representation Invariants:
        - datetime.date(2020, 1, 1) < self.date < datetime.date(2022, 1, 1)
        - 0 <= self.first_dose
        - 0 <= self.fully_vacc
    """
    date: datetime.date
    first_dose: int
    fully_vacc: int


def load_covid_data(filename: str) -> list[CovidCases]:
    """
    Returns a list of CovidCases based on real data from Ontario
    """
    covid_list = []
    month_list = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                  'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    with open(filename) as f:
        reader = csv.reader(f, delimeter=',')
        next(reader)  # skip the header

        for row in reader:
            assert len(row) == 3
            date = row[0].split()
            date = datetime.date(int(date[3]), month_list[date[1]], int(date[2]))
            covid_list.append(CovidCases(date, int(row[1])))
    return covid_list

def load_vaccine_data(filename: str) -> list[VaccinationRate]:
    """
    Returns a list of VaccinationRate based on real data from Ontario
    """
    vaccine_list = []
    month_list = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                  'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    with open(filename) as f:
        reader = csv.reader(f, delimeter=',')
        next(reader)  # skip the header

        for row in reader:
            assert len(row) == 3
            date = row[0].split()
            date = datetime.date(int(date[3]), month_list[date[1]], int(date[2]))
            vaccine_list.append(VaccinationRate(date, int(row[2]), int(row[1])))
    return vaccine_list
