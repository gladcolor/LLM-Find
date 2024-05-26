import configparser
config = configparser.ConfigParser()
config.read('config.ini')

# use your KEY.
OpenAI_key = config.get('API_Key', 'OpenAI_key')
# print("OpenAI_key:", OpenAI_key)


# carefully change these prompt parts!   

#------------- Select suitable data source
select_role = r'''A professional Python programmer in geographic information science (GIScience). You have worked on GIScience for more than 20 years and know every detail and pitfall when collecting data and coding. You know which websites you can get suitable spatial data and know the methods or tricks to download data, such as OpenStreetMap, Census Bureau, or various APIs. You are also experienced in processing the downloaded data, including saving them in suitable formats, map projections, and creating detailed and useful meta-data.
'''

select_task_prefix = r'select a suitable data source from the given list to download the requested geo-spatial data for this task'


data_sources = """
1. OpenStreetMap. You can download the administrative boundaries, street networks, points of interest (POIs) from OpenStreetMap.
2. US Census Bureau. It provides the Census and demographic data, US administrative boundaries (nation, state, county, tract, and block group level; also metroplitan statistic areas.
3. US COVID-19 data by New York Times. Cumulative counts of COVID-19 cases and deaths in the United States, at the state and county level, over time. 
"""

selection_reply_example = """{'Explaination': "According to the use requests of US state administrative boundary from OpenStreetMap, I should download data from OpenStreetMap.", "Selected data source": 'OpenStreetMap'}
"""

select_requirements = [
    "Return the exact name of the data source as the given names.",
    "If a data source is given in the task, e.g., OpenStreetMap or Census Bureau, you need to select that given data source.",
    "If you need to download the administrative boundary of a place and without mentioning the data sources, you can get data from OpenStreetMap."
    "If you need to download the US Census tract and block group boundaries, download them from Census Bureau."
    "Follow the given JSON format.",
    "If you cannot find a suitable data source in the given sources, return a data source you think is most appropriate.",
    "DO NOT make fake data source. If you cannot find any suitable data source, return 'Unknown' as for the 'Selected data source' key in the reply JSON format. DO NOT use ```json and ```",
    
]


data_source_dict = {
    "OpenStreetMap": {"ID": "OpenStreetMap"},
    "US Census Bureau": {"ID": "US_Census"},
    "US COVID-19 data by New York Times": {"ID": "COVID_NYT"},
    "Unknown": {"ID": "Unknown"},
}

#------------- Handbook for OpenStreetMap
handbooks = {'OpenStreetMap':[
                "If you need to download the administrative boundary of a place from OpenStreetMap, please use a Python package named 'OSMnx' by this code line: `ox.geocode_to_gdf(query, which_result=None, by_osmid=False, buffer_dist=None)`. This method is fast. ",
                "If you need to download POIs, you may use the Overpass API, which is faster than OSMnx library. Code example is: `area['SO3166-2'='US-PA']->.searchArea;(nwr[amenity='hospital'](area.searchArea););out center;`",
               "If you need to download polylines, you may use the Overpass API, which is faster than OSMnx library.",
               "You need to use OSMnx Python package to download cities, neighborhoods, boroughs, counties, states, or countries. The code is: `gdf = ox.geocode_to_gdf(places)`. The Overpass API `area['name'='target_placename']` usually return emplty results; do not use it. You usually need to obtain the boundaries first then use it to filter out the target data.",
               "You can use the bounding box in the Overpass query to filter out the data extent (`west, south, east, north = ox.geocode_to_gdf(place_name).unary_union.bounds`), and using the tags to filter out the data type. DO NOT download all the data first then filter, which it is not feasible.",
                "Only use OSMnx to obtain the place boundaries; do no use it to download networks or POIs as it is very slow! Instead, use Overpass Query (endpoint: https://overpass-api.de/api/interpreter).",
                "If using Overpass API, you need to output the geometry, i.e., using `out geom;` in the query. The geometry can be accessed by `returned_json['elements']['geometry']`; the gemotry is a list of points as `{'lat': 30.5, 'lon': 114.2}`.",
                "Use GeoPandas, rather than OSGEO package to create vectors.",
                "If the file saving format is not given in the tasks, save the downloaded files into GeoPackage format.",
                "You need to create Python code to download and save the data. Another program will execute your code directly."
                " Put your reply into a Python code block, Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).",
                "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                "When downloading OSM data, no need to use 'building' tags if it is not asked for.",
                "Need to keep most attributes of the downloaded data, such as place name, street name, road type and level.",
                
            ],

             #------------- Handbook for US Census Bureau
                'US_Census':[
                    "If the place of boundaries request is in the USA, you can download boundaries from Census Bureau, which is official and better than OSM. An example link is: https://www2.census.gov/geo/tiger/GENZ2021/shp/cb_{year}_{extend}_{level}_500k.zip. You can change the year and administrative level (state/county) in link accordingly. 'year' is 4-digit. 'extend' can be 'us' or 2-digit state FIPS; when 'extend' = 'us', 'level' can be 'state' and 'county' only, and the downloaded data is national. When 'extend' is 2-digit state FIPS, 'level' can be 'tract' and 'bg' only. 'bg' refers to block groups. E.g., do not set 'extend' to 2-digit FIPS code when download county boundaries for a state. If you need to download counties boundaries, 'extend' must be 'us'.",
                    "If the file saving format is not given in the tasks, save the downloaded files into GeoPackage format.",
                    "You need to create Python code to download and save the data. Another program will execute your code directly."
                    " Put your reply into a Python code block, Explanation or conversation can be Python comments at the begining of the code block(enclosed by ```python and ```).",
                    "The download code is only in a function named 'download_data()'. The last line is to execute this function.",
                    "If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is `gpd.read_file(URL)`. DO NOT download and unzip the file.",
                    "Note Python package 'pandas' has no attribute or method of 'StringIO'.",
                ],
    
            }



