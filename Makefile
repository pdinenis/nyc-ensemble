# Makefile for Clawpack code in this directory.
# This version only sets the local files and frequently changed
# # options, and then includes the standard makefile pointed to by CLAWMAKE.
 CLAWMAKE = $(CLAW)/clawutil/src/Makefile.common

# See the above file for details and a list of make options, or type
#   make .help
# at the unix prompt.


# Adjust these variables if desired:
# ----------------------------------

CLAW_PKG = geoclaw                  # Clawpack package to use
EXE = xgeoclaw                 # Executable to create
SETRUN_FILE = setrun.py        # File containing function to make data
OUTDIR = _output               # Directory for output
SETPLOT_FILE = setplot.py      # File containing function to set plots
PLOTDIR = _plots               # Directory for plots

# Environment variable FC should be set to fortran compiler, e.g. gfortran

# Compiler flags can be specified here or set as an environment variable
#FFLAGS += -g -C -CB -CU -fpe0 -ftrapuv -fp-model precise -DNETCDF -lnetcdff -I$(NETCDF4_DIR)/include -L$(NETCDF4_DIR)/lib
FFLAGS += -DNETCDF -lnetcdff -I$(NETCDF4_DIR)/include -L$(NETCDF4_DIR)/lib -O2 -ipo -qopenmp -check all 
#FFLAGS += -DNETCDF -lnetcdff -I$(NETCDF4_DIR)/include -L$(NETCDF4_DIR)/lib -O2 -ipo -qopenmp  
#FFLAGS += -DNETCDF -lnetcdff -I$(NETCDF4_DIR)/include -L$(NETCDF4_DIR)/lib -check all -warn all,nodec,interfaces -gen_interfaces -traceback -fpe0 -fp-stack-check -fdiagnostics-color=auto
LFLAGS += -O2 -ipo -qopenmp -L$(NETCDF4_DIR)/lib -lnetcdff


# ---------------------------------
# package sources for this program:
# ---------------------------------

GEOLIB = $(CLAW)/geoclaw/src/2d/shallow
include $(GEOLIB)/Makefile.geoclaw

# ---------------------------------------
# package sources specifically to exclude
# (i.e. if a custom replacement source 
#  under a different name is provided)
# ---------------------------------------

EXCLUDE_MODULES = \

EXCLUDE_SOURCES = \

# ----------------------------------------
# List of custom sources for this program:
# ----------------------------------------

RIEMANN = $(CLAW)/riemann/src

MODULES = \

SOURCES = \
	$(RIEMANN)/rpn2_geoclaw.f \
	$(RIEMANN)/rpt2_geoclaw.f \
	$(RIEMANN)/geoclaw_riemann_utils.f \


#-------------------------------------------------------------------
# Include Makefile containing standard definitions and make options:
include $(CLAWMAKE)


.PHONY: topo all

# Construct the topography data

#topo:
#	../bathy/get_bathy.py ../bathy/

topo:
	bathy/get_bathy.py bathy/

-all:
	$(MAKE) .topo
	$(MAKE) .plots


### DO NOT remove this line - make depends on it ###
