# radolan2hdf5

Convert RADOLAN data to plain daily hdf5 without metadata.

## Usage

`$ python radolan2hdf5.py <config file>`

## Configuration file

You can just copy the following part into a file as a template for your config file:

```
[filing]
# Directory with the monthly reanalysis tar files
monthlytardir = e:/temp/ry

# Monthly tar file name pattern (do not change)
monthlytarfile = RY2017.002_%%d%%02d.tar

# Daily tar.gz file naming pattern (do not change)
dailytarfile = RY2017.002_%%d%%02d%%02d.tar.gz

# Relative path to temporary directory 1 (will be deleted!)
tmpdir = tmp

# Relative path to temporary directory 2 (will be deleted!)
tmpdir2 = tmp2

# Directory where to store the hdf5 files
hdf5dir = e:/temp/ry/hdf5

# Desired name pattern for hdf5 files (do not change)
hdf5name = ry_%%04d%%02d%%02d.hdf5

# Kind of a log file for missing time steps
missing = missing_ry.txt

[time]
# First day that should be processed
start = 2002-01-01

# Last day that should be processed
end = 2002-01-0

[grid]
# Expected number of rows in RADOLAN grid (do not change)
nx = 1100

# Expected number of columns in RADOLAN grid (do not change)
ny = 900
```