#------------- download data from a perticular data source
download_role = r'''A professional Python programmer in geographic information science (GIScience). You have worked on GIScience for more than 20 years and know every detail and pitfall when collecting data and coding. You know which websites you can get suitable spatial data and know the methods or tricks to download data, such as OpenStreetMap, Census Bureau, or various APIs. You are also experienced in processing the downloaded data, including saving them in suitable formats, map projections, and creating detailed and useful meta-data. When downloading geo-spatial data, the handbook for a perticular data source is provided, you can follow it, and write Python code carefully to download the data. 
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

#--------------- constants for graph generation  ---------------
graph_role = r'''A professional cartographer and programmer good at Python. You have worked on cartography for more than 20 years and know every detail and pitfall when visualizing spatial data and coding. You know how to set up workflows for cartography tasks well. You have significant experience in visualizing spatial data and graph theory. You are also experienced in generating maps using Matplotlib, GeoPandas, and other interactive Python packages, such as Plotly.
'''

graph_task_prefix = r'Generate a graph (data structure) only, whose nodes are a series of consecutive steps to make a map, including visualizing the data add map elements such as title, legend, scalebar, label, and annotation.: '

graph_reply_exmaple = r"""
```python
import networkx as nx
G = nx.DiGraph()
# Add nodes and edges for the graph
# 1 Load boundary shapefile
G.add_node("boundary_shp_url", node_type="data", path="https://xxx/boundary.zip", description="Boundary shapefile URL")
G.add_node("load_boudary_shp", node_type="operation", description="Load boundary shapefile")
G.add_edge("boundary_shp_url", "load_boudary_shp")
G.add_node("boundary_gdf", node_type="data", description="Boundary GeoDataFrame")
G.add_edge("load_boudary_shp", "boundary_gdf")
...
```
"""
graph_requirement = [   
                        'Think step by step.',
                        'Steps and data (both input and output) form a graph stored in NetworkX. Disconnected components are NOT allowed.',
                        'Each step is a data process operation: the input can be data paths or variables, and the output can be data paths or variables.',
                        'There are two types of nodes: a) operation node, and b) data node (both input and output data). These nodes are also input nodes for the next operation node.',
                        'The input of each operation is the output of the previous operations, except those that need to load data from a path or need to collect data.',
                        'You need to name the output data node carefully, making they human readable but not too long.',
                        'The data and operation form a graph.',
                        'The first operations are data loading or collection, and the output of the last operation is to generate map(s).',
                        'Operation nodes need to connect via output data nodes; DO NOT connect the operation node directly.',
                        'The node attributes include: 1) node_type (data or operation), 2) data_path (data node only, set to "" if not given), and description. E.g., {"name": "County boundary", "data_type": "data", "data_path": "D:\\Test\\county.shp",  "description": "County boundary for the study area"}.',
                        'The connection between a node and an operation node is an edge.', 
                        'Add all nodes and edges, including node attributes to a NetworkX instance. DO NOT change the attribute names.',
                        'DO NOT generate code to implement the steps.',
                        'Join the attribute to the vector layer via a common attribute if necessary.',
                        'Put your reply into a Python code block, NO explanation or conversation outside the code block(enclosed by ```python and ```).',
                        'Note that GraphML writer does not support class dict or list as data values.',
                        'You need to use the given spatial data (e.g., vector or raster) to make a map.',
                        'A map usually contains several map elements, such as title, north arrow scalebar, legend, label, and annotation.',
                        'Create an operation node to draw each map element, you can determine which element is needed according to user input or based on your reasoning.',
                        'Add a map element via an individual operation node. The nodes of adding map elements should be successive.',
                        'Do not put the GraphML writing process as a step in the graph.',
                        'Keep the graph concise; DO NOT use too many operation nodes.',
  
                         ]

  

#--------------- constants for operation generation  ---------------
operation_role = r'''A professional cartographer and programmer good at Python. You have worked as a cartographer for over 20 years, and you know every detail and pitfall when processing and visualizing spatial data and using code to generate the map. You know how to design and implement a function that meets the interface between other functions well. Your program is always robust, considering the various data circumstances, such as column data types, avoiding mistakes when joining tables, and removing NaN cells before further processing. You have a good feeling of overview, meaning functions in your program are coherent and connect well, such as function names, parameter types, and the calling orders. You are also super experienced in generating maps using GeoPandas, Matplotlib, and Plotly. Your current job is to write a serial of Python function to generate a map.
'''

operation_task_prefix = r'You need to generate a Python function to do: '

operation_reply_exmaple = """
```python
# Loading CSV file for further use.
def Load_csv(tract_population_csv_url="https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv"):
# Description: Load a CSV file from a given URL
# tract_population_csv_url: Tract population CSV file URL
tract_population_df = pd.read_csv(tract_population_csv_url)
return tract_population_df
```
"""

operation_requirement = [                         
                        'DO NOT change the given variable names and paths.',
                        'Put your reply into a Python code block(enclosed by ```python and ```), NO explanation or conversation outside the code block. Function description can be given as comments before generating the Python function.',
                        'If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.',
                        "You need to receive the data from the functions. DO NOT load in the function if other functions have loaded the data and returned it in advance.",
                        "Use the latest Python modules and methods.",
                        "When doing spatial analysis, convert the involved spatial layers into the same map projection if they are not in the same projection.",
                        "Keep the needed table columns for the further steps.",
                        "Remember the variable, column, and file names used in ancestor functions when using them, such as joining tables or calculating.",                        
                        "DO NOT use 'if __name__ == '__main__:' statement because this program needs to be executed by exec().",
                        "Use the Python built-in functions or attributes. If you do not remember, DO NOT make up fake ones, just use alternative methods.",
                        "Pandas library has no attribute or method 'StringIO', so 'pd.compat.StringIO' is wrong; you need to use 'io.StringIO' instead.",
                        "If you need to make a map and the map size is not given, set the map size to 15*10 inches.",
                        'When you add a color bar, make sure it has a suitable size, such as not longer than the map height or width.',    
                        "When adding the map grid, colorbar, and scalebar, you need to show the unit, such as meter, mile, or km. For the scale bar, show the geo-distance only, no need to show the map distance; e.g., show 1 km, not 1 mm.",
                        "if the operation is to generate a scale bar, these code lines could be your reference: from matplotlib_scalebar.scalebar import ScaleBar; ax.add_artist(ScaleBar(1))",
                        'If the operation is to save a map, save the generated map with the file name as "output_map.png", the DPI is 100.',
                        ]


#--------------- constants for assembly prompt generation  ---------------
assembly_role =  r'''A professional cartographer and programmer good at Python. You have worked on cartography for more than 20 years and know every detail and pitfall when visualizing spatial data and coding. You are very good at assembling functions and small programs. You know how to make programs robust.
'''

assembly_requirement = ['You can think step by step. ',
                    "Each function is one step to solve the question. ",
                    "The output of the final function is to generate a map.",
                    "Put your reply in a code block(enclosed by ```python and ```), NO explanation or conversation outside the code block.",              
                    "Save the generated map as the file of 'output_map.png'. If use matplotlib, the function is: matplotlib.pyplot.savefig(*args, **kwargs).",
                    "The program is executable; put it in a function named 'assembely_solution()' then run it, but DO NOT use 'if __name__ == '__main__:' statement because this program needs to be executed by exec().",
                    "Use the built-in functions or attribute, if you do not remember, DO NOT make up fake ones, just use alternative methods.",
                    'If the operation is to save a map, save the generated map with the file name as "output_map.png", the DPI is 100.',
                    ]

#--------------- constants for direct request prompt generation  ---------------
direct_request_role = r'''A professional Geo-information scientist and programmer good at Python. You have worked on Geographic information science for more than 20 years, and know every detail and pitfall when processing spatial data and coding. Your programs are always concise and robust, considering the various data circumstances, such as map projections, column data types, and spatial joinings. You are also super experienced in generating maps.
'''

direct_request_task_prefix = r'Write a Python program'

direct_request_reply_exmaple = """
```python',

```
"""

direct_request_requirement = [
                        "You can think step by step.",
                        'DO NOT change the given variable names and paths.',
                        'Put your reply into a Python code block(enclosed by ```python and ```), NO explanation or conversation outside the code block.',
                        'If using GeoPandas to load a zipped ESRI shapefile from a URL, the correct method is "gpd.read_file(URL)". DO NOT download and unzip the file.',
                        "Generate descriptions for input and output arguments.",
                        "Note module 'pandas' has no attribute or method of 'StringIO'.",
                        "Use the latest Python modules and methods.",
                        "When doing spatial analysis, convert the involved spatial layers into the same map projection, if they are not in the sample projection.",
                        # "DO NOT reproject or set spatial data(e.g., GeoPandas Dataframe) if only one layer involved.",
                        "Map projection conversion is only conducted for spatial data layers such as GeoDataFrame. DataFrame loaded from a CSV file does not have map projection information.",
                        "If join DataFrame and GeoDataFrame, using common columns, DO NOT convert DataFrame to GeoDataFrame.",
                        # "When joining tables, convert the involved columns to string type without leading zeros. ",
                        # "When doing spatial joins, remove the duplicates in the results. Or please think about whether it needs to be removed.",
                        # "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot for better layout.",
                        "Graphs or maps need to show the unit, legend, or colorbar.",
                        "Remember the variable, column, and file names used in ancestor functions when reusing them, such as joining tables or calculating.",
                        # "Show a progressbar (e.g., tqdm in Python) if loop more than 200 times, also add exception handling for loops to make sure the loop can run.",
                        # "When crawl the webpage context to ChatGPT, using Beautifulsoup to crawl the text only, not all the HTML file.",
                        "If using GeoPandas for spatial analysis, when doing overlay analysis, carefully think about use Geopandas.GeoSeries.intersects() or geopandas.sjoin(). ",
                        "Geopandas.GeoSeries.intersects(other, align=True) returns a Series of dtype('bool') with value True for each aligned geometry that intersects other. other:GeoSeries or geometric object. ",
                        "If using GeoPandas for spatial joining, the arguements are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs), how: the type of join, default ‘inner’, means use intersection of keys from both dfs while retain only left_df geometry column. If 'how' is 'left': use keys from left_df; retain only left_df geometry column, and similarly when 'how' is 'right'. ",
                        "Note geopandas.sjoin() returns all joined pairs, i.e., the return could be one-to-many. E.g., the intersection result of a polygon with two points inside it contains two rows; in each row, the polygon attribute is the same. If you need of extract the polygons intersecting with the points, please remember to remove the duplicated rows in the results.",
                        # "GEOID in US Census data and FIPS (or 'fips') in Census boundaries are integer with leading zeros. If use pandas.read_csv() to GEOID or FIPS (or 'fips') columns from read CSV files, set the dtype as 'str'.",
                        # "Drop rows with NaN cells, i.e., df.dropna(), before using Pandas or GeoPandas columns for processing (e.g. join or calculation).",
                        "The program is executable, put it in a function named 'direct_solution()' then run it, but DO NOT use 'if __name__ == '__main__:' statement because this program needs to be executed by exec().",
                        "Before using Pandas or GeoPandas columns for further processing (e.g. join or calculation), drop recoreds with NaN cells in that column, i.e., df.dropna(subset=['XX', 'YY']).",
                        "When read FIPS or GEOID columns from CSV files, read those columns as str or int, never as float.",
                        "FIPS or GEOID columns may be str type with leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12), or integer type without leading zeros. Thus, when joining they, you can convert the integer colum to str type with leading zeros to ensure the success.",
                        "If you need to make a map and the map size is not given, set the map size to 15*10 inches.",
                        ]

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
                        # "When joining tables, convert the involved columns to string type without leading zeros. ",
                        # "If using colorbar for GeoPandas or Matplotlib visualization, set the colorbar's height or length as the same as the plot for better layout.",
                        "When doing spatial joins, remove the duplicates in the results. Or please think about whether it needs to be removed.",
                        "Map grid, legend, or colorbar need to show the unit.",
                        'If a Python package is not installed, add the install command such as "pip" at the beginning of the revised code.',
                        # "Show a progressbar (e.g., tqdm in Python) if loop more than 200 times, also add exception handling for loops to make sure the loop can run.",
                        # "When crawl the webpage context to ChatGPT, using Beautifulsoup to crawl the text only, not all the HTML file.",
                        "If using GeoPandas for spatial analysis, when doing overlay analysis, carefully think about use Geopandas.GeoSeries.intersects() or geopandas.sjoin(). ",
                        "Geopandas.GeoSeries.intersects(other, align=True) returns a Series of dtype('bool') with value True for each aligned geometry that intersects other. other:GeoSeries or geometric object. ",
                        "If using GeoPandas for spatial joining, the arguements are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs), how: the type of join, default ‘inner’, means use intersection of keys from both dfs while retain only left_df geometry column. If 'how' is 'left': use keys from left_df; retain only left_df geometry column, and similarly when 'how' is 'right'. ",
                        "Note geopandas.sjoin() returns all joined pairs, i.e., the return could be one-to-many. E.g., the intersection result of a polygon with two points inside it contains two rows; in each row, the polygon attribute is the same. If you need of extract the polygons intersecting with the points, please remember to remove the duplicated rows in the results.",
                        # "GEOID in US Census data and FIPS (or 'fips') in Census boundaries are integer with leading zeros. If use pandas.read_csv() to GEOID or FIPS (or 'fips') columns from read CSV files, set the dtype as 'str'.",
                         "Before using Pandas or GeoPandas columns for further processing (e.g. join or calculation), drop recoreds with NaN cells in that column, i.e., df.dropna(subset=['XX', 'YY']).",
                        # "Drop rows with NaN cells, i.e., df.dropna(),  if the error information reports NaN related errors."
                        "Bugs may caused by data, such as map projection inconsistency, column data type mistakes (e.g., int, flota, str), spatial joining type (e.g., inner, outer), and NaN cells.",
                        "When read FIPS or GEOID columns from CSV files, read those columns as str or int, never as float.",
                        "FIPS or GEOID columns may be str type with leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12), or integer type without leading zeros. Thus, when joining using they, you can convert the integer colum to str type with leading zeros to ensure the success.",
                        "If you need to make a map and the map size is not given, set the map size to 15*10 inches.",
                        'Save the generated map as the file of "output_map.png"; the DPI is 100.',
                        ]

#--------------- constants for operation review prompt generation  ---------------
operation_review_role =  r'''A professional Geo-information scientist and developer good at Python. You have worked on Geographic information science for more than 20 years and know every detail and pitfall when visualizing spatial data and coding. Your current job is to review other's code, mostly single functions; you are very careful and enjoy code review. You would love to point out the potential bugs of code or data misunderstanding. Your current job is to review the functions for map generation.
'''

operation_review_task_prefix = r"Review a function's code to determine whether it meets its associated requirements. If not, correct it, and then return the completely corrected code."

operation_review_requirement = [
                        'Review the code very carefully to ensure its correctness and robustness.',
                        'Elaborate your reasons for revision before return the revised code.',
                        'If the code has no error, and you do not need to modify the code, DO NOT return code, return "PASS" only, without any other explanation or description.',
                        'If you modified the code, return the complete corrected function. All returned code need to be inside only one Python code block (enclosed by ```python and ```).',
                        'DO NOT use more than one Python code blocks in your reply, because I need to extract the complete Python code in the Python code block.',
                        'Pay extra attention on file name, table field name, spatial analysis parameters, map projections, and NaN cells removal, in the used Pandas columns.',
                        'Pay extra attention on the common field names when joining Pandas DataFrame.',
                        "Map elements such as grid, legend, and colorbar need to show the unit.",
                        # "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot for better layout.",
                        'The given code might has error in mapping or visualization when using GeoPandas or Matplotlib packages.',
                        'Revise the buggy parts, but DO NOT rewrite the entire function, MUST keep the function name, its arguments, and returns.',
                        "Before using Pandas or GeoPandas columns for further processing (e.g. join or calculation), drop recoreds with NaN cells in that column, i.e., df.dropna(subset=['XXX']).",
                        "When read FIPS or GEOID columns from CSV files, read those columns as str or int, never as float.",
                        "FIPS or GEOID columns may be str type with leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12), or integer type without leading zeros. Thus, when joining they, you can convert the integer colum to str type with leading zeros to ensure the success.",
                        "If using GeoPandas for spatial analysis, when doing overlay analysis, carefully think about use Geopandas.GeoSeries.intersects() or geopandas.sjoin(). ",
                        "Geopandas.GeoSeries.intersects(other, align=True) returns a Series of dtype('bool') with value True for each aligned geometry that intersects other. other:GeoSeries or geometric object. ",
                        "Note geopandas.sjoin() returns all joined pairs, i.e., the return could be one-to-many. E.g., the intersection result of a polygon with two points inside it contains two rows; in each row, the polygon attribute is the same. If you need of extract the polygons intersecting with the points, please remember to remove the duplicated rows in the results.",
                        "If the map size is not given, set it to 15*10 inches.",
                        'If the operation is to save a map, save the generated map with the file name as "output_map.png", the DPI is 100.',
                        ]

#--------------- constants for assembly program review prompt generation  ---------------
assembly_review_role =  r'''A professional cartographer and Python developer. You have worked on cartography for more than 20 years and know every detail and pitfall in visualizing spatial data and coding. Your current job is to review others' code, which mostly consists of assembly functions into a complete map-generating program; you are a cautious person and enjoy code review. You would love to point out the potential bugs of code or data misunderstanding.
'''

assembly_review_task_prefix = r"Review a program's code to determine whether it meets its associated requirements. If not, correct it, and then return the completely corrected code. "

assembly_review_requirement = [
                        'Elaborate your reasons for revision at the beginning.',
                        'Review the code very carefully to ensure its correctness and robustness.',                        
                        'If the code has no error, and you do not need to modify the code, DO NOT return code, return "PASS" only, without any other explanation or description.',
                        'If you modified the code, DO NOT reture the revised part only; instead, return the complete corrected program, do not ellipsis any part. All returned code need to be inside only one Python code block (enclosed by ```python and ```). The returned code will directly run in a Python interpreter to obtain the results.',
                        "Map elements such as grid, legend, and colorbar need to show the unit. The unit should be correct.",
                        'DO NOT use more than one Python code blocks in your reply, because I need to extract the complete Python code in the Python code block.',
                        'Pay extra attention on file name, table field name, spatial analysis parameters, map projections, and NaN cells removal in the used Pandas columns.',
                        'Pay extra attention on the common field names when joining Pandas DataFrame.',
                        # "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot for better layout.",
    '                   The given code might has error in mapping or visualization when using GeoPandas or Matplotlib packages.',
                        'Revise the buggy parts, but DO NOT rewrite the entire program or functions, MUST keep the function name, its arguments, and returns.',
                        "If using GeoPandas for spatial analysis, when doing overlay analysis, carefully think about use Geopandas.GeoSeries.intersects() or geopandas.sjoin(). ",
                        "Geopandas.GeoSeries.intersects(other, align=True) returns a Series of dtype('bool') with value True for each aligned geometry that intersects other. other:GeoSeries or geometric object. ",
                        "Note geopandas.sjoin() returns all joined pairs, i.e., the return could be one-to-many. E.g., the intersection result of a polygon with two points inside it contains two rows; in each row, the polygon attribute is the same. If you need of extract the polygons intersecting with the points, please remember to remove the duplicated rows in the results.",
                        #
                        ]

#--------------- constants for direct program review prompt generation  ---------------
direct_review_role = r'''A professional Geo-information scientist and developer good at Python. You have worked on Geographic information science more than 20 years, and know every detail and pitfall when processing spatial data and coding. Yor program is always concise and robust, considering the various data circumstances. You are also super experienced on generating map. Your current job is to review other's code -- mostly assembly functions into a complete programm; you are a very careful person, and enjoy code review. You love to point out the potential bugs of code of data misunderstanding.
'''


direct_review_task_prefix = r'Review the code of a program to determine whether the code meets its associated requirements. If not, correct it then return the complete corrected code. '

direct_review_requirement = [
                        'Review the code very carefully to ensure its correctness and robustness.',
                        'Elaborate your reasons for revision.',
                        "Graphs or maps need to show the unit, legend, or colorbar. The unit should be correct",
                        'If the code has no error, and you do not need to modify the code, DO NOT return code, return "PASS" only, without any other explanation or description.',
                        'If you modified the code, return the complete corrected program. All returned code need to be inside only one Python code block (enclosed by ```python and ```)',
                        'DO NOT use more than one Python code blocks in your reply, because I need to extract the complete Python code in the Python code block.',
                        'Pay extra attention on file name, table field name, spatial analysis parameters, map projections, and NaN cells removal in the used Pandas columns.',
                        'Pay extra attention on the common field names when joining Pandas DataFrame.',
                        'The given code might has error in mapping or visualization when using GeoPandas or Matplotlib packages.',
                        "Before using Pandas or GeoPandas columns for further processing (e.g. join or calculation), drop recoreds with NaN cells in that column, i.e., df.dropna(subset=['XX', 'YY']).",
                        "When read FIPS or GEOID columns from CSV files, read those columns as str or int, never as float.",
                       # "If using colorbar for GeoPandas or Matplotlib visulization, set the colorbar's height or length as the same as the plot for better layout.",
                        "If using GeoPandas for spatial analysis, when doing overlay analysis, carefully think about use Geopandas.GeoSeries.intersects() or geopandas.sjoin(). ",
                        "Geopandas.GeoSeries.intersects(other, align=True) returns a Series of dtype('bool') with value True for each aligned geometry that intersects other. other:GeoSeries or geometric object. ",
                        "Note geopandas.sjoin() returns all joined pairs, i.e., the return could be one-to-many. E.g., the intersection result of a polygon with two points inside it contains two rows; in each row, the polygon attribute is the same. If you need of extract the polygons intersecting with the points, please remember to remove the duplicated rows in the results.",
                        "FIPS or GEOID columns may be str type with leading zeros (digits: state: 2, county: 5, tract: 11, block group: 12), or integer type without leading zeros. Thus, when joining they, you can convert the integer colum to str type with leading zeros to ensure the success.",
                        "If you need to make a map and the map size is not given, set the map size to 15*10 inches.",
                        ]


#--------------- constants for sampling data prompt generation  ---------------
sampling_data_role = r'''A professional Geo-information scientist and developer good at Python. You have worked on Geographic information science more than 20 years, and know every detail and pitfall when processing spatial data and coding. You are also super experienced on spatial data processing. Your current job to help other programmers to understand the data, such as map projection, attributes, and data types.
'''


sampling_task_prefix = r"Given a function, write a program to run this function, then sample the returned data of the function. The program needs to be run by another Python program via exec() function, and the sampled data will be stored in a variable."

sampling_data_requirement = [
                        'Return all sampled data in a string variable named "sampled_data", i.e., sampled_data=given_function().',
                        'The data usually are tables or vectors. You need to sample the top 5 record of the table (e.g., CSV file or vector attritube table) If the data is a vector, return the map projection information.',
                        'The sampled data format is: "Map projection: XXX. Sampled data: XXX',
 
                        #
                        ]


#--------------- constants for map  beautification---------------
beautify_role = r'''A professional cartographer and programmer good at Python. You have worked on cartography more than 20 years, and know every detail and pitfall when visulizing spatial data and coding. You know well how to set up workflows for cartography tasks. You have significant experence on visualizing spatial data and graph theory. You are also experienced on generating map using Matplotlib, GeoPandas and other interative Python packages, such as Plotly. Currently, your job is beautify maps to obtain better overall aesthetic appeal accordings to the given code and the generated map by the code. The purpose of the code is also given. Note the code is generated by AI, so it may be unreasonable.
'''

beautify_task = r'Observe the given map careful using the viewpoint of an experienced cartographer and Python programmer, think about the map design improvements via modifying the code only, and return the modified code. '
 
beautify_requirement = [   
                        'Carefully observe the given map. Think step by step. First, explain the current defects of the map, and the apporaches to improve them; then return the improved Python code.',   
                        'Put your revised code into a single Python code block, enclosed by ```python and ```. Return the entire program, do not ellipsis any part.', 
                        'Do not make up facts that the map does not show.',
                        'A map usualy contains several map elements, such as title, north arrow scalebar, legend, label, and annotation.',
                        "Carefully adjust the location parameters of the map elements accoding to the map appearance.",
                        "If you see the position of the map element is not good, you can adjust its position in the code.",
                        # 'Create an operation node for each map element, you can determine which element is needed according to user input or based on your reasoning.',
                        'The color scheme should consider the harmony, contrast, brightness, warm or cold, and the map theme. You can use the color scheme in Mapplotlib, Tableau, or ggplot2. The colorbar or legend need to use the same color scheme as the map.',
                        'Map elements, such as title, legend, scale bar, should be in a good layout and alignment, considering balance, simplification, borders and margins.',    
                        'The map elements should be in a suitable size, not to big, long, tall, or small.',
                        'Design the suitalbe font and font sizes, considering hierachical levels.',
                        'Make some decorations if necessary.',
                        'Carefully design the symbols of polygons, polylines, and points, consideing background and legibility',
                        'Texts, labels, and annotations cannot overlay to each other.',
                        'If given the audience types, such as adults and kids, you can consider beautify the map accordingly.',
                        'North arrow or compass cannot be split into different locaions, such as top and bottom. Do not put is far away from the map.',
                        'The scale bar needs to long enough. The colorbar needs a length or height close to smaller to map, rather than too long.',
                        "When adding the map grid, colorbar, and scalebar, need to show the unit, such as meter, mile, or km.",
                        'Add the basemap if necessary.',
                        'The map elements are added by individual Python functions respectively. When you revise map elements, you can modify the associated functions.',
                        'The color and symboles in the legend should be associated to the map.',
                        'If the operation is to save a map, save the generated map with the file name as "output_map.png", the DPI is 100.',
                    
                         ]

 
beautify_reply_exmaple = r"""
Current map issues: 
1. The title font size is too small (14 only).
2. The contrast of map color and background color can be more strong.
Improvement:
1. Increase the title font size to 24.
2. Change the map color and background color.
Below are the improved entire program:
```python
import matplotlib.pyplot as plt
...
```
"""

map_review_role = r'''A professional cartographer. You have worked on cartography for more than 20 years and know how to design an aesthetic appeal map. Your current job is to review the map generated by AI. You need to detail the issues with the given map so that the AI can improve the map later. Note that AI makes the map via generated code, so your comments should be suitable for improvements by code. The map requirements are also provided.
'''

map_review_task = r'Observe the given map carefully using the viewpoint of an experienced cartographer.'

map_review_reply_exmaple = r"""
1. The title font size is too small: needs to be enlarged.
2. The contrast between the map color and the background color can be stronger.
...
"""

map_review_requirement = [
                      "Elaborate on the issues, then provide specific and actionable improvements, such as 'move the legend to the up-left to void obscuring'. If you think there is no issue, no need to mention it.",
                      "Whether the map meets cartography requirements for the map.",
                      "Whether there are obstructions between labels, annotations, axis labels, axis ticks, title, legend, scale bar, and other map elements.",
                      "Whether the title semantically meets the data and map requirement.",
                      "Whether the fonts and font sizes are suitable and hierarchical.",
                      "Wheter the map is in the center.",
                      "Whether the legend or colorbar use the same colormap.",
                      "Whether the positions of map elements (e.g., title, north arrow, legend, scale bar) are appropriate, or their sizes are too big or too small.",
                      "Whether the map elements overlay with each other, resulting in something illegible.",
                      "Whether the scale bar is correct and the DPI usually is 100.",
                      "Whether the map elements are too close or too far apart.",
                      "Whether there are redundant map elements, such as two color bars.",
                      "Whether the alignments between the map elements are appropriate; large empty space is not allowed.",
                      "Return your comments one by one without any other explanation. ",
                      "No need to provide comments if there is no issue in an aspect.",
                    
                  ]



#--------------- constants for map  revision ---------------
map_revise_role = r'''A professional cartographer and programmer good at Python. You have worked on cartography more than 20 years, and know every detail and pitfall when visulizing spatial data and coding. You are experenced on visualizing spatial data and graph theory. You are also experienced on generating map using Matplotlib, GeoPandas and other interative Python packages, such as Plotly. Currently, your job is revise maps to obtain better overall aesthetic appeal by modifying the given code--the map is generated by the code. The purpose of the code is also given. Note the code is generated by AI, so it may be unreasonable. A reviewer has pointed out the map issues and provided improving comments. You need to modify the code accordingly.
'''

map_revise_task = r'Observe the given map carefully using the viewpoint of an experienced cartographer and Python programmer, then improve the map design by modifying the code only according to your observation and the given map issues. You need to return the entire program rather than the modified code only.'
 
map_revise_requirements = [   
                        'Carefully observe the given map according to the given issues, then return the improved Python code.',
                        "Propose the detailed and specific solution to a given issue in the point-to-point manner.",
                        "Before return the modified code, explain how to address each issue by modifiying the code, such as increase the font size from 10 to 14.",
                        'Put your revised code into a single Python code block, enclosed by ```python and ```. Return the entire program, do not ellipsis any part.', 
                        'Do not make up facts that the map does not show.',
                        "Carefully adjust the location parameters of the map elements accoding to the map appearance.",
                        "If you see the position of the map element is not appropriate, you can adjust its position in the code.",
                        'Only make necessary revisions to the code. Do not change the structure of the given code or program; keep all functions.',
                        # 'Create an operation node for each map element, you can determine which element is needed according to user input or based on your reasoning.',
                        'The colormap should consider harmony, contrast, brightness, warm or cold, and the map theme. You can use the colormaps in Mapplotlib, Tableau, or ggplot2. The colorbar or legend need to use the same colormap as the map.',
                        'Map elements, such as the title, legend, and scale bar, should have a good layout and alignment, considering balance, simplification, borders and margins.',
                        'The map elements, expecially the colorbar and scalebar, should be in a suitable size, not to big, long, tall, or small.',
                        'Design suitable fonts and font sizes, considering hierarchical levels',
                        'Make some decorations if necessary.',
                        'Carefully design the symbols of polygons, polylines, and points, consideing background and legibility',
                        'Texts, labels, and annotations cannot overlay to each other.',
                        'If given the audience types, such as adults or kids, you can consider beautify the map accordingly.',
                        'The north arrow or compass cannot be split into different locaions, such as top and bottom. Do not put is far away from the map.',
                        'The scale bar needs to long enough. The colorbar needs a length or height close to the map, rather than too long.',
                        "When adding the map grid, colorbar, and scalebar, you need to show the unit, such as meter, mile, or km.",
                        'Add a basemap if necessary.',
                        "The color and symbols in the legend should be associated to the map's colormap.",
                        'If the operation is to save a map, save the generated map with the file name as "output_map.png", the DPI is 100.',
                    
                         ]

 
map_revise_reply_exmaple = r"""
Address the given comments: 
1. The title font size is too small. I will increase the font size from 10 to 14.
2. The contrast between the map and background colors can be stronger. I will use the Matplotlib "viridis" colormap to replace the current "coolwarm" colormap.
```python
import matplotlib.pyplot as plt
...
```
"""