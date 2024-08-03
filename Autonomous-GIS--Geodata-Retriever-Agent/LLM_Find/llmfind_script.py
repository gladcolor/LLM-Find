
import sys

import asyncio
import nest_asyncio
from qgis._core import QgsRasterLayer
from qgis.core import QgsVectorLayer, QgsProject

# # custom_module_dir = r"D:\LLM_Geo_QGIS\LLMQgs"  #REPLACE WITH THE PATH THAT CONTAINS ALL THE MODULES
# custom_module_dir = r"C:\Users\AKINBOYEWA TEMITOPE\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\llmfind"  # REPLACE WITH THE PATH THAT CONTAINS ALL THE MODULES
# if custom_module_dir not in sys.path:
#     sys.path.append(custom_module_dir)

from IPython import get_ipython

# Enable autoreload
ipython = get_ipython()
if ipython:
    ipython.run_line_magic('load_ext', 'autoreload')
    ipython.run_line_magic('autoreload', '2')

import os
import rasterio
from PIL import Image

import requests
import networkx as nx
import pandas as pd
import geopandas as gpd
# from pyvis.network import Network
from openai import OpenAI
from IPython.display import display, HTML, Code
from IPython.display import clear_output
import matplotlib.pyplot as plt

import base64

import pickle
import sys
import osmnx as ox

import os
import sys

# Get the directory of the current script
current_script_dir = os.path.dirname(os.path.abspath(__file__))
llm_find_dir = os.path.join(current_script_dir, 'LLM_Find')

# Add the directory to sys.path
if current_script_dir not in sys.path:
    sys.path.append(llm_find_dir)

# Now you can import the module
import LLM_Find_Constants as constants
import LLM_Find_helper as helper


import numpy as np
# from LLM_Find_kernel import Solution

from langchain_openai import ChatOpenAI

# from langchain_core.prompts import ChatPromptTemplate

# OpenAI_key = helper.load_OpenAI_key()

# ---- Data source 1:  OpenStreetMap  -----------------

# # task_name ='China_mainland_province_boundary'  # most test failed! solved.
# downloaded_file_name = 'China_mainland_Province_boundary'
# saved_fname = f"D:\LLMFIND\Downloaded Data\{downloaded_file_name}.gpkg"
# task = rf'''1. Download all province boundaries of China mainland.
# 2. Save the downloaded data as polygons in GeoPackage format at: {saved_fname}
# '''

# task_name ='OSM_PA_boundary'
# downloaded_file_name = 'PA_boundary'
# # saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# saved_fname = rf"D:\LLMFIND\Downloaded Data\{downloaded_file_name}.gpkg"
# task = rf'''1. Download the administrative boundary of Pennsylvania State, USA.
# 2. Save the downloaded data in GeoPackage format, save it at: {saved_fname}
#  '''


# # task_name ='OSM_PA_hospital'
# downloaded_file_name = r'PA_hospital.gpkg'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download all hospitals in Pennsylvania State, USA.
# 2. Save the downloaded data as points in GeoPackage format at: {saved_fname}
# '''

#------------------------------## Data source 2:  US Census Bureau administrative boundary

# # task_name ='Census_SC_tract'
# downloaded_file_name = r'Census_SC_tract.gpkg'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download all census tract boundaries in South Carolina, USA.
# 2. Save the downloaded data as polygons in GeoPackage format, save it at: {saved_fname}
# '''


# task_name ='Census_SC_blockgroups'
# downloaded_file_name = r'Census_SC_blockgroups22.gpkg'
# #saved_fname = r'E:\OneDrive_PSU\OneDrive - The Pennsylvania State University\Research_doc\LLM-Find\Downloaded_Data\Census_SC_blockgroups.gpkg'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# if os.path.exists(saved_fname):
#     os.remove(saved_fname)
# task = rf'''1. Download all Census block group boundaries in South Carolina, USA.
# 2. Save the downloaded data as polygons in GeoPackage format, save it at: {saved_fname}
# '''

#__________________________________Data source 3:  US Census Bureau demographic variables____#API KEY NEEDED_____________________________________________________
# task_name ='Census_SC_counties_population'
# # saved_fname = r'E:\OneDrive_PSU\OneDrive - The Pennsylvania State University\Research_doc\LLM-Find\Downloaded_Data\Census_SC_counties_population.csv'
# downloaded_file_name = r'Census_SC_counties_population.csv'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download latest population for each county in South Carolina.
# 2. Save the downloaded data as CSV files, save it at: {saved_fname}
# '''

# task_name ='Census_SC_Richland_race_population'
# saved_fname = r'E:\OneDrive_PSU\OneDrive - The Pennsylvania State University\Research_doc\LLM-Find\Downloaded_Data\Census_SC_Richland_race_population.csv'
# downloaded_file_name = r"Census_SC_Richland_race_population.csv"
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download latest population of each race for Richland county in South Carolina, at Census block group level.
# 2. Save the downloaded data as CSV files, save it at: {saved_fname}
# '''

