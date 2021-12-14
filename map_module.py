"""map_module
This module is for the display of the visual outputs produced by the simulation

"""
import math
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import csv
import math_module
from shapely.geometry import Point

def main():
    list_of_cities = math_module.setup()

    sf = shp.Reader("mdf\OntarioShapefile.shp")
    len(sf.shapes())

    crs={'init':'epsg:4326'}


    df=gpd.read_file("mdf\OntarioShapefile.shp")

    df.head()
    
    df = df[[]]
    df.boundary.plot()
    df.plot()
    
    
def plot_sectors(data: list, day: int):
    """The plot_sectors function is used for producing the Covid Severity graph on a specific day
        This function takes in a list of graphable data from main and the specific day the user want to access. 
        It plots the virus proportions for the different cities and plots them on the graph. The more opaque the dots become, 
        the higher the virus proportion there is

    
    """
    df = gpd.read_file("mdf/OntarioShapefile.shp")
    geodatas = []
    ontario_map = df.plot()
    for mdata in data:
        # geodatas.append(virus_city(s)[0])
        mp = {'population': [mdata.total_population], 'longitude': [mdata.longitude], 'latitude': [mdata.latitude],
             'density': [mdata.density],
             'infected': [mdata.i_proportion], 'geometry': [Point(mdata.longitude, mdata.latitude)]}
        geodatas.append(mp)
    for m in geodatas:
        g = gpd.GeoDataFrame(m, crs='EPSG:4326')
        gf = gpd.GeoDataFrame(m, geometry=gpd.points_from_xy(g.latitude, g.longitude))
        inf = min(0.75, g.infected[0] * 10.0)
        # Draws dots on map, the infected_proportion determines the translucency of the dots
        gf.plot(ax=ontario_map, color='red', markersize=g.density/1.5, alpha=inf)
    # Title of map
    plt.title('Covid Severity at day ' + str(day))
    
