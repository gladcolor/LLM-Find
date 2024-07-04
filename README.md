# LLM-Find: an autonomous agent framework for geospatial data fetching

Geographic information system (GIS) users and analyst need to fetching geospatial data for analysis or research tasks. Data fetching can be time-consuming and label intensive. Is it possible to fetching with less pain and time? This study tried to create an autonomous fetching agent for GIS analysts and then make them more focus on their creative work.

This study proposes LLM-Find, an autonomous agent framework to select geospatial data and then fetch data by generating and executing programs with self-debugging. LLM-Find adopts an LLM as the decision maker to pick up the applicable data source from a list and then fetch data from the selected source. Each data source has a pre-defined handbook that records the metadata and technical details for data fetching. The proposed framework is flexible and extensible, designed as a plug-and-play mechanism; human users or autonomous data scrawlers can add a new data source by adding a new handbook. LLM-Find provides a fundamental agent framework for data fetching in autonomous GIS. We also prototyped an agent based on LLM-Find, which can fetch data from OpenStreetMap, COVID-19 cumulative cases from GitHub, administrative boundaries and demographic data from the US Census Bureau, weather data from a commercial provider, and satellite basemap from ESRI World Imagery.

We tested various data cases; by accepting data requests in natural language, most of the requests got correct data in an about 80% success rate. We feel excited about that because the success of such data fetching  agent indicates that the data intensive GIS research or boarder scientific research can be executed by agents. Autonomous research agents can collect necessary online or local data and then conduce analysis parallely while adjust methods or strategies for better results. LLM-Find will be a foundational role in such a bright vision. 
 

Reference: [Autonomous GIS: the next-generation AI-powered GIS](https://www.tandfonline.com/doi/full/10.1080/17538947.2023.2278895). Recommended citation format: Li Z., Ning H., 2023. Autonomous GIS: the next-generation AI-powered GIS. Interntional Journal of Digital Earth. https://doi.org/10.1080/17538947.2023.2278895. GitHub repository: github.com/gladcolor/LLM-Geo

Note:  We are still developing LLM-Find, and the ideas presented in the paper may change due to the rapid development of AI. We hope LLM-Find can inspire GIScience professionals to further investigate on autonomous GIS.    


# Installation

- Clone or download the repository, rename `your_config.ini` as `config.ini`. Then, put your OpenAI API key and other keys in the `config.ini` file. Please use GPT-4o, the lower versions may not have enough  ability to generate correct code.
- Install the Python packages in the top cell.

- If you have difficulties installing `GeoPandas` in Windows, refer to this [post](https://geoffboeing.com/2014/09/using-geopandas-windows/). 


# How to use
- Set the `downloaded_file_name` in LLM-Find.ipynb; extention is needed, space is not allowed. LLM-Find will save the downloaded data at this file.
- Put your data request to the `task` variable.
- Run all cells.
- LLM-Find will use the backed LLM (GPT-4o now) to generate and debug the data fetching program. GPT-4o's debugging ability is still weak. The default maximum attempt count is set to 10; modify this value is needed. 

# Case studies
Please play with the provided cases (~60), we also encourage you use your own cases. These case studies are designed to show the concepts of autonomous data fetching agents. Please use GPT-4o or above; the lower version of GPT will fail to generate the correct code and results. Note every time GPT-4o generates different outputs, your results may look different. Per our test, the generated program may not succeed at a chance about 10%; if so, please re-run all the cells again; no need to manually debug the code unless you like to do so. 


# To Do
- Needs a data assessment module.

# Note:

- You may need [OSMnx](https://osmnx.readthedocs.io/en/stable/) and [geopandas](https://geopandas.org/en/stable/getting_started.html#installation) packages to download and read vector files. Please install it in advance.