#_______________________________________Data source 4:  COVID-19 accumulative cases by New York Times____________________________________________________
# task_name ='COVID_Richland_SC'
# downloaded_file_name = r'COVID_Richland_SC2.csv'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download the COVID-19 case data of Richland County in South Carolina, USA. The time is from 2021-01 to 2021-09.
# 2. Save the downloaded data as a CSV file at: {saved_fname}
# '''

#______________________________________Data source 5: Weather data ________#API Key needed____________________________________________
# # task_name ='OpenWeather_Columbia'
# downloaded_file_name = r'OpenWeather_Columbia.csv'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download the historical weather data of Columbia, South Carolina in May 2024.
# 2. Save the downloaded data in CSV format, save it at: {saved_fname}
# '''

#________________________________Data source 6:  Satellite image (ESRI World Imagery (for export))_____________________________

# task_name ='FAST_Telescope'
# downloaded_file_name = r'FAST_Telescope_image2.tif'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download the FAST Telescope (Guizhou, China) satellite image at level 18.
# 2. Save the downloaded data in tiff format, save it at: {saved_fname}
# '''

# task_name ='Nigeria_image'
# downloaded_file_name = r'Nigeria_image.tif'
# saved_fname = os.path.join(os.getcwd(), "Downloaded_Data", downloaded_file_name)
# task = rf'''1. Download the Nigeria satellite image at level 7.
# 2. Save the downloaded data in tiff format, save it at: {saved_fname}
# '''


def main(task, saved_fname, model_name):
    filename_only = os.path.basename(saved_fname)
    # Convert the data locations string back to a list if needed
    #saved_fname = saved_fname.split(';')  # Assuming data locations are joined by a semicolon
    #task_name = task_name
    #task = task
    return filename_only



if __name__ == "__main__":

    task = sys.argv[1]
    saved_fname = sys.argv[2]
    model_name = sys.argv[3]
    main(task, saved_fname, model_name)
downloaded_file_name = main(task, saved_fname, model_name)

if os.path.exists(saved_fname):
    os.remove(saved_fname)

save_dir = os.path.join(os.getcwd(), "Downloaded_Data")
os.makedirs(save_dir, exist_ok=True)

# model_name = r'gpt-4o'


OpenAI_key = helper.load_OpenAI_key()

model = ChatOpenAI(api_key=OpenAI_key, model=model_name, temperature=1)

source_select_prompt_str = helper.create_select_prompt(task=task)

print(source_select_prompt_str)

from IPython.display import clear_output


async def fetch_chunks(model, source_select_prompt_str):
    chunks = []
    async for chunk in model.astream(source_select_prompt_str):
        chunks.append(chunk)
        # print(chunk.content, end="", flush=True)
    return chunks


nest_asyncio.apply()
chunks = asyncio.run(fetch_chunks(model, source_select_prompt_str))

clear_output(wait=True)
# clear_output(wait=False)
LLM_reply_str = helper.convert_chunks_to_str(chunks=chunks)

print("Select the data source: \n")
print(LLM_reply_str)

import ast
select_source = ast.literal_eval(LLM_reply_str)

selected_data_source = select_source['Selected data source']
data_source_ID = constants.data_source_dict[selected_data_source]['ID']

print("selected_data_source:", selected_data_source)
print("data_source_ID:", data_source_ID)

handbook_list = constants.handbooks[f"{data_source_ID}"]
handbook_str =  '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(handbook_list)])
print()
print(f"Handbook:\n{handbook_str}")


download_prompt_str = helper.create_download_prompt(task,saved_fname, selected_data_source, handbook_str)
print(download_prompt_str)


from IPython.display import clear_output
async def fetch_download_str(model, download_prompt_str):
    chunks = []

    async for chunk in model.astream(download_prompt_str):
        chunks.append(chunk)
        # print(chunk.content, end="", flush=True)
    return chunks
nest_asyncio.apply()
chunks = asyncio.run(fetch_chunks(model, download_prompt_str))

clear_output(wait=True)
# clear_output(wait=False)
LLM_reply_str = helper.convert_chunks_to_str(chunks=chunks)
print(LLM_reply_str)


code = helper.extract_code_from_str(LLM_reply_str, task)
display(Code(code, language='python'))


code = helper.execute_complete_program(code=code, try_cnt=10, task=task, model_name=model_name, handbook_str=handbook_str)
display(Code(code, language='python'))



if saved_fname.endswith('.gpkg') or saved_fname.endswith('.csv') or saved_fname.endswith('.shp'):
    layer = QgsVectorLayer(saved_fname, f"{downloaded_file_name}", "ogr")
    QgsProject.instance().addMapLayer(layer)
    print("vector data loaded")
elif saved_fname.endswith('.tif'):
    layer =QgsRasterLayer(saved_fname,f"{downloaded_file_name}")
    QgsProject.instance().addMapLayer(layer)
    print("Raster data loaded")

else:
    print("Unsupported file format")



print("SAVED FNAME: ",saved_fname)
# print("Layer path: ",layer_path)
