import re
import sys
import traceback
# import openai
from collections import deque
from openai import OpenAI

import configparser

# import networkx as nx
import logging
import time

import os
import requests
import networkx as nx
import pandas as pd
import geopandas as gpd
from pyvis.network import Network
 

import LLM_Find_Constants as constants
from langchain_core.prompts import ChatPromptTemplate


#load config
config = configparser.ConfigParser()
config.read('config.ini')

# use your KEY.
OpenAI_key = config.get('API_Key', 'OpenAI_key')
client = OpenAI(api_key=OpenAI_key)

def load_OpenAI_key():
    OpenAI_key = config.get('API_Key', 'OpenAI_key')
    return OpenAI_key

def create_select_prompt(task):
    select_requirement_str = '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(constants.select_requirements)])

    prompt =  f"Your role: {constants.select_role} \n" + \
              f"Your mission: {constants.select_task_prefix}: " + f"{task}\n\n" + \
              f"Requirements: \n{select_requirement_str} \n\n" + \
              f"Data sources:{constants.data_sources} \n" + \
              f'Your reply example: {constants.selection_reply_example}'

    # print(prompt)

    # The template seems cannot have the "{}", otherwise LangChain may confuse with its variable using "{}" as the tag.

#     prompt_langChain = ChatPromptTemplate.from_messages([
#     ("system", constants.select_role),
#     ("human", prompt)
# ])
    
    return prompt

def convert_chunks_to_str(chunks):
    LLM_reply_str = ""
    for c in chunks:
        # print(c)
        LLM_reply_str += c.content # c['content']
    return LLM_reply_str




def create_download_prompt(task, selected_data_source, handbook_str):
    # select_requirement_str = '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(constants.select_requirements)])

    prompt =  f"Your role: {constants.download_role} \n" + \
              f"Your mission: {constants.download_task_prefix}: " + f"{task}\n\n" + \
              f"Data source:{selected_data_source} \n" + \
              f"Handbook: \n{handbook_str} \n\n" + \
              f'Your reply example: {constants.download_reply_example}'

    
    return prompt 

def get_LLM_reply_LC(
            prompt,
            model,
            verbose=True,
            temperature=1,
            stream=True,
            retry_cnt=3,
            sleep_sec=10,
            system_role="",
            ):   
    """
    Get LLM reply using LangChain. "LC" means LangChain.
    """
 
    # Query ChatGPT with the prompt
    # if verbose:
    #     print("Geting LLM reply... \n")
    count = 0
    isSucceed = False
    while (not isSucceed) and (count < retry_cnt):
        try:
            count += 1
            # For OpenAI
            if model.dict()["_type"] == "openai-chat":  
                response = client.chat.completions.create(model=model,
                # messages=self.chat_history,  # Too many tokens to run.
                messages=[
                            {"role": "system", "content": system_role},
                            {"role": "user", "content": prompt},
                          ],
                temperature=temperature,
                stream=stream)
        except Exception as e:
            # logging.error(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            print(f"Error in get_LLM_reply_LC(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n",
                  e)
            time.sleep(sleep_sec)

    ## Do not know how to process returns of non-OpenAI 
    response_chucks = []
    if stream:
        for chunk in response:
            response_chucks.append(chunk)
            content = chunk.choices[0].delta.content
            if content is not None:
                if verbose:
                    print(content, end='')
    else:
        content = response.choices[0].message.content
        # print(content)
    print('\n\n')
    # print("Got LLM reply.")

    response = response_chucks  # good for saving

    content = helper.extract_content_from_LLM_reply(response)

    # self.chat_history.append({'role': 'assistant', 'content': content})

    return response

def extract_content_from_LLM_reply(response):
    stream = False
    if isinstance(response, list):
        stream = True
        
    content = ""
    if stream:       
        for chunk in response:
            chunk_content = chunk.choices[0].delta.content         

            if chunk_content is not None:
                # print(chunk_content, end='')
                content += chunk_content
                # print(content)
        # print()
    else:
        content = response.choices[0].message.content
        # print(content)
        
    return content


def extract_code(response, verbose=False):
    '''
    Extract python code from reply
    '''
    # if isinstance(response, list):  # use OpenAI stream mode.
    #     reply_content = ""
    #     for chunk in response:
    #         chunk_content = chunk["choices"][0].get("delta", {}).get("content")
    #
    #         if chunk_content is not None:
    #             print(chunk_content, end='')
    #             reply_content += chunk_content
    #             # print(content)
    # else:  # Not stream:
    #     reply_content = response["choices"][0]['message']["content"]

    python_code = ""
    reply_content = extract_content_from_LLM_reply(response)
    python_code_match = re.search(r"```(?:python)?(.*?)```", reply_content, re.DOTALL)
    if python_code_match:
        python_code = python_code_match.group(1).strip()

    if verbose:
        print(python_code)
    
    return python_code


