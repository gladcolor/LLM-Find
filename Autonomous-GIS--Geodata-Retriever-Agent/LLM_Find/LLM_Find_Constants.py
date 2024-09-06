import os
import sys
import configparser

# Get the directory of the current script
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Add the directory to sys.path
if current_script_dir not in sys.path:
    sys.path.append(current_script_dir)

import LLM_Find_Codebase as codebase

# Ensure the configuration is read freshly
def load_config():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_script_dir, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_path)
    return config

# Load the updated configuration
config = load_config()




# use your KEY.
# OpenAI_key = config.get('API_Key', 'OpenAI_key')
# OpenWeather_key = config.get('API_Key', 'OpenWeather_key')
# US_Census_key = config.get('API_Key', 'US_Census_key')


# print("OpenAI_key:", OpenAI_key)


# carefully change these prompt parts!   

#------------- Select suitable data source
select_role = r'''A professional Python programmer in geographic information science (GIScience). You have worked on GIScience for more than 20 years and know every detail and pitfall when collecting data and coding. You know which websites you can get suitable spatial data and know the methods or tricks to download data, such as OpenStreetMap, Census Bureau, or various APIs. You are also experienced in processing the downloaded data, including saving them in suitable formats, map projections, and creating detailed and useful meta-data.
'''

select_task_prefix = r'select a suitable data source from the given list to download the requested geo-spatial data for this task'


data_sources = """
1. OpenStreetMap. You can download the administrative boundaries, street networks, points of interest (POIs) from OpenStreetMap.
2. US Census Bureau boundary. It provides the US administrative boundaries (nation, state, county, tract, and block group level, as well as metropolitan statistic areas.
3. US Census Bureau demography. It provides the demographic and socio-economic data, such as population, gender, income, education, and race.
4. US COVID-19 data by New York Times. Cumulative counts of COVID-19 cases and deaths in the United States, at the state and county level, over time from 2020-01-21 to 2023-03-23. 
5. OpenWeather data. It provides historical, current, and forecast weather data. The historical data can be back to 2023-08. API limited: [Hourly forecast: 4 days, Daily forecast: 16 days, 3 hour forecast: 5 days]
6. ESRI World Imagery (for Export). It is a web map service, providing satellite image tiles. You can download tiles and mosaic them into a large image. 
"""

selection_reply_example = """{'Explanation': "According to the use requests of US state administrative boundary from OpenStreetMap, I should download data from OpenStreetMap.", "Selected data source": 'OpenStreetMap'}
"""

select_requirements = [
    "Return the exact name of the data source as the given names.",
    "If a data source is given in the task, e.g., OpenStreetMap or Census Bureau, you need to select that given data source.",
    "If you need to download the administrative boundary of a place without mentioning the data sources, you can get data from OpenStreetMap."
    "If you need to download the US Census tract and block group boundaries, download them from Census Bureau."
    "Follow the given JSON format.",
    "If you cannot find a suitable data source in the given sources, return a data source you think is most appropriate.",
    "DO NOT make fake data source. If you cannot find any suitable data source, return 'Unknown' as for the 'Selected data source' key in the reply JSON format. DO NOT use ```json and ```",
    
]


data_source_dict = {
    "OpenStreetMap": {"ID": "OpenStreetMap"},
    "US Census Bureau boundary": {"ID": "US_Census_boundary"},
    "US Census Bureau demography": {"ID": "US_Census_demography"},
    "US COVID-19 data by New York Times": {"ID": "COVID_NYT"},
    "OpenWeather data": {"ID": "OpenWeather"},
    "ESRI World Imagery (for Export)": {"ID": "ESRI_world_imagery"},
    "Unknown": {"ID": "Unknown"},
}




