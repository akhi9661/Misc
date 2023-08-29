import geopandas as gpd
from shapely.geometry import Point
from pyproj import CRS, Transformer
import uuid  # Import the uuid module for generating unique IDs

def reproj_shp(input_shapefile, output_shapefile = None, subset = False, subset_shapefile = None, num_points = 10): 

    # Read the input shapefile
    gdf = gpd.read_file(input_shapefile)

    # Define the target CRS (EPSG:4326)
    target_crs = CRS.from_epsg(4326)

    # Reproject the GeoDataFrame
    gdf = gdf.to_crs(target_crs)

    # Create 'lat' and 'lon' columns
    gdf['lat'] = gdf.geometry.y
    gdf['lon'] = gdf.geometry.x

    # Generate and add unique IDs to the 'name' column
    gdf['name'] = [str(uuid.uuid4()) for _ in range(len(gdf))]
    
    if subset:
        # Take a subset of 10 points
        subset_gdf = gdf.sample(n=num_points, random_state=42)  # Adjust random_state for different subsets
        # Save the subset GeoDataFrame to a new shapefile
        subset_gdf.to_file(subset_shapefile)
    else:
        # Save the reprojected GeoDataFrame to a new shapefile
        gdf.to_file(output_shapefile)
    
    return None

# Input and output file paths
input_shapefile = r'D:\Preetham\Grid.shp'
subset_shapefile = r'D:\Preetham\Grid_gcs_sub.shp'

reproj_shp(input_shapefile = input_shapefile, subset_shapefile = subset_shapefile, subset = True, num_points = 20)
