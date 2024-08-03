ESRI_world_imagery_code_sample = r'''
import geopandas as gpd
import osmnx as ox
import requests
import numpy as np
from PIL import Image
from osgeo import gdal
import os

def download_data():
    # Define the target area for which to download the data
    place = 'Japan'

    # Get the boundary of Japan
    # get the first return's bounding box
    url = f"https://nominatim.openstreetmap.org/search?q={place}&format=geojson"
    response = requests.get(url, headers={"User-Agent":"LLM-Find/gladcolor@gmail.com"})
    minx, miny, maxx, maxy = response.json()['features'][0]['bbox']

    # extend the boundary for a point or to small:
    if abs(maxx - minx) < 0.000001:  # note unit is degree
         ext = 0.00005
         maxx = maxx + ext
         minx = minx - ext
         maxy = maxy + ext
         miny = miny - ext 
         
    # Set the zoom level
    z = 6
    n = 2 ** z

    # Calculate the tiling scheme boundaries
    tile_min_col = int((minx + 180.0) / 360.0 * n)
    tile_max_col = int((maxx + 180.0) / 360.0 * n)
    tile_min_row = int((1.0 - np.log(np.tan(np.radians(maxy)) + 1 / np.cos(np.radians(maxy))) / np.pi) / 2.0 * n)
    tile_max_row = int((1.0 - np.log(np.tan(np.radians(miny)) + 1 / np.cos(np.radians(miny))) / np.pi) / 2.0 * n)

    # Create directory to store individual tile images
    save_dir = "tiles"
    os.makedirs(save_dir, exist_ok=True)

    # Download tiles
    for row in range(tile_min_row, tile_max_row + 1):
        for col in range(tile_min_col, tile_max_col + 1):
            url = f"https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{row}/{col}"
            response = requests.get(url)
            tile_path = os.path.join(save_dir, f"{z}-{row}-{col}.jpg")
            with open(tile_path, 'wb') as f:
                f.write(response.content)

    # Stitch the tiles to create a mosaic image
    cols = tile_max_col - tile_min_col + 1
    rows = tile_max_row - tile_min_row + 1
    tile_width, tile_height = Image.open(os.path.join(save_dir, f"{z}-{tile_min_row}-{tile_min_col}.jpg")).size
    mosaic = Image.new('RGB', (cols * tile_width, rows * tile_height))

    for row in range(rows):
        for col in range(cols):
            tile_path = os.path.join(save_dir, f"{z}-{tile_min_row + row}-{tile_min_col + col}.jpg")
            tile = Image.open(tile_path)
            mosaic.paste(tile, (col * tile_width, row * tile_height))

    # Save the mosaic image as a TIFF file
    mosaic_path = "E:/OneDrive_PSU/OneDrive - The Pennsylvania State University/Research_doc/LLM-Find/Downloaded_Data/Japan_image.tif"
    mosaic.save(mosaic_path, "TIFF", compression="jpeg")

    # Save a world file to record the image location. Note that this is just a rough location. Further geo-reference is need to correctly position the downloaded image of Web Mercator Auxiliary Sphere projection.
    x_res = (maxx - minx) / (cols * tile_width)
    y_res = (maxy - miny) / (rows * tile_height)
    tfw_content = f"{x_res}\n0.0\n0.0\n{-y_res}\n{minx}\n{maxy}\n"
    with open(mosaic_path.replace(".tif", ".tfw"), "w") as tfw_file:
        tfw_file.write(tfw_content)

    # Clean up the individual tile images (optional)
    for file in os.listdir(save_dir):
        os.remove(os.path.join(save_dir, file))
    os.rmdir(save_dir)

download_data()
'''

# not used     
""" 
    # boundary = ox.geocode_to_gdf(place)
# minx, miny, maxx, maxy = boundary.total_bounds
If the requested place can be a point, such as Christ the Redeemer statue, you can use the following code to get the location:
#url = f"https://nominatim.openstreetmap.org/search?q={place}&format=geojson"
#response = requests.get(url, headers={"User-Agent":"LLM-Find/gladcolor@gmail.com"})
#minx, miny, maxx, maxy = response.json()['features'][0]['bbox']
"""

