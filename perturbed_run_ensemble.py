#!/usr/bin/env python

"""Run specificed storms from the synthetic storms provided."""

from __future__ import print_function

import sys
import os

import numpy
import matplotlib.pyplot as plt

import batch.habastorm as batch

import clawpack.geoclaw.dtopotools as dtopotools
import clawpack.clawutil as clawutil
import datetime
import time

from clawpack.geoclaw.surge.storm import Storm

#from load_synthetic_storms import load_chaz_storms 

# Time Conversions  
def days2seconds(days):
    return days * 60.0**2 * 24.0


class LongIslandStormJob(batch.HabaneroStormJob):
    r"""
    Modifications to the :class:'HabaneroStormJob' for 
    Long Island Habanero storm runs 
    """

    r"""Class used to describe a storm 
    job run 

    .. attribute:: type
 
        (string) - The top most directory that the storm 
        batch output will be located in. 

    .. attribute:: prefix::
 
        (int) storms named by number
    
    .. attribute:: storm_directory
       
        (string) specify the directory where jobs are saved 

    .. attribute:: storm_object 
        
        (geoclaw storm data object)

    Methods
    -------
    
    """
     
    def __init__(self, prefix, 
                       storm_directory,
                       storm_object, 
                       wind_model, 
                       amr_level, 
                       storm_ensemble_type, 
                       region):  
        r"""
        Initialize a LongIslandStormJob object.

        See :class:`LongIslandStormJob` for full documentation

        """

        super(LongIslandStormJob, self).__init__()

        self.email = None 

        self.type = "storm-surge"
        self.storm_ensemble_type = storm_ensemble_type
        self.region = region 
 
        self.storm_directory = storm_directory
        self.storm_object = storm_object

        self.name = "%s-amr%s" %(wind_model, amr_level)  
        self.prefix = str(prefix).zfill(4) 
        self.executable = 'xgeoclaw'

        # Data objects
        import setrun
        self.rundata = setrun.setrun()

        # Set rundata friction, surge, and clawdata variables  
        self.rundata = setrun.setgeo(self.rundata)


        # Set surge data 
        self.rundata.surge_data.storm_specification_type = wind_model 

        #thousand_ts = numpy.load("5000_ts05.npy")
        #t_intersect = thousand_ts[self.storm_object.ID-4000]
        t_intersect = 950400.0

        # Boxes to refine in
        #x_lows = [-74.2, -74.6, -74.6, -75, -75, -75, -75.6]
        #y_lows = [41.2, 39.9, 39.5, 39.3, 39.1, 38.9, 38.5]
        #widths = [3.2, 3.6, 2.8, 2.8, 2.6, 2.4, 2.6]
        #heights= [0.5, 1.4, 0.8, 0.21, 0.21, 0.21, 0.41]

        # Find time the storm intersects the boxes
        #lons_orig = self.storm_object.eye_location[0,:]
        #lats_orig = self.storm_object.eye_location[1,:]
        #print(lons_orig)
        #print(lats_orig)
        #n = len(lons_orig)
        #print(n)
        #t_p = numpy.linspace(0,6*60*60*(n-1),n)
        #t = numpy.linspace(0,6*60*60*(n-1),6*4*(n-1)+1)
        #lons = numpy.interp(t, t_p, lons_orig-360.0)
        #lats = numpy.interp(t, t_p, lats_orig)
        #intersects = False
        #j = 0
        #while not(intersects):
        #    if j == len(lons):
        #        t_intersect = -1.0
        #        break
        #    for h in range(len(x_lows)):
        #        if (x_lows[h] < lons[j] < x_lows[h] + widths[h]) and (y_lows[h] < lats[j] < y_lows[h]+heights[h]):
        #            t_intersect = t[j] 
        #            intersects = True
        #            break
        #    j = j + 1
        #print(str(self.storm_object.ID).zfill(4)+":  "+str(t_intersect))

        # Find landfall time
        #i_landfall = 0
        #d_landfall = 10e6
        #nyc_x = -74.013
        #nyc_y = 40.7
        #for ind in range(len(self.storm_object.t)):
        #    self.storm_object.eye_location[0,ind] = -360.0 + self.storm_object.eye_location[0,ind]
        #    d_ind = (nyc_x-self.storm_object.eye_location[0,ind])**2+(nyc_y-self.storm_object.eye_location[1,ind])**2
        #    if d_ind < d_landfall:
        #        d_landfall = d_ind
        #        i_landfall = ind
        #t_landfall = (self.storm_object.t[i_landfall]-self.storm_object.time_offset).total_seconds()

        #delta_t0 = self.storm_object.t[0] - self.storm_object.time_offset
        #self.rundata.clawdata.t0 = days2seconds(delta_t0.days)/2 
        #self.rundata.clawdata.t0 = days2seconds(-0.5)  
        #self.rundata.clawdata.t0 = t_landfall - days2seconds(1.5)  
        self.rundata.clawdata.t0 = t_intersect - days2seconds(1.0)  
        
        # clawdata.tfinal value is the entire length of the track in days
        print(self.storm_object.t[-1]) 
        print(self.storm_object.time_offset) 
        delta_tf = self.storm_object.t[-1] - self.storm_object.time_offset
        #self.rundata.clawdata.tfinal = delta_tf.total_seconds()
        #self.rundata.clawdata.tfinal = t_landfall + days2seconds(1.5)
        self.rundata.clawdata.tfinal = t_intersect + days2seconds(3.0)

       # print("######################################")
        #print("#### closest point")
        #print(self.storm_object.eye_location[0,i_landfall])
        #print(self.storm_object.eye_location[1,i_landfall])

        #print("#### t_landfall = " + str(t_landfall))
        #print("######################################")

        # Set refinement 
        #self.rundata.amrdata.amr_levels_max = amr_level 
        self.rundata.amrdata.amr_levels_max = 5

        # Set regions data =
        # Long Island Region 
        self.rundata.regiondata.regions = []  
        #self.rundata.regiondata.regions.append([1, 7, self.rundata.clawdata.t0, 
        #                                              self.rundata.clawdata.tfinal, 
        #                                              -74.1, -73.7, 40.55, 48.5])
        # NYC regions
        # put some refinement around landfall time
        #self.rundata.regiondata.regions.append([5,5,days2seconds(-0.5),days2seconds(0.50),-74.2,-73.7,40.40,48.5])
        #self.rundata.regiondata.regions.append([4,5,days2seconds(0.10),days2seconds(1),-74.2,-73.7,40.55,48.5])

        #self.rundata.regiondata.regions.append([4,4,t_landfall-days2seconds(0.5),t_landfall+days2seconds(0.5),-74.2,-69.7,37.0,48.5])
        #self.rundata.regiondata.regions.append([4,4,t_landfall-days2seconds(1.0),t_landfall+days2seconds(1.0),-75.0,-73.0,39.5,42.4])
        #self.rundata.regiondata.regions.append([5,5,t_landfall-days2seconds(1.0),t_landfall+days2seconds(1.0),-74.25,-73.25,40.45,40.95])

        # Boxes to refine in
        x_lows = [-74.2, -74.6, -74.6, -75, -75, -75, -75.6]
        y_lows = [41.2, 39.9, 39.5, 39.3, 39.1, 38.9, 38.5]
        widths = [3.2, 3.6, 2.8, 2.8, 2.6, 2.4, 2.6]
        heights= [0.5, 1.4, 0.8, 0.21, 0.21, 0.21, 0.41]
       
        for r in range(len(x_lows)):
            self.rundata.regiondata.regions.append([3,3,t_intersect-days2seconds(0.5),self.rundata.clawdata.tfinal,x_lows[r],x_lows[r]+widths[r],y_lows[r],y_lows[r]+heights[r]])
   
        # == settopo.data values ==
        topo_data = self.rundata.topo_data
        topo_data.topofiles = []
        topo_path = os.path.join(os.getcwd(),"../bathy") 
        atlantic_ocean = os.path.join(topo_path, "atlantic_1min.tt3")
        new_york = os.path.join(topo_path, "newyork_3s.tt3") 
        topo_data.topofiles.append([3, 1, 4, self.rundata.clawdata.t0,
                                         self.rundata.clawdata.tfinal,
                                         atlantic_ocean])
        topo_data.topofiles.append([3, 1, 8, self.rundata.clawdata.t0,
                                         self.rundata.clawdata.tfinal,
                                         new_york])


        # Set Gauge Data 
        # for gauges append lines of the form  [gaugeno, x, y, t1, t2]
        self.rundata.gaugedata.gauges = []
        # Gauge 1 
        #self.rundata.gaugedata.gauges.append([1, -73.84055, 40.44838,
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        ## Gauge 2  
        #self.rundata.gaugedata.gauges.append([2, -73.33605, 40.62581,
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal])
        #
        #self.rundata.gaugedata.gauges.append([3, -73.76252, 40.56637,
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        #
        #self.rundata.gaugedata.gauges.append([4, -74.09573, 40.49226,
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal])
        #
        #self.rundata.gaugedata.gauges.append([5, -73.93428, 40.51212, 
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        #
        #self.rundata.gaugedata.gauges.append([1, -73.82716, 40.47975,
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        #
        #self.rundata.gaugedata.gauges.append([2, -73.91643, 40.40659,
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        ## Sea Gauge 1 for coasrse refinements 
        #self.rundata.gaugedata.gauges.append([3, -73.82854, 40.26235, 
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        #
        ## Sea Gauge 2 for coarse refinements  
        #self.rundata.gaugedata.gauges.append([4, -73.49758, 40.46744, 
        #                                    self.rundata.clawdata.t0, 
        #                                    self.rundata.clawdata.tfinal]) 
        
        # battery gauge
        self.rundata.gaugedata.gauges.append([1,-74.013,40.7,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Kings point gauge
        self.rundata.gaugedata.gauges.append([2,-73.77,40.81,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Sandy Hook gauge
        self.rundata.gaugedata.gauges.append([3,-74.01,40.47,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Bergen Point West Reach
        self.rundata.gaugedata.gauges.append([4,-74.14166,40.6367,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Narrows
        self.rundata.gaugedata.gauges.append([5,-74.038,40.605,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Liberty Island
        self.rundata.gaugedata.gauges.append([6,-74.0454,40.68836,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # East river by UN
        self.rundata.gaugedata.gauges.append([7,-73.966336,40.743870,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Hudson river by Hudson Yards
        self.rundata.gaugedata.gauges.append([8,-74.011548,40.758075,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # Brighton Beach
        self.rundata.gaugedata.gauges.append([9,-73.960479,40.573854,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # JFK
        self.rundata.gaugedata.gauges.append([10,-73.7712,40.6415,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # East river by UN 2
        self.rundata.gaugedata.gauges.append([11,-73.956336,40.743870,self.rundata.clawdata.t0,self.rundata.clawdata.tfinal])
        # further out 1
        self.rundata.gaugedata.gauges.append([12,-73.71, 40.41, self.rundata.clawdata.t0, self.rundata.clawdata.tfinal])
        # further out 2
        self.rundata.gaugedata.gauges.append([13,-73.5, 40.2, self.rundata.clawdata.t0, self.rundata.clawdata.tfinal])
        

        # Include auxillary gauge data 
        self.rundata.gaugedata.aux_out_fields = [4, 5, 6] 
 
        self.rundata.gaugedata.min_time_increment = 60 
                                                 
        # Set path to geoclaw storm file  
        self.rundata.surge_data.storm_file = os.path.join(self.storm_directory,
                                       "%s_%s.storm" %(self.region, self.prefix))
    
        # Write storm data in geoclaw storm file  
        self.storm_object.write(self.rundata.surge_data.storm_file, 
                                            file_format = "geoclaw")


    def __str__(self):
        output = super(LongIslandStormJob, self).__str__()

        output += "{:<20}{:<1}{:<15}{:<1}".format("Region", ": ", "Long Island","\n")
        output += '{:<20}{:<1}{:<15}{:<1}'.format("Storm Format", ": ", "%s"
                                                %self.storm_ensemble_type, "\n")
        output += '{:<20}{:<1}{:<15}{:<1}'.format("Number", ": ", "%s" %self.prefix, "\n")
        
        return output


def run_longisland_job(wind_model  = 'holland80',
                       amr_level   = 5, 
                       storms     = None):  
    r"""
    Setup jobs to run at specific storm start and end.  
    """

    storm_tracker = storms[0].ID + len(storms)  
    # Path to file containing log of storms run
    path = os.path.join(os.environ.get('DATA_PATH', os.getcwd()), 
                   "new_york", 
                   "NYC-storm-%i-%i" %(storms[0].ID, storm_tracker),
                   "run_log.txt")
    #print(path) 

    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path))

 
    data_path = os.path.join(os.getcwd(), "data")
    storms_path = os.path.join(data_path, "storms") 
    tracks = os.path.join(storms_path, "geoclaw-longisland-tracks")
    print(tracks) 

    if not os.path.exists(tracks): 
        os.makedirs(os.path.dirname(tracks)) 

    jobs = []  
    with open(path, 'w') as run_log_file: 
        jobs = []

        location = "LongIsland" 
    
        # Run through list of storms and create 
        # Create storm name through storm ID and location
        # Write to log file and create job 
        for storm in storms:  
            storm_name = "%s_%s" %(location, str(storm.ID))
            run_log_file.write("%s %s\n" % (storm.ID, storm_name))
    
            # Create job and add to queue 
            jobs.append(LongIslandStormJob(prefix = storm.ID, 
                                 storm_directory      = tracks, 
                                 storm_object         = storm, 
                                 wind_model           = wind_model, 
                                 amr_level            = amr_level, 
                                 storm_ensemble_type  = "Chaz", 
                                 region               = "LongIsland"))
        
        print('Jobs created sent to controller')
        print("")   
        # Jobs are all created now we run 
        # the jobs using the batch 
        # controller  
        controller = batch.HabaneroStormBatchController(jobs)
        #controller.email = 'pcd2120@columbia.edu'
        print(controller)
        controller.run()
        jobs = []

    return len(jobs)  
         


if __name__ == '__main__':
    r"""
    Run Batch jobs.    
    """
    

    if len(sys.argv) == 1: 
        model = 'holland80'
        amr_l = 2 
    else: 
        model = str(sys.argv[1])
        amr_l = int(sys.argv[2]) 


    ## Adjust mask distance and mask speed
    md = None  
    ms = None 

    peaks3_perturbed = numpy.loadtxt('storm-surge/peaks3_perturbed.txt')
    
    import copy
    storms = []
    control_storm = Storm(path='perturb_control.storm', file_format = 'geoclaw')
    n = 9000
    for delta_mws in numpy.linspace(0,30,10):
        for delta_mwr in numpy.linspace(0,-3e4,10):
            for delta_cp in numpy.linspace(0,-5e3,10):
                s = copy.deepcopy(control_storm)
                s.max_wind_speed += delta_mws
                s.max_wind_radius += delta_mwr
                s.central_pressure += delta_cp
                s.ID = n
                if peaks3_perturbed[n-9000]<0.5:
                    storms.append(s)
                n = n+1

    #thousand_ids = numpy.load("5000_ids05.npy")
    #for count, n in enumerate(thousand_ids):
    #    s_n = Storm(path='chazstorms/storms/CCSM4_2005_CRH/%s.storm'%(str(n).zfill(5)), file_format = 'geoclaw')
    #    s_n.ID = count + 4000
    #    storms.append(s_n)
        
   
    #storms = [] 
    #new_indices = numpy.load('chazstorms/storms/newindices.npy')
    #for count, n in enumerate(new_indices):
    #    s_n = Storm(path='chazstorms/storms/edit_CCSM4_2005_CRH/%s.storm'%(str(count).zfill(5)), file_format = 'geoclaw')
    #    #s_n = Storm(path='chazstorms/storms/CCSM4_2005_CRH/%s.storm'%(str(n).zfill(5)), file_format = 'geoclaw')
    #    s_n.ID = 2000+count
    #    storms.append(s_n)

    #control_storm = Storm(path='sandy-orig.storm', file_format='geoclaw') 
#    sandy = Storm(path='sandy13.storm', file_format='geoclaw')
#    distance_squared = (sandy.eye_location[0,-2]-sandy.eye_location[0,-1])**2 + (sandy.eye_location[1,-2]-sandy.eye_location[1,-1])**2
#    distance_from_landfall = numpy.sqrt(distance_squared)
#    direction = numpy.pi + numpy.arctan2((sandy.eye_location[1,-2]-sandy.eye_location[1,-1]),(sandy.eye_location[0,-2]-sandy.eye_location[0,-1]))
#    delta_distance = distance_from_landfall # here just one step
    #print(direction)
    #print(numpy.cos(direction)*delta_distance)
    #print(numpy.sin(direction)*delta_distance)
    #print(sandy.eye_location[0,0] + delta_distance*numpy.cos(direction))
    #print(sandy.eye_location[0,1])
    #print(sandy.eye_location[1,0] + delta_distance*numpy.sin(direction))
    #print(sandy.eye_location[1,1])
    #print(sandy.eye_location[0,0] + 2*delta_distance*numpy.cos(direction))
    #print(sandy.eye_location[0,2])
    #sys.exit()

#    import copy
#    ID = 0
#    storms_j = []
#    s = copy.deepcopy(sandy)
#    storms_j.append(s)
#    for tj in range(-1,0):
#        storms_o = copy.deepcopy(storms_j)
#        storms_j = []
#        for si in storms_o:
#            for theta in numpy.linspace(-numpy.pi/6,numpy.pi/6,3):
#                s = copy.deepcopy(si)
#                s.eye_location[0,tj] = s.eye_location[0,tj-1] + delta_distance*numpy.cos(direction+theta)
#                s.eye_location[1,tj] = s.eye_location[1,tj-1] + delta_distance*numpy.sin(direction+theta)
#                #s.eye_location[2,tj] = 0.0
#                storms_j.append(s)

#    storms = storms_j  
#    for s in storms:
#        s.ID = ID
#        ID = ID +1

    #import copy
    #ID = 0
    #for i1, theta1 in enumerate(numpy.linspace(-numpy.pi/4,numpy.pi/4,3)):
    #    for i2, theta2 in enumerate(numpy.linspace(-numpy.pi/4,numpy.pi/4,3)):
    #        for i3, theta3 in enumerate(numpy.linspace(-numpy.pi/4,numpy.pi/4,3)):
    #            for i4, theta4 in enumerate(numpy.linspace(-numpy.pi/4,numpy.pi/4,3)):
    #                s = copy.deepcopy(sandy)
    #                s.eye_location[0,1] = s.eye_location[0,0] + delta_distance*numpy.cos(direction + theta1)
    #                s.eye_location[1,1] = s.eye_location[1,0] + delta_distance*numpy.sin(direction + theta1)
#
#                    s.eye_location[0,2] = s.eye_location[0,1] + delta_distance*numpy.cos(direction + theta2)
#                    s.eye_location[1,2] = s.eye_location[1,1] + delta_distance*numpy.sin(direction + theta2)
#
#                    s.eye_location[0,3] = s.eye_location[0,2] + delta_distance*numpy.cos(direction + theta3)
#                    s.eye_location[1,3] = s.eye_location[1,2] + delta_distance*numpy.sin(direction + theta3)
#
#                    s.eye_location[0,4] = s.eye_location[0,3] + delta_distance*numpy.cos(direction + theta4)
#                    s.eye_location[1,4] = s.eye_location[1,3] + delta_distance*numpy.sin(direction + theta4)
#
#                    s.ID = ID
#                    storms.append(s)
#                    ID = ID + 1
    
    #import copy
    #ID = 0
    #for il, thetal in enumerate(numpy.linspace(-numpy.pi/6,numpy.pi/6,21)):
    #    s = copy.deepcopy(sandy)
    #    s.eye_location[0,-1] = s.eye_location[0,-2] + delta_distance*numpy.cos(direction + thetal)
    #    s.eye_location[1,-1] = s.eye_location[1,-2] + delta_distance*numpy.sin(direction + thetal)                   
    #    s.ID = ID
    #    storms.append(s)
    #    ID = ID + 1


    #for i, offset in enumerate(numpy.linspace(-3,3,13)):
    #    for j, theta in enumerate(numpy.linspace(-3*numpy.pi/4,numpy.pi/4,10)):
    #        s = copy.deepcopy(sandy)
    #        s.eye_location[0,1] = sandy.eye_location[0,1] + offset
    #        s.eye_location[1,1] = sandy.eye_location[1,1] + offset
    #        s.eye_location[0,0] = s.eye_location[0,1] + distance_from_landfall*numpy.cos(theta)
    #        s.eye_location[1,0] = s.eye_location[1,1] + distance_from_landfall*numpy.sin(theta)
    #        #s.max_wind_speed = 2.0e1
    #        #s.max_wind_radius = 1.0e5
    #        s.ID = ID
    #        storms.append(s)
    #        ID = ID + 1

    #print("Max Wind Speed Sandy: ", control_storm.max_wind_speed, "\n") 
    #print("\nMax Wind Radius Sandy: ", control_storm.max_wind_radius, "\n")
    #print("\nCentral Pressure Sandy: ", control_storm.central_pressure, "\n") 
    #print("\nTime of Sandy: ", control_storm.t, "\n") 
    #print("\nLongitutde of Sandy: ", control_storm.eye_location[0, :], "\n") 
    #print("\nLatitude of Sandy: ", control_storm.eye_location[1, :], "\n") 
    #print("\nStorm Radius of Sandy: ", control_storm.storm_radius, "\n") 
     
    #import copy
    #ID = 0
    #max_wind_speed = np.linspace(1e1,7e1,7)
    #max_wind_radius = np.linspace(0.5e5,2e5,5)
    #storm_radius = np.linspace(5e5,10e5,11)
    #for i in range(len(max_wind_speed)):
    #    for j in range(len(max_wind_radius)):
    #        for k in range(len(storm_radius)):
    #            s = copy.deepcopy(control_storm)
    #            s.max_wind_speed = max_wind_speed[i]
    #            s.max_wind_radius = max_wind_radius[j]
    #            s.storm_radius = storm_radius[k]
    #            s.ID = ID
    #            storms.append(s)
    #            ID = ID+1

    #sys.exit() 
    test = False

    # Counter to track number of jobs 
    # in one batch should not exceed
    # 500 storms
    # N determines the full number of
    # storms we might run.  
    jobs_counter = 0
    if test: 
        N = 1 
    else: 
        N = len(storms)  
   
    while jobs_counter < N: 
        if (500 + jobs_counter > N): 
            jobs_batch = N
        else:
            jobs_batch = 500 + jobs_counter

        num_storms = jobs_batch - jobs_counter 
        print('Create %i jobs' %(num_storms)) 
        run_longisland_job(wind_model  = model, 
                           amr_level   = amr_l,  
                           storms      = storms[jobs_counter : jobs_batch])

        jobs_counter = jobs_batch 