def extract_code_from_str(LLM_reply_str, verbose=False):
    '''
    Extract python code from reply string, not 'response'.
    '''
 
    python_code = ""
    python_code_match = re.search(r"```(?:python)?(.*?)```", LLM_reply_str, re.DOTALL)
    if python_code_match:
        python_code = python_code_match.group(1).strip()

    if verbose:
        print(python_code)
    
    return python_code


def execute_complete_program(code: str, try_cnt: int = 10) -> str:
    

    count = 0
    while count < try_cnt:
        print(f"\n\n-------------- Running code (trial # {count + 1}/{try_cnt}) --------------\n\n")
        try:
            count += 1
            compiled_code = compile(code, 'Data downloading program', 'exec')
            exec(compiled_code, globals())  # #pass only globals() not locals()
            #!!!!    all variables in code will become global variables! May cause huge issues!     !!!!
            print("\n\n--------------- Done ---------------\n\n")
            return code

        # except SyntaxError as err:
        #     error_class = err.__class__.__name__
        #     detail = err.args[0]
        #     line_number = err.lineno
        #
        except Exception as err:

            # cl, exc, tb = sys.exc_info()

            # print("An error occurred: ", traceback.extract_tb(tb))

            if count == try_cnt:
                print(f"Failed to execute and debug the code within {try_cnt} times.")
                return code

            debug_prompt = get_debug_prompt(exception=err, code=code)
            print("Sending error information to LLM for debugging...")
            # print("Prompt:\n", debug_prompt)
            response = get_LLM_reply(prompt=debug_prompt,
                                            system_role=constants.debug_role,
                                            model=model_name,
                                            verbose=True,
                                            stream=True,
                                            retry_cnt=5,
                                            )
            code = extract_code(response)

    return code


def get_debug_prompt(exception, code):
        etype, exc, tb = sys.exc_info()
        exttb = traceback.extract_tb(tb)  # Do not quite understand this part.
        # https://stackoverflow.com/questions/39625465/how-do-i-retain-source-lines-in-tracebacks-when-running-dynamically-compiled-cod/39626362#39626362

        ## Fill the missing data:
        exttb2 = [(fn, lnnr, funcname,
                   (code.splitlines()[lnnr - 1] if fn == 'Data downloading program'
                    else line))
                  for fn, lnnr, funcname, line in exttb]

        # Print:
        error_info_str = 'Traceback (most recent call last):\n'
        for line in traceback.format_list(exttb2[1:]):
            error_info_str += line
        for line in traceback.format_exception_only(etype, exc):
            error_info_str += line

        print(f"Error_info_str: \n{error_info_str}")

        # print(f"traceback.format_exc():\n{traceback.format_exc()}")

        debug_requirement_str = '\n'.join([f"{idx + 1}. {line}" for idx, line in enumerate(constants.debug_requirement)])

        debug_prompt = f"Your role: {constants.debug_role} \n" + \
                          f"Your task: correct the code of a program according to the error information, then return the corrected and completed program. \n\n" + \
                          f"Requirement: \n {debug_requirement_str} \n\n" + \
                          f"The given code is used for this task: {task} \n\n" + \
                          f"The error information for the code is: \n{str(error_info_str)} \n\n" + \
                          f"The code is: \n{code}"

        return debug_prompt
    
def get_LLM_reply(prompt="Provide Python code to read a CSV file from this URL and store the content in a variable. ",
                  system_role=r'You are a professional Geo-information scientist and developer.',
                  model=r"gpt-3.5-turbo",
                  verbose=True,
                  temperature=1,
                  stream=True,
                  retry_cnt=3,
                  sleep_sec=10,
                  ):

    # Generate prompt for ChatGPT
    # url = "https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv"
    # prompt = prompt + url

    # Query ChatGPT with the prompt
    # if verbose:
    #     print("Geting LLM reply... \n")
    count = 0
    isSucceed = False
    while (not isSucceed) and (count < retry_cnt):
        try:
            count += 1
            response = client.chat.completions.create(model=model,
            messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            stream=stream)
        except Exception as e:
            # logging.error(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            print(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            time.sleep(sleep_sec)


    response_chucks = []
    if stream:
        for chunk in response:
            response_chucks.append(chunk)
            content = chunk.choices[0].delta.content
            if content is not None:
                if verbose:
                    print(content, end='')
    else:
        content = response.choices[0].message.content
        # print(content)
    print('\n\n')
    # print("Got LLM reply.")
        
    response = response_chucks # good for saving
    
    return response
    