#------------- Handbook for OpenStreetMap
handbooks = {'OpenStreetMap':[
               "If the requested area is given in an English name, you need to use `['name:en'='XX']` to filter the place in Overpass queries; otherwise you will get empty results. The `name` tag in OpenStreetMap usually is in the location language.",
                "If you need to download the administrative boundary of a place from OpenStreetMap, please use a Python package named 'OSMnx' by this code line: `ox.geocode_to_gdf(query, which_result=None, by_osmid=False, buffer_dist=None)`. This method is fast. ",
                "If you need to download POIs, you may use the Overpass API, which is faster than OSMnx library. Code example is: `area['SO3166-2'='US-PA']->.searchArea;(nwr[amenity='hospital'](area.searchArea););out center;`",
               "If you need to download polylines, you may use the Overpass API, which is faster than OSMnx library.",
               # 
               # "You can use the bounding box in the Overpass query to filter out the data extent (`west, south, east, north = ox.geocode_to_gdf(place_name).unary_union.bounds`), and using the tags to filter out the data type. DO NOT download all the data first then filter, which it is not feasible. After getting the data in a bounding box, you can use GeoPandas and the boundary to filter out the data in the target area: `gpd.sjoin(gdf, boundary, how='inner', op='within')`.",
                "If you need to use a boundary to filter features in GeoPandas, this is the code: `gpd.sjoin(gdf, boundary, how='inner', op='within')`.",
                "If you need to download multiple administrative boundaries at the same level, e.g., states or provinces, DO NOT use OSMnx because it is slow. You can use Overpass API. Example code: `area['ISO3166-1'='US'][admin_level=2]->.us;(relation(area.us)['admin_level'='4'];);out geom;`. Overpass API is  quicker and simpler; you only need to carefully set up the administrative level.",                
                "Only use OSMnx to obtain the place boundaries; do no use it to download networks or POIs as it is very slow! Instead, use Overpass Query (endpoint: https://overpass-api.de/api/interpreter).",
                "If using Overpass API, you need to output the geometry, i.e., using `out geom;` in the query. The geometry can be accessed by `returned_json['elements']['geometry']`; the gemotry is a list of points as `{'lat': 30.5, 'lon': 114.2}`.",
                "Use GeoPandas, rather than OSGEO package, to create vectors.",
                "If the file saving format is not given in the tasks, save the downloaded files into GeoPackage format.",
                "You need to create Python code to download and save the data. Another program will execute your code directly.",
                "Put your reply into a Python code block, explanation or conversation can be Python comments at the beginning of the code block(enclosed by ```python and ```).",
                "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                "When downloading OSM data, no need to use 'building' tags if it is not asked for.",
                "You need to keep most attributes of the downloaded data, such as place name, street name, road type, and level.",
                "Throw an error if the the program fails to download the data; no need to handle the exceptions.",
                "If you need to convert the OpenStreetMap returned JSON to GeoJSON, you can add this line to the OverPass query: `item ::=::,::geom=geom(),_osm_type=type(), ::id=id();`. Note the converted GeoJSON may only contains polygons, no polygons.",
               f"This is a program for your reference; note that you can improve it: {codebase.OpenStreetMap_code_sample_2}",
                
            ],
 
             #------------- Handbook for US Census Bureau boundary
                'US_Census_boundary':[
                    "If the place of boundaries request is in the USA, you can download boundaries from Census Bureau, which is official and better than OSM. An example link is: https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_{year}_{extend}_{level}_500k.zip. You can change the year and administrative level (state/county) in link accordingly. 'year' is 4-digit. 'extend' can be 'us' or 2-digit state FIPS; when 'extend' = 'us', 'level' can be 'state' and 'county' only, and the downloaded data is national. When 'extend' is 2-digit state FIPS, 'level' can be 'tract' and 'bg' only. 'bg' refers to block groups. E.g., do not set 'extend' to 2-digit FIPS code when download county boundaries for a state. If you need to download counties boundaries, 'extend' must be 'us'.",
                    "If the file saving format is not given in the tasks, save the downloaded files into GeoPackage format.",
                    "You need to create Python code to download and save the data. Another program will execute your code directly."
                    "Put your reply into a Python code block, Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).",
                    "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                    "If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is `gpd.read_file(URL)`. DO NOT download and unzip the file.",
                    "Note Python package 'pandas' has no attribute or method of 'StringIO'.",
                    "Throw an error if the the program fails to download the data; no need to handle the exceptions.",
                    
                ],


                          #------------- Handbook for US Census Bureau demographic
                'US_Census_demography':[
                    f"If you need an API key, you can use this: {US_Census_key}",
                    "Prefer the office APIs, do not use other Python pacakges such as `census`. This is an example: https://api.census.gov/data/2019/acs/acs1?get=NAME,B01001_001E&for=state:*",
                    "Store the returns into CSV files.",
                    "Use 'variable_name + label' as descriptive headers without special characters; e.g.'B01001_002E:Total:!!Male:', the variable label should come from the `label` value in the variable descriptions in https://api.census.gov/data/2022/acs/acs5/variables.json. Note that you may need to change the year and dataset accordingly. You need to download this JSON file and read the variable labels from it. Remove any 'Estimate!!' of the labels in variables.json file.",
                    "Add the year of the data as a column to the saved CSV files.",     
                    "Add the source of the data as a column to the saved CSV files, such as 'ACS 2021'.",  
                    "The variable column names in the saved CSV files should be 'B01001_002E:Total:!!Male:', containing the variable ID and label.",
                    "Put your reply into a Python code block. Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).",
                    "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                    "Add the variable description as Python comments before the queried variables, e.g. `# B15001_001E:Total population`.",
                    "The Census Bureau APIs provide very fine-grained variables, such as `B01001_018E` for male between 60 and 61 years. Some data requests involve multiple variables; you need to carefully use these variables. No more or no less. E.g., higher education attainments need to contain all degrees higher than bachelor for both female and male, if the sex is not explicitly requested in the mission..",
                    "The population needs to contain both male and female, if the sex is not explicitly requested in the mission.",
                    "DO not query only male or female population if the sex is not explicitly requested in the mission.",
                    "DO NOT handle any exceptions since we need to error information for debug.",  
                    "Keep the identifiers of downloaded data: for states and counties, names and FIPS are required; for tract, blockgroup, only FIPS is needed.",
                    "Note that in the API response headers, 'NAME' can refer to state name, 'state' refers to FIPS, not the state name. Do not mix up!",  # 'STNAME' or 
                    "In the GET request, the parameters 'state' and 'county' are not included.",
                    "If requesting total population, carefully consider whether it refers to the entire population of a place or the population of a topic. E.g., B15002_001E (label: Estimate!!Total:) refers to the total population of the concept of 'SEX BY EDUCATIONAL ATTAINMENT FOR THE POPULATION 25 YEARS AND OVER'; B01001_001E (label: Estimate!!Total:) refers to the total population of the concept of 'SEX BY AGE', or the total population of a place. Make sure you carefully understand which `total population` is requested in the mission.",
                    "Carefully think whether the requested data needs to combine multiple Census variables. For example, 'senior population' and 'higher education attainment' needs retrieve multiple variables across age, gender and degree attainment.",
                    "Sometimes you do not need to retrieve multiple variables, since some variables may include others. E.g., B15003_022E (Estimate!!Total:!!Bachelor's degree) consists of B15002_015E (Estimate!!Total:!!Male:!!Bachelor's degree) and B15002_032E (Estimate!!Total:!!Female:!!Bachelor's degree). You can retrieve less variable in such occasions.",
                    "Please return the total population/household along with the requested sub group populations to compute the ratio, which is usually needed in most analyses.",
                    "FIPS or GEOID columns may be str type with leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12).",
                    # "Use the column names from API response, do not name the columns yourself.",
                    "If the saved file name is given, do not change the file name.",
                    # "When requesting educational attainments, B15002 (for population > 25-year) is more commonly used than B15001 (for population > 18-year).",     
                    f"This is a brief variable summary for your reference: {codebase.Census_variables}",
                    f"This is a program for your reference, note that you can improve it: {codebase.US_Census_demography_code_sample}",
                ],

                                       #------------- Handbook for US COVID-19 data by New York Times
                'COVID_NYT':[
                    "The COVID-19 cumulative death and case data can be accessed via: `https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties-{year}.csv`, year can be 2021, 2022,and 2023.",  
                    "The CSV columns are: `date,county,state,fips,cases,deaths`, the data line can be: `2020-01-21,Washington,53,1,0`. Note that the data-type of `fips` column is string, while the `case` and `deaths` are integer. You need to store the data type correctly.",
                    "Put your reply into a Python code block. Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).",
                    "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                ],

                                                    #------------- Handbook for OpenWeather -----
                'OpenWeather':[
                    f"The OpenWeather API key is: {OpenWeather_key}",
                    "The endpoint for current weather is: https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={API key}",  
                    "Hourly forecast for 4 days (96 timestamps) end point is: https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={lat}&lon={lon}&units=metric&appid={API key}.",
                    "Daily Forecast (16 days at most) end point is: api.openweathermap.org/data/2.5/forecast/daily?lat={lat}&lon={lon}&cnt={cnt}&appid={API key}.",
                    "Climate Forecast (30 days) end point is: https://pro.openweathermap.org/data/2.5/forecast/climate?lat={lat}&lon={lon}&appid={API key}.",
                    "The endpoints for historical weather are 1) https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&end={end}&units=metric&appid={API key}, 2) https://history.openweathermap.org/data/2.5/history/city?lat={lat}&lon={lon}&type=hour&start={start}&cnt={cnt}&units=metric&appid={API key}.",
                    "Each query can get one week data at most, including historical and forecast data. You may need to query multiple times if the requested period is longer than a week.",
                    "If the data request does not mention using historical/current/forecast API, you need to get the current time to determine using the forecast or historical API endpoint.",
                    "Need to use metric units. E.g., the temperature units should be Celsius.",
                    "Do not use 'One Call API' since we have not subscribed it.",
                    "Other parameters and values in the API: [mode: default is `json`. cnt: optional, a number of timestamps in response.]",
                    "Put your reply into a Python code block. Explanation or conversation can be Python comments at the beginning of the code block(enclosed by ```python and ```).",
                    "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                    "API calls per minute is 3000, so make your program sleep for a while if you request too many times in a minute.",
                    "Save the results in a CSV file; columns include place name, date (YYYY-MM-DD), hour (e.g., '01'), and all the returned weather variables in separate columns, including sub-levels in all top-levels, such as 'main' and 'weather'. Using '_' to join the top- and sub-levels, e.g., 'main_temp'. Note that the 'weather' node has a list value, e.g., `'weather': [ {'id': 501,'main': 'Rain', 'description': 'moderate rain', 'icon': '10n' }]`. Other nodes have a dictionary value, e.g., `'main': { 'temp': 275.45, 'feels_like': 271.7, 'pressure': 1014, 'humidity': 74, 'temp_min': 274.26, 'temp_max': 276.48}`. Please handle the 'weather' node correctly. ",
                    "Using Python code to numerate the returned sub-level weather variables, rather than using your own memory. ",
                    "Store the requested place name or lat/lon in the result file.",
                    
                ],
                # Note: GPT-4o seems know the API well, for example, the historical one week limit and UNIX time stamp, but it cannot know the current time.

                                                    #------------- Handbook for ESRI World imagery (for export) -----
                'ESRI_world_imagery':[
                    "The endpoint is: https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{row}/{col}. 'row' is the row number from the top, 'col' is the column number from the left. The map projection is WGS 1984 Web Mercator (auxiliary sphere), EPSG: 3857.",
                    "You need to download the image tiles into the given folder (name them as 'z-row-col.jpg'), and then mosaic them into a single TIFF image with jpeg compression; also save a .jpw file for tiles to record the image locations for further merge. The mosaic result needs a .tfw file.",
                    "You will receive a place name or a bounding box of the target area.",
                    "Put your reply into a Python code block. Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).",
                    "The download code is only in a function named 'download_data()'. The last line is to execute this function; do not use `if __name__ == '__main__':`.",
                    "You can use OSMnx Python package to download the boundary of the request place, then use boundary's bounding box to determine the extent of the imagery. Example code: `minx, miny, maxx, maxy = ox.geocode_to_gdf(places).total_bounds`.",
                    "The tile's row and col can be calculated by: `tile_col = int((lon + 180.0) / 360.0 * n); tile_row = int((1.0 - np.log(np.tan(np.radians(lat)) + 1 / np.cos(np.radians(lat))) / np.pi) / 2.0 * n)`.",
                    "Remember how to do name the tiles since you need to mosaic them later.",
                    "DO NOT handle any exceptions since we need to error information for debug.",  
                    f"This is a program for your reference, note that you can improve it: {codebase.ESRI_world_imagery_code_sample}",
                   
                ],
             
            }



 
#------------- download data from a perticular data source
download_role = r'''A professional Python programmer in geographic information science (GIScience). You have worked on GIScience for more than 20 years and know every detail and pitfall when collecting data and coding. You know which websites you can get suitable spatial data and know the methods or tricks to download data, such as OpenStreetMap, Census Bureau, or various APIs. You are also experienced in processing the downloaded data, including saving them in suitable formats, map projections, and creating detailed and useful meta-data. When downloading geo-spatial data, the technical handbook for a particular data source is provided; you can follow it, and write Python code carefully to download the data. 
'''


download_task_prefix = r'download geo-spatial data from the given data source for this task'


download_reply_example = """
```python
import geopandas as gpd
import osmnx as ox
def download_data():
    # data downloading code 
    # downloaded code 
download_data()
```
"""





"""
1. Think step by step.
2. If you need to download the administrative boundary of a place and without mentioning the data sources, you can get data from OSM using OSM package by `ox.geocode_to_gdf(query, which_result=None, by_osmid=False, buffer_dist=None)`. This method is fast. 
3.If the place of boundaries request is in the USA, you can download boundaries from Census Bureau, which is official and better than OSM. An example link is: https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_{year}_{extend}_{level}_500k.zip. You can change the year and administrative level (state/county) in link accordingly. "year" is 4-digit. 'extend' can be 'us' or 2-digit state FIPS; when 'extend' = 'us', 'level' can be 'state' and 'county' only, and the downloaded data is national. When 'extend' is 2-digit state FIPS, 'level' can be 'tract' and 'bg' only. 'bg' refers to block groups. E.g., do not set 'extend' to 2-digit FIPS code when download county boundaries for a state. If you need to download counties boundaries, 'extend' must be 'us'.
4. If the mentioned the saving file format, save the downloaded data in GeoPackage format. 
5. You need to create Python code to download and save the data. Another program will execute your code directly.
6. You can use various technical ways to download the data, such as Overpass QL, Overpass API, OSMnx Python package, Census file downloading link, or Census Python packages.
7. Put your reply into a Python code block, Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).
8. The download code is only in a function named 'download_data()'. The last line is to execute this function.
9. When downloading OSM data, no need to use 'building' tags if it is not asked for.
10. If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.
11. Note Python package 'pandas' has no attribute or method of 'StringIO'.,
12. If a data source is given in the task, e.g., OSM or Census Bureau, you need to download data from that data source.

"""
 
#--------------- constants for debugging prompt generation  ---------------
debug_role =  r'''A professional geo-information scientist and programmer who is good at Python. You have worked on Geographic information science for over 20 years and know every detail and pitfall when processing spatial data and coding. You have significant experience in code debugging. You like to find out debugs and fix code. Moreover, you usually will consider issues from the data side, not only code implementation. Your current job is to debug the code for map generation.
'''

debug_task_prefix = r"You need to correct a program's code based on the given error information and then return the complete corrected code."

debug_requirement = [
                        'Think step by step. Elaborate your reasons for revision before returning the code.',
                        'Correct the code. Revise the buggy parts, but need to keep program structure, i.e., the function name, its arguments, and returns.',                        
                        'You must return the entire corrected program in only one Python code block(enclosed by ```python and ```); DO NOT return the revised part only.',
                        'If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.',
                        'Make necessary revisions only. Do not change the structure of the given code or program; keep all functions.',
                        "Note module 'pandas' has no attribute or method of 'StringIO'",
                        "When doing spatial analysis, convert the involved spatial layers into the same map projection, if they are not in the same projection.",
                        "DO NOT reproject or set spatial data(e.g., GeoPandas Dataframe) if only one layer involved.",
                        "Map projection conversion is only conducted for spatial data layers such as GeoDataFrame. DataFrame loaded from a CSV file does not have map projection information.",
                        "If join DataFrame and GeoDataFrame, using common columns, DO NOT convert DataFrame to GeoDataFrame.",
                        "Remember the variable, column, and file names used in ancestor functions when using them, such as joining tables or calculating.",
                        "You can use OSMnx Python package to download a city, neighborhood, borough, county, state, or country. The code is: `gdf = ox.geocode_to_gdf(place)`. The Overpass API `area['name'='target_placename']` might return emplty results.",
                        # "You usually need to obtain the boundaries first then use it to filter out the target data.",
                        # "When joining tables, convert the involved columns to string type without leading zeros. ",
                        # "If using colorbar for GeoPandas or Matplotlib visualization, set the colorbar's height or length as the same as the plot for better layout.",
                        # "When doing spatial joins, remove the duplicates in the results. Or please think about whether it needs to be removed.",
                        # "Map grid, legend, or colorbar need to show the unit.",
                        'If a Python package is not installed, add the install command such as "pip" at the beginning of the revised code.',
                        # "Show a progressbar (e.g., tqdm in Python) if loop more than 200 times, also add exception handling for loops to make sure the loop can run.",
                        # "When crawl the webpage context to ChatGPT, using Beautifulsoup to crawl the text only, not all the HTML file.",
                        "If using GeoPandas for spatial analysis, when doing overlay analysis, carefully think about use Geopandas.GeoSeries.intersects() or geopandas.sjoin(). ",
                        "Geopandas.GeoSeries.intersects(other, align=True) returns a Series of dtype('bool') with value True for each aligned geometry that intersects other. other:GeoSeries or geometric object. ",
                        "If using GeoPandas for spatial joining, the arguements are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs), how: the type of join, default ‘inner’, means use intersection of keys from both dfs while retain only left_df geometry column. If 'how' is 'left': use keys from left_df; retain only left_df geometry column, and similarly when 'how' is 'right'. ",
                        "Note geopandas.sjoin() returns all joined pairs, i.e., the return could be one-to-many. E.g., the intersection result of a polygon with two points inside it contains two rows; in each row, the polygon attribute is the same. If you need of extract the polygons intersecting with the points, please remember to remove the duplicated rows in the results.",
                        # "GEOID in US Census data and FIPS (or 'fips') in Census boundaries are integer with leading zeros. If use pandas.read_csv() to GEOID or FIPS (or 'fips') columns from read CSV files, set the dtype as 'str'.",
                         # "Before using Pandas or GeoPandas columns for further processing (e.g. join or calculation), drop recoreds with NaN cells in that column, i.e., df.dropna(subset=['XX', 'YY']).",
                        # "Drop rows with NaN cells, i.e., df.dropna(),  if the error information reports NaN related errors."
                        # "Bugs may caused by data, such as map projection inconsistency, column data type mistakes (e.g., int, flota, str), spatial joining type (e.g., inner, outer), and NaN cells.",
                        # "When read FIPS or GEOID columns from CSV files, read those columns as str or int, never as float.",
                        "FIPS or GEOID columns may be str type with leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12), or integer type without leading zeros. Thus, when joining using they, you can convert the integer colum to str type with leading zeros to ensure the success.",
                        # "If you need to make a map and the map size is not given, set the map size to 15*10 inches.",
                        # 'Save the generated map as the file of "output_map.png"; the DPI is 100.',
                        ]

 
 
''' 
NOTE: AREA in Overpass API
Areas are an extension of Overpass API: They constitute a new data type area beside the OSM data types node, way, and relation. So this data is not extracted and updated from the main API, but computed by a special process on the Overpass API server.
https://wiki.openstreetmap.org/wiki/Overpass_API/Areas

Thus, `area[tag=XX]` returns no polygons.

## Convert the OSM JSON to GeoJSON:
[out:json];
( way(51.477,-0.001,51.478,0.001)[name="Blackheath Avenue"];
  node(w);
  relation(51.477,-0.001,51.478,0.001); );
convert item ::=::,::geom=geom(),_osm_type=type(), ::id=id();
out geom;
// https://dev.overpass-api.de/overpass-doc/en/targets/formats.html#json
// Not sure whether the conversion is correct, little official documents. 
// Not good for polygons. GeoJSON results only contain polylines.
'''
 