US_Census_demography_code_sample = r'''
import requests
import csv
import json

def download_data():
    # Define the endpoint and related configurations
    base_url = "https://api.census.gov/data/2021/acs/acs5"
    api_key = "xxxx"
    dataset_year = "2021"
    dataset_source = f"ACS {dataset_year}"
    
    # Variables we need to fetch
    variables = [
        # B02001_001E:Total population
        "B02001_001E",  
        # B02001_002E:White alone
        "B02001_002E",  
        # B02001_003E:Black or African American alone
        "B02001_003E",  
        # B02001_004E:American Indian and Alaska Native alone
        "B02001_004E",  
        # B02001_005E:Asian alone
        "B02001_005E",  
        # B02001_006E:Native Hawaiian and Other Pacific Islander alone
        "B02001_006E",  
        # B02001_007E:Some other race alone
        "B02001_007E",  
        # B02001_008E:Two or more races
        "B02001_008E",  
    ]

    # Fetch the variable labels
    response = requests.get(f"{base_url}/variables.json")
    variables_metadata = response.json()

    # Helper function to get variable labels
    def get_variable_label(var_name):
        label = variables_metadata['variables'][var_name]['label']
        return label.replace("Estimate!!", "").strip()
    
    # Construct the URL for the data request
    get_vars = ",".join(variables)
    url = f"{base_url}?get={get_vars}&for=block%20group:*&in=state:45 county:079&key={api_key}"
    
    # Download data from Census API
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Prepare the CSV file for writing
    csv_path = "E:\\OneDrive_PSU\\OneDrive - The Pennsylvania State University\\Research_doc\\LLM-Find\\Downloaded_Data\\Census_SC_Richland_race_population.csv"

    # Create header with variable labels
    header = [f"{var}:{get_variable_label(var)}" for var in variables] + ["state_fips", "county_fips", "tract_fips", "block_group_fips", "year", "source"]
    rows = data[1:]  # Skip the header row provided by API
    for row in rows:
        row.extend([dataset_year, dataset_source])
    
    # Write to CSV file
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)

# Execute the function
download_data()
'''


Census_variables = '''
B01001_001E - B01001_049E: male and female population by age.
B02001_001E - B02013_001E: population by race.
B14001_001E - B14001_010E: school enrollment by level of school for the population 3 years and over.
B15003_001E - B15003_025E: educational attainment for the population 25 years and over.
B17026_001E - B17026_013E: ratio of income to poverty level of families in the past 12 months.
B19001_001E - B19001_017E: household income in the past 12 months.
B19013_001E: median household income in the past 12 months.
B19101_001E - B19101_017E: family income in the past 12 months.
B23025_001E - B23025_007E：employment status for the population 16 years and over.
B25091_001E - B25091_023E: mortgage status by selected monthly owner costs as a percentage of household income in the past 12 months.
B27001_001E - B27001_057E：male and female population health insurance coverage status.
C17002_001E - C17002_008E: ratio of income to poverty level in the past 12 months.
'''


OpenStreetMap_code_sample_1 = r'''
## The following code is to download the railway network in Wuhan, Hubei, China.
# Import necessary libraries
import geopandas as gpd
import requests
import json
import osmnx as ox

def download_data():
    # Define the area for Wuhan, Hubei, China
    place_name = "Wuhan, Hubei, China"

    # Get the bounding box of Wuhan using OSMnx
    gdf = ox.geocode_to_gdf(place_name)
    west, south, east, north = gdf.unary_union.bounds

    # Define Overpass API query to get railway network in the bounding box
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
        way["railway"]({south},{west},{north},{east});
        relation["railway"]({south},{west},{north},{east});
    );
    out geom;
    """

    # Send request to Overpass API
    response = requests.get(overpass_url, params={'data': overpass_query})
    response.raise_for_status()  # Automatically raises an error for bad status codes

    # Parse the JSON response
    data = response.json()

    # Extract elements with their geometries
    features = []
    for element in data['elements']:
        if 'geometry' in element:
            points = [(point['lon'], point['lat']) for point in element['geometry']]
            # Convert all property values to str
            properties = {
                key: ', '.join(map(str, value)) if isinstance(value, list) else str(value)
                for key, value in element.items() if key != 'geometry'
            }

            if element['type'] == 'way':
                features.append({
                    'type': 'Feature',
                    'geometry': {'type': 'LineString', 'coordinates': points},
                    'properties': properties
                })
            elif element['type'] == 'relation':
                for member in element['members']:
                    if member['type'] == 'way' and 'geometry' in member:
                        points = [(point['lon'], point['lat']) for point in member['geometry']]
                        properties = {
                            key: ', '.join(map(str, value)) if isinstance(value, list) else str(value)
                            for key, value in element.items() if key != 'geometry'
                        }
                        features.append({
                            'type': 'Feature',
                            'geometry': {'type': 'LineString', 'coordinates': points},
                            'properties': properties
                        })

    # Create a GeoDataFrame
    gdf_railway = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')

    # Save to GeoPackage
    output_file = r"E:\OneDrive_PSU\OneDrive - The Pennsylvania State University\Research_doc\LLM-Find\Downloaded_Data\Wuhan_Railway_network.gpkg"
    gdf_railway.to_file(output_file, layer='railway_network', driver='GPKG')

# Execute the function
download_data()
'''