def get_LLM_reply_v0(prompt="Provide Python code to read a CSV file from this URL and store the content in a variable. ",
                  system_role=r'You are a professional Geo-information scientist and developer.',
                  model=r"gpt-3.5-turbo",
                  verbose=True,
                  temperature=1,
                  stream=True,
                  retry_cnt=3,
                  sleep_sec=10,
                  ):

    # Generate prompt for ChatGPT
    # url = "https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv"
    # prompt = prompt + url

    # Query ChatGPT with the prompt
    # if verbose:
    #     print("Geting LLM reply... \n")
    count = 0
    isSucceed = False
    while (not isSucceed) and (count < retry_cnt):
        try:
            count += 1
            response = client.chat.completions.create(model=model,
            messages=[
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            stream=stream)
        except Exception as e:
            # logging.error(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            print(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            time.sleep(sleep_sec)


    response_chucks = []
    if stream:
        for chunk in response:
            response_chucks.append(chunk)
            content = chunk.choices[0].delta.content
            if content is not None:
                if verbose:
                    print(content, end='')
    else:
        content = response.choices[0].message.content
        # print(content)
    print('\n\n')
    # print("Got LLM reply.")
        
    response = response_chucks # good for saving
    
    return response

def get_LLM_vision_reply(prompt="Provide Python code to read a CSV file from this URL and store the content in a variable. ",
                  system_role=r'You are a professional Geo-information scientist and developer.',
                  model=r"gpt-3.5-turbo",
                  img_base64="",
                  verbose=True,
                  temperature=1,
                  stream=True,
                  retry_cnt=3,
                  sleep_sec=10,
                  ):

    # Generate prompt for ChatGPT
    # url = "https://github.com/gladcolor/LLM-Geo/raw/master/overlay_analysis/NC_tract_population.csv"
    # prompt = prompt + url

    # Query ChatGPT with the prompt
    # if verbose:
    #     print("Geting LLM reply... \n")
    count = 0
    isSucceed = False
    while (not isSucceed) and (count < retry_cnt):
        try:
            count += 1
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system", "content": system_role
                    },

                   {
                        "role": "user", 
                         "content": [
                            {
                                "type": "text", "text": prompt
                            },
                            {
                                "type": "image_url", 
                                "image_url": {
                                    "url": f"data:image/jpeg;base64, {img_base64}",
                                    # "detail": "high"
                                 } # This closing brace matches the "image_url" dictionary
                            }
                         ],

                   },  
               ],
                temperature=temperature,
                stream=stream
             )
             
        except Exception as e:
            # logging.error(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            print(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n", e)
            time.sleep(sleep_sec)
            
    response_chucks = []
    # response_chucks = ""
    if stream:
        for chunk in response:
            response_chucks.append(chunk)
            content = chunk.choices[0].delta.content
            if content is not None:
                # response_chucks += str(content)
                if verbose:
                    print(content, end='')
                     
           
    else:
        content = response.choices[0].message.content
        # response_chucks += content
        # print(content)
    print('\n\n')
    # print("Got LLM reply.")
     
        
    # response = response_chucks # good for saving
    
    return response_chucks


 
def has_disconnected_components(directed_graph, verbose=True):
    # Get the weakly connected components
    weakly_connected = list(nx.weakly_connected_components(directed_graph))

    # Check if there is more than one weakly connected component
    if len(weakly_connected) > 1:
        if verbose:
            print("component count:", len(weakly_connected)) 
        return True
    else:
        return False
    
def generate_function_def(node_name, G):
    '''
    Return a dict, includes two lines: the function definition and return line.
    parameters: operation_node
    '''
    node_dict = G.nodes[node_name]
    node_type = node_dict['node_type']
    
    predecessors = G.predecessors(node_name)
     
    # print("predecessors:", list(predecessors))
    
    # create parameter list with default values
    para_default_str = ''   # for the parameters with the file path
    para_str = ''  # for the parameters without the file path
    for para_name in predecessors:        
        # print("para_name:", para_name)
        para_node = G.nodes[para_name]
        # print(f"para_node: {para_node}")
        # print(para_node)
        data_path = para_node.get('data_path', '')  # if there is a path, the function need to read this file
        
        if data_path != "":            
            para_default_str = para_default_str + f"{para_name}='{data_path}', "
        else:
            para_str = para_str + f"{para_name}={para_name}, "
        
    all_para_str = para_str + para_default_str
    
    function_def = f'{node_name}({all_para_str})'
    function_def = function_def.replace(', )', ')')  # remove the last ","
    
    # generate the return line
    successors = G.successors(node_name) 
    return_str = 'return ' + ', '.join(list(successors))

    
    # print("function_def:", function_def)  # , f"node_type:{node_type}"
    # print("return_str:", return_str)  # , f"node_type:{node_type}"
    # print(function_def, predecessors, successors)
    return_dict = {"function_definition": function_def, 
                   "return_line":return_str, 
                   'description': node_dict['description'], 
                   'node_name': node_name
                  }
    return return_dict

