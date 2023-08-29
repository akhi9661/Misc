import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer

# Input CSV file path
input_csv = r'D:\Preetham\Grid_New.csv'

# Read the CSV into a pandas DataFrame
df = pd.read_csv(input_csv)

# UTM Zone 44 CRS definition
utm_crs = 'EPSG:32644'

# Target CRS (EPSG:4326)
target_crs = 'EPSG:4326'

# Create a Transformer for coordinate transformation
transformer = Transformer.from_crs(utm_crs, target_crs, always_xy=True)

# Create a geometry column using the UTM coordinates
geometry = [Point(transformer.transform(x, y)) for x, y in zip(df['x'], df['y'])]

# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs=target_crs)

# Save the GeoDataFrame to a shapefile
output_shapefile = r'D:\Preetham\Grid.shp'
gdf.to_file(output_shapefile)
