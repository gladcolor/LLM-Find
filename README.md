# An autonomous GIS agent framework for geospatial data retrieval

Powered by the emerging large language models (LLMs), autonomous geographic information systems (GIS) agents have the potential to accomplish spatial analyses and cartographic tasks. However, a research gap exists to support fully autonomous GIS agents: how to enable agents to discover and download the necessary data for geospatial analyses. This study proposes an autonomous GIS agent framework capable of retrieving required geospatial data by generating, executing, and debugging programs. The framework utilizes the LLM as the decision-maker, selects the appropriate data source (s) from a pre-defined source list, and fetches the data from the chosen source. Each data source has a handbook that records the metadata and technical details for data retrieval. The proposed framework is designed in a plug-and-play style to ensure flexibility and extensibility. Human users or autonomous data scrawlers can add new data sources by adding new handbooks. We developed a prototype agent based on the framework, which was released as a QGIS plugin (GeoData Retrieve Agent) and a Python program. Experiment results demonstrate its capability of retrieving data from various sources, including OpenStreetMap, administrative boundaries and demographic data from the US Census Bureau, satellite basemaps from ESRI World Imagery, global digital elevation model (DEM) from OpenTotography, weather data from a commercial provider, the COVID-19 cases from the NYTimes GitHub. Our study is among the first attempts to develop an autonomous geospatial data retrieval agent.

We tested various data cases; by accepting data requests in natural language, most of the requests got correct data with an about 80% - 90% success rate. We feel excited about that because the success of such data fetching agents indicates that the data-intensive GIS research or border scientific research can be executed by agents. Autonomous research agents can collect necessary online or local data and then conduct analysis parallelly while adjusting methods or strategies for better results. LLM-Find will play a foundational role in such a bright vision. 

