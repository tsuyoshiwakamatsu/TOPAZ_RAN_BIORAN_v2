import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')  # Use an interactive backend
import numpy as np
import pylab as pl
from mpl_toolkits.basemap import Basemap, cm
from netCDF4 import Dataset

def log_to_linear_std(log_std, mean_linear):
    """
    Convert standard deviation from log10 scale to linear scale.
    
    Parameters:
    log_std (numpy.ndarray or float): Standard deviation in the log10 scale.
    mean_linear (numpy.ndarray or float): Mean of the data in the linear scale.
    
    Returns:
    numpy.ndarray or float: Standard deviation in the linear scale.
    """
    linear_std = mean_linear * (10**log_std - 1)
    return linear_std

isdebug = False

target_date = "20190601"
#target_date = "20160601"

#input_file = 'data/CMEMSGLB_SCHL/SCHL_'+target_date+'_full.nc'
input_file = 'data/ESACCI_SCHL/SCHL_'+target_date+'_full.nc'

nc = Dataset(input_file, 'r')   # Open the NetCDF file

var_name = 'chlor_a'
var = nc.variables[var_name]
std_name = 'chlor_a_log10_rmsd'
std = nc.variables[std_name]
lon = nc.variables['lon']
lat = nc.variables['lat']

if isdebug:
   print(var.shape,type(var))
   print(std.shape,type(std))
   print(lon.shape,type(lon))
   print(lat.shape,type(lat))

# aggregate data at observation time (center of a window, so simple mean)

if hasattr(var, '_FillValue'):
   fill_value = var._FillValue
   data = np.ma.masked_equal(var[:], fill_value)
else:
   data = var
print('var', var.shape ,type(var))
var_mean = data[0,:,:].squeeze()

if hasattr(std, '_FillValue'):
   fill_value = std._FillValue
   data = np.ma.masked_equal(std[:], fill_value)
else:
   data = std
std_mean = data[0,:,:].squeeze()

lon_mean, lat_mean = np.meshgrid(lon, lat)

# apply CHL mask (nan) to other parameters

std_mean.mask = std_mean.mask
lon_mean.mask = var_mean.mask
lat_mean.mask = var_mean.mask

if isdebug:
   print('var_mean', var_mean.shape ,type(var_mean))
   print('std_mean', std_mean.shape ,type(std_mean))
   print('lon_mean', lon_mean.shape ,type(lon_mean))
   print('lat_mean', lat_mean.shape ,type(lat_mean))

   var_list = [ 'CHL', 'CHL_uncertainty', 'lon', 'lat']

   for var_name in var_list:
      plt.imshow(var_mean[:,:], origin='lower')
      plt.colorbar(label=var_name)
      plt.xlabel('Longitude')
      plt.ylabel('Latitude')
      plt.show()

# compress 2D data w/ nan to 1D data w/o nan to plot

var_plot=var_mean.compressed()
std_plot=std_mean.compressed()
lon_plot=lon_mean.compressed()
lat_plot=lat_mean.compressed()

if isdebug:
   print('var_plot', var_plot.shape, type(var_plot))
   print('std_plot', std_plot.shape, type(std_plot))
   print('lon_plot', lon_plot.shape, type(lon_plot))
   print('lat_plot', lat_plot.shape, type(lat_plot))

# plot data on map projection

isarctic = False
isnordic = True
ispacific = False

if isarctic:
   m = Basemap(projection='npaeqd',resolution='c',boundinglat=55,lon_0=0)
   s = 3 # marker size

elif isnordic:
   m = Basemap(projection='cass',resolution='i',llcrnrlon=-20,llcrnrlat=55,urcrnrlon=60,urcrnrlat=75,lon_0=0,lat_0=70)
   s = 2 # marker size

elif ispacific:
   m = Basemap(projection='cass',resolution='i',llcrnrlon=160,llcrnrlat=55,urcrnrlon=240,urcrnrlat=75,lon_0=180,lat_0=70)
   s = 2 # marker size

x_plot, y_plot = m(lon_plot,lat_plot)

if isdebug:
   print('x_plot', x_plot.shape, type(x_plot))
   print('y_plot', y_plot.shape, type(y_plot))

# plot var

fig, ax = plt.subplots()

cs = m.scatter(x_plot,y_plot,s=s,c=var_plot,edgecolors='none',marker='o',alpha=1.0,vmin=0.0,vmax=10.0)
cb = m.colorbar(cs,location='right',pad='13%')

# draw coastlines, country boundaries, fill continents.                                                                                                                              
m.drawcoastlines(linewidth=0.5,color='dimgray')
m.fillcontinents(color='whitesmoke',lake_color='whitesmoke')

# draw meridians and parallelss                                                                                                                                                      
lbs_lon=[1, 0, 0, 1]
lbs_lat=[0, 1, 1, 0]

m.drawmeridians(range(-180,180,20),labels=lbs_lon,color='gray');
m.drawparallels(range(-90,90,10),labels=lbs_lat,color='gray');

# title                                                                                                                                                                              
title='CHL_'+target_date
plt.title(title,y=1.06)

outfile="figs/"+title+".png"
pl.savefig(outfile,dpi=300)   

plt.show()

# plot std

fig, ax = plt.subplots()

cs = m.scatter(x_plot,y_plot,s=s,c=std_plot,edgecolors='none',marker='o',alpha=1.0,vmin=0.0,vmax=100.0)
cb = m.colorbar(cs,location='right',pad='13%')

# draw coastlines, country boundaries, fill continents.                                                                                                                              
m.drawcoastlines(linewidth=0.5,color='dimgray')
m.fillcontinents(color='whitesmoke',lake_color='whitesmoke')

# draw meridians and parallelss                                                                                                                                                      
lbs_lon=[1, 0, 0, 1]
lbs_lat=[0, 1, 1, 0]

m.drawmeridians(range(-180,180,20),labels=lbs_lon,color='gray');
m.drawparallels(range(-90,90,10),labels=lbs_lat,color='gray');

# title                                                                                                                                                                              
title='CHL_uncertainty_'+target_date
plt.title(title,y=1.06)

outfile="figs/"+title+".png"
pl.savefig(outfile,dpi=300)   

plt.show()
