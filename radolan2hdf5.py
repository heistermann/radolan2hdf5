import tarfile
import os
import wradlib
import itertools
import datetime as dt
import shutil
import calendar
import numpy as np
import h5py
import sys
from configparser import ConfigParser

print("\n\n\n==================================\n")
print("Convert RADOLAN Reanalysis to HDF5\n")

try:
    conffile = sys.argv[1]
except:
    conffile = "my.conf"
    
conf = ConfigParser()

try:
    conf.read(conffile)
    print("Using config file: %s" % conffile)
except:
    raise Exception("Could not read configuration file: %s" % conffile)

# Transfer values from conf
monthlytardir = conf["filing"]["monthlytardir"]
monthlytarfile = conf["filing"]["monthlytarfile"]
dailytarfile = conf["filing"]["dailytarfile"]
tmpdir = conf["filing"]["tmpdir"]
tmpdir2 = conf["filing"]["tmpdir2"]
hdf5dir = conf["filing"]["hdf5dir"]
hdf5name = conf["filing"]["hdf5name"]
missing = conf["filing"]["missing"]

nx = int(conf["grid"]["nx"])
ny = int(conf["grid"]["ny"])

start = dt.datetime.strptime(conf["time"]["start"], "%Y-%m-%d")
end = dt.datetime.strptime(conf["time"]["end"], "%Y-%m-%d")

print("Processing period: %s until %s\n" % (conf["time"]["start"], conf["time"]["end"]))

def add_one_month(dt0):
    dt1 = dt0.replace(day=1)
    dt2 = dt1 + dt.timedelta(days=32)
    dt3 = dt2.replace(day=1)
    return dt3

# Create a list of months between start and end
months = [start]
dt0 = start
# in case end is in the same month as start
end_ = end.replace(day=1)
while dt0 < end_:
    dt0 = add_one_month(dt0)
    months.append(dt0)

missing_f = open(missing, "a")

for month in months: 
    
    # Create tmp dir
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    
    # Extract monthly tar
    tfpath = os.path.join(monthlytardir, monthlytarfile % (month.year, month.month))
    print("Monthly tar: %s" % tfpath)
    with tarfile.open(tfpath) as tf:
        tf.extractall(path=tmpdir)
    
    # Iterate over all days of the month
    for day in range(1, calendar.monthrange(month.year, month.month)[1] + 1):
        dt_day = dt.datetime(month.year, month.month, day)
        if dt_day > end:
            break
        if dt_day < start:
            continue
        tfpath = os.path.join(tmpdir, dailytarfile % (month.year, month.month, day))
        # Extract 5 minute data from one day
        try:
            print("\tDaily tar: %s" % tfpath, end="")
            with tarfile.open(tfpath) as tf:
                tf.extractall(path=tmpdir2)
        except FileNotFoundError:
            missing_f.write("MISSING DAY: " + tfpath + "\n")
            continue
        except:
            raise Exception("Some unexpected error.")

        # Create container
        data = np.zeros((24*12,nx,ny)).astype(np.float16) * np.nan
        
        # Create hdf5 file and dataset
        h5file = os.path.join(hdf5dir, hdf5name % (month.year, month.month, day))
        with h5py.File(h5file, 'w') as f:
            dset = f.create_dataset("data", data.shape, dtype=np.float16, compression="gzip")
            min5s = wradlib.util.from_to(dt_day.strftime("%Y-%m-%d 00:00:00"),
                                         dt_day.strftime("%Y-%m-%d 23:55:00"), 60*5)
            for i, dtime in enumerate(min5s):
                ryfile = dtime.strftime("raa01-ry2017.002_10000-%y%m%d%H%M-dwd---bin")
                rypath = os.path.join(tmpdir2, ryfile)
                try:
                    data[i] = wradlib.io.read_radolan_composite(rypath, missing=np.nan)[0]
                    os.remove(rypath)    
                except FileNotFoundError:
                    print(".", end="")
                    missing_f.write(ryfile + "\n")
                    continue
                except EOFError:
                    print(".", end="")
                    missing_f.write(ryfile + "\n")
                    continue
                except OSError:
                    print(".", end="")
                    missing_f.write(ryfile + "\n")
                    continue
                except:
                    raise Exception("Some unexpected error.")
            # Write all data to hdf5 file
            dset[:] = data
        
        # Remove tmp2 dir including files
        shutil.rmtree(tmpdir2)
        print()

    # Remove tmp dir including files
    shutil.rmtree(tmpdir) 

missing_f.close()