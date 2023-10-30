# Two modes can be adopted. 'single' or 'partial'.
# Single Mode:
# Partial Mode:

MODE = 'partial'

# The directory of the txt file including outlet points.
# The file must be tab limited.
# The file must consists of the following headers. ['id', 'name', 'long', 'lat', 'area[km2]']
# id: a unique number identifying a particular point
# name: a unique name for the point.
# long: longitude - lat: latitude
# area: upstream area of the pour point if previously known. If not, leave empty.
OUTLETS = "../AGI-Havzalar/input/liste.csv"


# If single MODE is used, this becomes trivial. This can be set None or empty string "".
WATERSHEDS = "data/vector/simplified_watershed_borders.geojson"

RIVERS = "data/vector/river/"

FLOW_ACCUMULATION = "data/raster/flow_accumulation/"

DRAINAGE_DIRECTION = "data/raster/drainage_direction/"

# True if the progress of the calculations is wanted to be printed out.
VERBOSE = False

# Number of neighboring pixels to consider
# in search of the neigboring pixel with the highest flow accumualtion.
# 1 is recommended to reduce the potential deviations from the original pour point.
PIXEL2SEARCH = 1

# The directory where the results to be stored.
RESULTS = "../AGI-Havzalar/results_bursa/"

MAX_STRAHLER = 1

VECTOR_EXTENSION = "kml"