OpenStreetMap_code_sample_2 = r'''
# Below is a program to download the province boundaries of Cuba.
import geopandas as gpd
import pandas as pd
import osmnx as ox
import requests
import json
from shapely.ops import linemerge, unary_union, polygonize
from shapely.geometry import MultiLineString, Polygon, MultiPolygon, LineString
from shapely.ops import polygonize

def download_data():
    # Define Overpass API query to download province boundaries of Cuba
    # This Overpass query is good for multiple polygons.
    # `boundary=ox.place_to_gdf(place)` is to get the first polygon returned by the Nominatim.org API. 
    osm_id = ox.geocode_to_gdf(place_name)['osm_id'][0] # get the osm_id then get the relation by osm_id.
    

    # IMPORTANT: keep the pipeline to form the Overpass query; it has been manually verified!
    # Note that area(osm_id) is not correct because it is not the native OpenStreetMap data structure.
    overpass_url = "https://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    relation({osm_id});   // Note that it is 'relation()'! 
    map_to_area->.rel;   // DO not forget this line!
    relation(area.rel)["admin_level"="4"];
    out geom;  // keep geom!
    """

    # if only request the boundary only, use `gdf = ox.geocode_to_gdf()` is the fastest way! You do not need to use Overpass and then parse the reply.
  
    # Send request to Overpass API
    response = requests.get(overpass_url, params={'data': overpass_query})
    response.raise_for_status()  # Automatically raises an error for bad status codes
    data = response.json()
    
    # Parse the JSON response
    property_list = []
    geometry_list = []
    
    for element in data['elements']:  # each province
        way_list = []    
        outer_lines = []
        inner_lines = []
        
        for member in element.get('members', []):  # each way/polyline
            
            if 'geometry' in member:
                if member['type'] == 'way':
                    way_points = [(point['lon'], point['lat']) for point in member['geometry']]
                    line_string = LineString(way_points)
                    if member['role'] == 'outer':
                        outer_lines.append(line_string)
    
                    if member['role'] == 'inner':
                        inner_lines.append(line_string)
                    
        # Create polygon. We use Multi-polygon to represent all polygons
        merged = linemerge([*outer_lines]) # merge LineStrings
        borders = unary_union(merged) # linestrings to a MultiLineString    
        outer_polygons = list(polygonize(borders))
        outer_polyon = MultiPolygon(outer_polygons)
    
        if len(inner_lines) > 0:
            merged = linemerge([*inner_lines]) # merge LineStrings
            borders = unary_union(merged) # linestrings to a MultiLineString    
            inner_polyons = list(polygonize(borders))
            inner_polyon = MultiPolygon(inner_polyons)
            final_polygon = outer_polyon.difference(inner_polyon)
            
        else:
            final_polygon = outer_polyon
    
        geometry_list.append(final_polygon)
    
        # extract the properties
        properties = {
            key: ', '.join(map(str, value)) if isinstance(value, list) else str(value)
            for key, value in element.items() if key not in {'geometry', 'members'}
        }
        property_list.append(properties)
     
    df = pd.DataFrame.from_dict(property_list)
    
    gdf = gpd.GeoDataFrame(df, geometry=geometry_list)
    gdf.crs = 'EPSG:4326'
    
    # # Save to GeoPackage
    output_file = r"E:\Cuba_Province_boundary.gpkg"
    gdf.to_file(output_file, layer='province_boundaries', driver='GPKG')

download_data()
'''

OpenTopography_code_sample = r'''
import requests
import osmnx as ox

def download_data():
    place_name = "Great Smoky Mountains National Park, USA"
    
    # Get the bounding box for the place name
    gdf = ox.geocode_to_gdf(place_name)
    west, south, east, north = gdf.unary_union.bounds
    
    # Set the OpenTopography API parameters
    demtype = "SRTMGL3"  # This is 90m resolution
    output_format = "GTiff"
    api_url = (
        f"https://portal.opentopography.org/API/globaldem?"
        f"demtype={demtype}&south={south}&north={north}&west={west}&east={east}&outputFormat={output_format}&API_Key=XXXX"
    )
    
    # Send the request to download the data
    response = requests.get(api_url)
    
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    
    # Save the downloaded data to the specified path
    output_path = r"E:\Great Smoky Mountains National Park.tif"
    
    with open(output_path, 'wb') as file:
        file.write(response.content)

# Execute the function to download the data
download_data()
'''