import math
import geopandas as gpd
import numpy as np
import pandas as pd
import shapefile as shp
import matplotlib.pyplot as plt
import seaborn as sns
import csv
import math_module

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
    
    
 def plot_sectors(sectors: list):
        df = gpd.read_file("/mdf/OntarioShapefile.shp")
        geodatas = []
        frame_datas = []
        ontario_map = df.plot()
        for sector in sectors:
            # geodatas.append(virus_city(s)[0])
            mp = {'city': [sector.name], 'population': [sector.population], 'longitude': [sector.longitude], 'latitude': [sector.latitude],
                  'density': [sector.density],
                  'infected': [sector.infectious_proportion], 'geometry': [Point(sector.longitude, sector.latitude)]}
            geodatas.append(mp)
        for m in geodatas:
            g = geopandas.GeoDataFrame(m, crs='EPSG:4326')
            gf = gpd.GeoDataFrame(m, geometry=gpd.points_from_xy(g.latitude, g.longitude))
            # Draws dots on map, the infected_proportion determines the translucency of the dots
            gf.plot(ax=ontario_map, color='red', markersize=g.density, alpha=g.infected * 1)

        # for gf in frame_datas:
            # gf.plot(ax=ontario_map, color='red', markersize=100, alpha=0.5)

        cases = {'Covid': 'red', 'vaccinated': 'green'}
        ontario_map.legend(['Covid', 'Vaccinated'])
        # Title of map
        plt.title('Covid Severity')

        
        
 def plot_city_dots():
    """ Plots city dots, reference code"""
    # reads the csv file of the city
    sp = "City_data_config.csv"
    mp = pd.read_csv(sp)
    df = gpd.read_file("OntarioShapefile.shp")
    # Gets the POINT() of the x and y of the cities
    df_geo = gpd.GeoDataFrame(mp, geometry=gpd.points_from_xy(
        mp.Latitude, mp.Longitude
    ))
    ontario_map = df.plot()
    # color means the dot colour, markersize is the size of the dots, alpha represents translucence
    # It plots dots on df.plot(), which is the ontario map
    df_geo.plot(ax=ontario_map, color='red', markersize=8, alpha=0.25)
    df_geo.plot(ax=ontario_map, color='green', markersize=8, alpha=0.25)
    cases = {'Covid': 'red', 'vaccinated': 'green'}
    ontario_map.legend(['Covid', 'Vaccinated'])
    # Title of map
    plt.title('Plot City points')

    
def read_shapefile(sf):
    #fetching the headings from the shape file
    fields = [x[0] for x in sf.fields][1:]
#fetching the records from the shape file
    records = [list(i) for i in sf.records()]
    shps = [s.points for s in sf.shapes()]
#converting shapefile data into pandas dataframe
    df = pd.DataFrame(columns=fields, data=records)
#assigning the coordinates
    df = df.assign(coords=shps)
    return df

def plot_shape(id, s=None):
    plt.figure()
    #plotting the graphical axes where map ploting will be done
    ax = plt.axes()
    ax.set_aspect('equal')
#storing the id number to be worked upon
    shape_ex = s.shape(id)
#NP.ZERO initializes an array of rows and column with 0 in place of each elements 
    #an array will be generated where number of rows will be(len(shape_ex,point))and number of columns will be 1 and stored into the variable
    x_lon = np.zeros((len(shape_ex.points),1))
#an array will be generated where number of rows will be(len(shape_ex,point))and number of columns will be 1 and stored into the variable
    y_lat = np.zeros((len(shape_ex.points),1))
    for ip in range(len(shape_ex.points)):
        x_lon[ip] = shape_ex.points[ip][0]
        y_lat[ip] = shape_ex.points[ip][1]
#plotting using the derived coordinated stored in array created by numpy
    plt.plot(x_lon,y_lat) 
    x0 = np.mean(x_lon)
    y0 = np.mean(y_lat)
    plt.text(x0, y0, s, fontsize=10)
# use bbox (bounding box) to set plot limits
    plt.xlim(shape_ex.bbox[0],shape_ex.bbox[2])
    return x0, y0

def plot_cities_data(sf, title, cities, data=None,color=None, print_id=False):
 
    df = read_shapefile(sf)
    city_id = []
    for i in cities:
        city_id.append(df[df.DIST_NAME == 
                            i.upper()].index.get_values()[0])
    plot_map_fill_multiples_ids_tone(sf, title, city_id, 
                                     print_id, \
                                     x_lim = None, 
                                     y_lim = None, 
                                     figsize = (11,9))
def plot_map_fill_multiples_ids_tone(sf, title, city,  
                                     print_id, color_ton, 
                                     bins, 
                                     x_lim = None, 
                                     y_lim = None, 
                                     figsize = (11,9)):
   
        
    plt.figure(figsize = figsize)
    fig, ax = plt.subplots(figsize = figsize)
    fig.suptitle(title, fontsize=16)
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
        ax.plot(x, y, 'k')
            
    for id in city:
        shape_ex = sf.shape(id)
        x_lon = np.zeros((len(shape_ex.points),1))
        y_lat = np.zeros((len(shape_ex.points),1))
        for ip in range(len(shape_ex.points)):
            x_lon[ip] = shape_ex.points[ip][0]
            y_lat[ip] = shape_ex.points[ip][1]
        ax.fill(x_lon,y_lat, color_ton[city.index(id)])
        if print_id != False:
            x0 = np.mean(x_lon)
            y0 = np.mean(y_lat)
            plt.text(x0, y0, id, fontsize=10)
    if (x_lim != None) & (y_lim != None):     
        plt.xlim(x_lim)
        plt.ylim(y_lim)