def bfs_traversal(graph, start_nodes):
    visited = set()
    queue = deque(start_nodes)

    order = []
    while queue:
        node = queue.popleft()
        # print(node)
        if node not in visited:
            order.append(node)
            visited.add(node)
            queue.extend(neighbor for neighbor in graph[node] if neighbor not in visited)
    return order


def generate_function_def_list(G):
    '''
    Return a list, each string is the function definition and return line
    '''
    # start with the data loading, following the data flow.
    nodes = []
    # Find nodes without predecessors
    nodes_without_predecessors = [node for node in G.nodes() if G.in_degree(node) == 0]
    # print(nodes_without_predecessors)
    # Traverse the graph using BFS starting from the nodes without predecessors
    traversal_order = bfs_traversal(G, nodes_without_predecessors)
    
    # print("traversal_order:", traversal_order)
    
    def_list = []
    data_node_list = []
    for node_name in traversal_order:
        node_type = G.nodes[node_name]['node_type']
        if node_type == 'operation':    
            # print(node_name, node_type)
            # predecessors = G.predecessors('Load_shapefile')
            # successors = G.successors('Load_shapefile') 

            function_def_returns = generate_function_def(node_name, G)
            def_list.append(function_def_returns)
            
        if node_type == 'data':
            data_node_list.append(node_name)

    return def_list, data_node_list

def get_given_data_nodes(G):
    given_data_nodes = []
    for node_name in G.nodes():
        node = G.nodes[node_name]
        in_degrees = G.in_degree(node_name)
        if in_degrees == 0:
            given_data_nodes.append(node_name)
            # print(node_name,in_degrees,  node)
    return given_data_nodes


def get_data_loading_nodes(G):
    data_loading_nodes = set()
    
    given_data_nodes = get_given_data_nodes(G)
    for node_name in given_data_nodes:
         
        successors = G.successors(node_name) 
        for node in successors:
            data_loading_nodes.add(node)
            # print(node_name,in_degrees,  node)
    data_loading_nodes = list(data_loading_nodes)
    return data_loading_nodes


def get_data_sample_text(file_path, file_type="csv", encoding="utf-8"): 
    """
    file_type: ["csv", "shp", "txt"]
    return: a text string
    """
    if file_type == "csv":
        df = pd.read_csv(file_path)
        text = str(df.head(3))
        
    if file_type == "shp":
        gdf = gpd.read_file(file_path)
        text = str(gdf.head(2))  # .drop('geomtry')
        
    if file_type == "txt":
        with open(file_path, 'r', encoding=encoding) as f:
            lines = f.readlines()
            text = ''.join(lines[:3])
    return text


def show_graph(G):    

    if has_disconnected_components(directed_graph=G):
        print("Disconnected component, please re-generate the graph!")

    nt = Network(notebook=True,     
                cdn_resources="remote",
                directed=True,
                # bgcolor="#222222",
                # font_color="white",
                height="800px",
                # width="100%",             
                #  select_menu=True,
                # filter_menu=True,

                )

    nt.from_nx(G)
    
    sinks = find_sink_node(G)
    sources = find_source_node(G)
    # print("sinks:", sinks)
    
    # Set node colors based on node type
    node_colors = []
    for node in nt.nodes:
        # print('node:', node)
        if node['node_type'] == 'data':
            #print('node:', node)
            if node['label'] in sinks:
                node_colors.append('violet')  # lightgreen
                #print(node)
            elif node['label'] in sources:
                node_colors.append('lightgreen')  # 
                #print(node)
            else:
                node_colors.append('orange')
            
        elif node['node_type'] == 'operation':
            node_colors.append('deepskyblue')            
        

    # Update node colorsb
    for i, color in enumerate(node_colors):
        nt.nodes[i]['color'] = color
        # nt.nodes[i]['shape'] = 'box'
        nt.nodes[i]['shape'] = 'dot'
        # nt.set_node_style(node, shape="box")
         
    return nt


def find_sink_node(G):
    """
    Find the sink node in a NetworkX directed graph.

    :param G: A NetworkX directed graph
    :return: The sink node, or None if not found
    """
    sinks = []
    for node in G.nodes():
        if G.out_degree(node) == 0 and G.in_degree(node) > 0:
            sinks.append(node)
    return sinks


# Function to find the source node
def find_source_node(graph):
    # Initialize an empty list to store potential source nodes
    source_nodes = []

    # Iterate over all nodes in the graph
    for node in graph.nodes():
        # Check if the node has no incoming edges
        if graph.in_degree(node) == 0:
            # Add the node to the list of source nodes
            source_nodes.append(node)

    # Return the source nodes
    return source_nodes