QGIS users can download the QGIS plugin (AutonomousGIS-GeodataRetrieveAgent) to download the data via natural language in a GIS environment. Note that for some data sources, you may need to apply API keys. The source code of the QGIS plugin is [here](https://github.com/Teakinboyewa/AutonomousGIS_GeodataRetrieverAgent). QGIS Plugin page: https://plugins.qgis.org/plugins/AutonomousGIS_GeodataRetrieverAgent/

Please watch demonstrations on our [YouTubeChannel](https://www.youtube.com/watch?v=4otpdHUlpwE&list=PL6ON3gdLloDE9NynwhMxYNDoFukbNJnf1). 
 
For more details, please refer to our paper: Ning, Huan, Zhenlong Li, Temitope Akinboyewa, and M. Naser Lessani. 2024. “LLM-Find: An Autonomous GIS Agent Framework for Geospatial Data Retrieval.” arXiv. https://doi.org/10.48550/arXiv.2407.21024.


Further reading: [Autonomous GIS: the next-generation AI-powered GIS](https://www.tandfonline.com/doi/full/10.1080/17538947.2023.2278895). Recommended citation format: Li Z., Ning H., 2023. Autonomous GIS: the next-generation AI-powered GIS. International Journal of Digital Earth. https://doi.org/10.1080/17538947.2023.2278895. GitHub repository: github.com/gladcolor/LLM-Geo

Note:  LLM-Find is under active development, and the ideas presented in the paper may change due to the rapid development of AI. We hope LLM-Find can inspire the geospatial community to investigate autonomous GIS further.    

![img.png](images/framework.png)

LLM-Find framework



![img.png](images/agent_workflow.png)

LLM-Find Agent workflow

# Installation

- Clone or download the repository, rename `your_config.ini` to `config.ini` in the `Keys` directory, and put your OpenAI API key in the `config.ini` file. Please use GPT-4o; the lower versions may not be able to generate the correct code.
- Install the Python packages in the top cell.
- If you need to download data from [OpenWeather](https://openweathermap.org/api), [US Census](https://api.census.gov/data/key_signup.html), and [OpenTopography](https://opentopography.org/developers), please apply their API keys and put them in their associated `*.keys` file in the `Keys` directory. Remove `YOUR_` in the `*.keys` file names.
- If you need to use your own data source, please edit a `handbook` following the format in the `Handbook` directory.


- If you have difficulties installing `GeoPandas` in Windows, refer to this [post](https://geoffboeing.com/2014/09/using-geopandas-windows/). 


# How to use
- Set the `downloaded_file_name` in LLM-Find.ipynb; the extension is needed, and space is not allowed. LLM-Find will save the downloaded data in this file.
- Put your data request to the `task` variable.
- Run all cells.
- LLM-Find will use the backed LLM (GPT-4o now) to generate and debug the data fetching program. GPT-4o's debugging ability is still weak. The default maximum attempt count is set to 10; modify this value is needed. 
- Tip 1: we suggest you re-run the program if LLM-Find cannot write the bug-free code. Per our observation, GPT sometimes will keep writing wrong code in a period about 10 minutes. Seems GPT will cache some previous answers so that it keeps return the same or similar wrong code.


# Case studies
Please try out the [provided cases (~70)](https://github.com/gladcolor/LLM-Find/blob/master/LLM_Find.ipynb); we also encourage you to use your own cases. These case studies are designed to show the concepts of autonomous data fetching agents. Please use GPT-4o or above; the lower version of GPT will fail to generate the correct code and results. Note every time GPT-4o generates different outputs, your results may look different. Per our test, the generated program may fail at a chance of about 10%; if so, please re-run all the cells again. You don't need to manually debug the code unless you'd like to. 

When fetching OpenStreetMap data and images, for those places that do not use the English language, we encourage you to input the names written in the local language. Such two data sources are more friendly and correct with the native language names than the English names. For example, when retrieving Chinese places, use the Chinese language rather than Pinyin since there are many of the same Pinyin for different characters. Similarly, there are many places that have the same name, such as "Columbia" in the USA. Therefore, please ensure your input place name is correct. You can use nominatim.openstreetmap.org to determine the correct name in OpenStreetMap. 

![img.png](images/FAST.png)

The LLM-Find agent downloaded a satellite image of the FAST Telescope from ESRI World Imagery. (Note: This feature has been removed from OpenStreetMap on Aug. 29, 2024: https://www.openstreetmap.org/way/384699313. Do not test this case for now.)

![img_2.png](images/weather.png)

The LLM-Find agent downloaded a 16-day daily weather forecast for Kabul, Afghanistan.


![img.png](Nigeria.png)
 The [The QGIS plugin of the GeoData Retrieve Agent](https://github.com/Teakinboyewa/AutonomousGIS_GeodataRetrieverAgent)) and the downloaded geospatial data of Nigeria, including cities (point), rivers (polyline), and state boundaries (polygon) from OpenStreetMap. The image basemap was downloaded from ESRI World Imagery using the plugin. Note that there are four individual data requests to retrieve the shown data (e.g., “Download the rivers in Nigeria.”) 

# To Do
- Develop a data assessment module.
- Issue 1: We observed that GPT cannot correct the contaminated information even adding instructions in the prompt. E.g., it has about 50% chance to ignore the instruction of "using `relation(osm_id)` rather than `area(osm_id)`". Thus, we have to replace the string using Python code.
- Adding current time to the prompt.


# Note:

- You may need [OSMnx](https://osmnx.readthedocs.io/en/stable/) and [geopandas](https://geopandas.org/en/stable/getting_started.html#installation) packages to download and read vector files. Please install it in advance.
  
# Change log
- 2025-04-25, a guideline in the Handbook for Census Bureau boundary needs to be updated: If using GeoPandas to load a zipped ESRI shapefile from a URL, do not use `gpd.read_file(URL)` because the Census Bureau has prohibited it. Download the zip file and use `gpd.read_file(zipfile)`.


