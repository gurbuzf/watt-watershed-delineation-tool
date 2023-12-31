import random
import string
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.features import geometry_mask, shapes
from shapely.geometry import Polygon, box
from src.utils import geopandas2KML


def rasterize_array(array, profile):
    """
    Rasterizes a NumPy array using the profile of a TIFF file.

    Args:
        array (np.ndarray): NumPy array to be rasterized.
        profile (dict): Metadata profile of the reference TIFF file.

    Returns:
        rasterio.DatasetReader: Rasterized rasterio Dataset object.

    Raises:
        ValueError: If the dimensions of the array and the profile do not match.

    Notes:
        - The function uses the rasterio library to rasterize the array.
        - The profile should contain the necessary information to define the output raster,
          such as the spatial reference system, resolution, and other properties.

    """

    # Check if the array dimensions match the profile dimensions
    if array.shape != (profile["height"], profile["width"]):
        raise ValueError(
            "Array dimensions do not match the profile dimensions.")

    # Convert the array to a supported data type
    # Change the data type here as per your needs
    array = array.astype(np.uint8)

    # Extract the bounds from the transform
    bounds = rasterio.transform.array_bounds(
        profile["height"], profile["width"], profile["transform"])
    extent = box(*bounds)

    # Create a new in-memory rasterio Dataset
    mem_profile = profile.copy()
    mem_profile.update(dtype=array.dtype, count=1)

    with rasterio.MemoryFile() as memfile:
        with memfile.open(**mem_profile) as dst:
            # Rasterize the array
            mask = geometry_mask([extent], out_shape=(profile["height"], profile["width"]),
                                 transform=profile["transform"], all_touched=False, invert=False)
            dst.write(array, 1)
            dst.write_mask(mask)

        # Read the rasterio Dataset object
        raster = memfile.open()

    return raster


def raster_to_polygon(raster_dataset, save_polygon=True, polygon_save_path=None, file_extension=None):
    """
    Convert a raster with binary values to a polygon.

    Args:
        raster_dataset (rasterio.DatasetReader): Rasterio dataset reader object.
        save_polygon (bool, optional): Flag indicating whether to save the polygon as a GeoJSON file. Defaults to True.
        polygon_save_path (str, optional): Path to save the GeoJSON file. If None, a random filename will be generated. Defaults to None.
        file_extension (str, optional): File extension for saving the polygon file (e.g., 'geojson', 'kml'). Defaults to None.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing the polygon geometry.

    Raises:
        ValueError: If the raster data dtype is not supported.

    Notes:
        - The raster file should contain binary values where 1 represents the area to be converted to a polygon.
        - The function uses rasterio and shapely libraries to perform the conversion.
    """

    # Read the raster band 1 as a numpy array
    raster_array = raster_dataset.read(1)

    # Convert the boolean mask to an integer mask
    mask = raster_array.astype('uint8')

    # Generate polygons from the mask
    shapes_iter = shapes(mask, transform=raster_dataset.transform, connectivity=8)
    polygons = [shape for shape, value in shapes_iter if value == 1]

    # Convert the generated shapes to a GeoDataFrame
    if len(polygons) > 0:
        # Extract exterior coordinates
        coordinates = polygons[0]['coordinates'][0]

        geom = Polygon(coordinates)

        gdf = gpd.GeoDataFrame({'geometry': [geom]}, crs=raster_dataset.crs)

        # Convert the geometry to a Cylindrical Equal Area (cea) projection
        gdf['geometry'] = gdf['geometry'].to_crs({'proj': 'cea'})

        # Calculate and round the area in square kilometers
        gdf["CalculatedArea[km2]"] = round(gdf.area / 10**6, 2)

        # Convert the geometry back to the default EPSG:4326 projection
        gdf = gdf.to_crs(epsg=4326)

        if save_polygon:
            if polygon_save_path is None:
                # Generate a random filename if not provided
                polygon_save_path = ''.join(random.choices(
                    string.ascii_lowercase + string.digits, k=10)) + f'.{file_extension}'
            else:
                # Ensure the provided path has the correct file extension
                if not polygon_save_path.endswith(f'.{file_extension}'):
                    polygon_save_path += f'.{file_extension}'

            # Save the GeoDataFrame to the specified file format
            if file_extension == "kml":
                geopandas2KML(gdf, polygon_save_path, vector_type="polygon")
            elif file_extension == "geojson":
                gdf.to_file(polygon_save_path, driver="GeoJSON")

        return gdf
    else:
        raise ValueError("No valid geometry objects found for rasterize.")
