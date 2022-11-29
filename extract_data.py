#!/usr/bin/env python

from __future__ import print_function

import os
import shutil
import datetime

import numpy
import netCDF4
import matplotlib.pyplot as plt

import cartopy.crs as ccrs        #import projections
import cartopy.feature as cfeature      #import features

import clawpack.geoclaw.surge.storm
import clawpack.geoclaw.units as units

def days2seconds(time):
    return time * 60**2 * 24

def extract_storms(data, verbose=False):
    r"""Extracts from data the `n`th storm and returns the correct length data"""
    
    # Output list
    storms = []
    
    # Get dimensions
    num_storms, max_time_length = data.variables['Mwspd'].shape
    if verbose:
        print("Num storms: %s" % num_storms)
        print("Max time length: %s" % max_time_length)
    
    num_failed_storms = 0
    for i in range(num_storms):
        # Extract size of storm data        
        longitude = data.variables['longitude'][i, :].compressed()
        latitude = data.variables['latitude'][i, :].compressed()
        assert(longitude.shape == latitude.shape)
        valid_length = longitude.shape[0]
        if valid_length == 0:
            num_failed_storms += 1
            break

        # Construct storm object
        storm = clawpack.geoclaw.surge.storm.Storm()
        
        # Times in 6 hour increments in seconds
        storm.time_offset = datetime.datetime.today()
        storm.t = numpy.array([storm.time_offset
                    + datetime.timedelta(seconds=k * 6 * 60**2) 
                            for k in range(valid_length)])
        storm.eye_location = numpy.empty((valid_length, 2))
        storm.eye_location[:, 0] = longitude
        storm.eye_location[:, 1] = latitude
        max_wind_speed = numpy.array(data.variables['Mwspd'][i, :valid_length])
        
        # Add radius of max wind - Use willoughby instead for high latitude?
        C0 = 218.3784 * numpy.ones(max_wind_speed.shape[0])
        max_wind_radius = ( C0 - 1.2014 * max_wind_speed 
                               + (max_wind_speed / 10.9884)**2 
                               - (max_wind_speed / 35.3052)**3 
                               - 145.5090 * numpy.cos(storm.eye_location[:, 1] * 0.0174533) )
        
        # Add central pressure - From Kossin, J. P. WAF 2015
        a = -0.0025
        b = -0.36
        c = 1021.36
        central_pressure = (  a * max_wind_speed**2
                            + b * max_wind_speed
                            + c)

        # Extent of storm set to 300 km                 
        storm_radius = 500 * numpy.ones(storm.t.shape)

        # Convert units
        storm.storm_radius = units.convert(storm_radius, 'km', 'm')
        storm.max_wind_radius = units.convert(max_wind_radius, 'nmi', 'm')
        storm.max_wind_speed = units.convert(max_wind_speed, 'knots', 'm/s')
        storm.central_pressure = units.convert(central_pressure, 'mbar', 'Pa')
        
        storms.append(storm)

        if num_failed_storms > 0:
            print("Number of failed storms = %s" % num_failed_storms)
    
    return storms


def plot_track(storm, color=False, axes=None):
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)

    category_color = {5:'red', 4:'yellow', 3:'orange', 2:'green', 1:'blue', 
                        0:'gray', -1:'gray'}
    cat = storm.category(categorization="NHC")
    if color:
        for i in range(storm.eye_location.shape[0] - 1):
            color = category_color[cat[i]]
            try:
                axes.plot(storm.eye_location[i:i+2, 0], storm.eye_location[i:i+2, 1], 
                    linewidth=1.5, color=color, transform = ccrs.Geodetic())
            except:
                print("stuff")
                pass

    else:
        axes.plot(storm.eye_location[:, 0], storm.eye_location[:, 1], 
                    linewidth=1.5, color='r', transform = ccrs.Geodetic())

    return axes

def plot_pressure(storm, axes=None):
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)

    axes.plot(storm.t, units.convert(storm.central_pressure, 'Pa', 'mbar'), 
        linewidth=0.5, color='gray')

    return axes

def plot_intensity(storm, axes=None):
    if axes is None:
        fig = plt.figure()
        axes = fig.add_subplot(1, 1, 1)

    axes.plot(storm.t, storm.max_wind_speed, linewidth=0.5, color='gray')

    return axes


if __name__ == '__main__':

    climate_models = ["CCSM4", "GFDL_CM3", "HadGEM2_ES", "MIROC5", "MPI_ESM_MR"]
    years = ["2005", "2040", "2099"]
    variants = ["CRH", "SD"]
    make_plots = True

    for climate_model in climate_models:
        for year in years:
            for variant in variants:
                print("Creating storms for %s %s %s" % (climate_model, year, variant))

                # Create directory
                dir_path = "./storms/%s_%s_%s" % (climate_model, year, variant)
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                os.makedirs(dir_path, exist_ok=True)

                storms = []
                for ensemble in range(20):
                    path = "./tracks/NE_%s_tracks_%sENS%s_%s.nc" % (climate_model, year, str(ensemble).zfill(3), variant)
                    data = netCDF4.Dataset(path)
                    storms.extend(extract_storms(data))
                    data.close()
                print("  Number of storms = %s" %  len(storms))

                # Plotting
                if make_plots:
                    central_lat = 30 
                    central_lon = -70 
                    fig = plt.figure(figsize=(15,9))
                    axes = plt.axes(projection=ccrs.LambertConformal(central_lon, central_lat))
                    axes.add_feature(cfeature.LAND, edgecolor='black')
                    axes.set_extent([-100, -40, 5, 57]) 
                    gl = axes.gridlines(draw_labels=True, x_inline=False, y_inline=False)
                    gl.top_labels = False

                if make_plots:
                    fig_wind = plt.figure()
                    fig_pressure = plt.figure()
                    axes_wind = fig_wind.add_subplot(1, 1, 1)
                    axes_pressure = fig_pressure.add_subplot(1, 1, 1)

                for (n, storm) in enumerate(storms):
                    name = "%s.storm" % (str(n).zfill(5))
                    storm.write(path="./storms/%s_%s_%s/%s" % (climate_model, year, variant, name), file_format="geoclaw")
                    if make_plots:
                        plot_track(storm, axes=axes)
                        plot_pressure(storm, axes=axes_pressure)
                        plot_intensity(storm, axes=axes_wind)

                if make_plots:
                    axes_wind.set_ylabel("m/s")
                    axes_pressure.set_ylabel("mbar")
                    axes_wind.set_title("%s %s %s - Wind" % (climate_model, year, variant))
                    axes_pressure.set_title("%s %s %s - Pressure" % (climate_model, year, variant))
                    axes.set_title("Storms Tracks (n = %s)" % len(storms))

                    fig.savefig("./storms/%s_%s_%s/tracks.png" % (climate_model, year, variant))
                    fig_wind.savefig("./storms/%s_%s_%s/wind.png" % (climate_model, year, variant))
                    fig_pressure.savefig("./storms/%s_%s_%s/pressure.png" % (climate_model, year, variant))
                    plt.close('all')
                    delete(fig, fig_wind, fig_pressure)
    