# import toml
import tomllib
import configparser

from glob import glob
import os
import sys
import logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class CaseSensitiveConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr):
        return optionstr  # Override to preserve case sensitivity

def collect_a_handbook(source_ID, source_dir='Handbooks', keys_dir='Keys'):
    handbook_file = os.path.join(source_dir, f'{source_ID}.toml')
    with open(handbook_file, "rb") as f:
        handbook = tomllib.load(f)
    handbook_total_str = handbook['handbook']

    # load keys
    key_file = os.path.join(keys_dir, f"{source_ID}.keys")
    if os.path.exists(key_file):
        keys = load_keys(source_ID, keys_dir)
        # replace key placeholders:
        for key in keys.keys():
            print(key, keys[key])
            handbook_total_str = handbook_total_str.replace(f"{{{key}}}",  keys[key])

    handbook_lines = handbook_total_str.strip().split('\n')
    numbered_handbook_str = ''
    for idx, line in enumerate(handbook_lines):
        line = line.strip(' ')
        numbered_handbook_str += f"{idx + 1}. {line}\n"

    for variable in handbook.keys():
        numbered_handbook_str = numbered_handbook_str.replace(f"{{{variable}}}",
                                                              handbook[variable])
    # print(handbook['code_example'])
    return numbered_handbook_str

def load_keys_v0(source_ID, keys_dir='Keys'):  # using .toml format, which requires quotation marks, not friendly for users
    key_file = os.path.join(keys_dir, f"{source_ID}.keys")
    with open(key_file, "rb") as f:
        keys = tomllib.load(f)
    return keys

def load_keys(source_ID, keys_dir='Keys'):  # using Python config format, which not requires quotation marks
    key_file = os.path.join(keys_dir, f"{source_ID}.keys")
    config = CaseSensitiveConfigParser()
    config.read(key_file)
    # keys = config['API_Key'].keys()
    # print("config['API_Key'].keys():", config['API_Key'].keys())
    keys_dict = {}
    for key in config['API_Key'].keys():
        keys_dict[key] = config.get("API_Key", key)
        # print("Key:", key)

    # print("keys_dict:", keys_dict)
    return keys_dict

def collect_datasources():
    return

def collect_handbook_files(source_dir='Handbooks'):
    handbooks = glob(os.path.join(source_dir, "*.toml"))
    try:
        handbooks.remove(os.path.join(source_dir, "template.toml"))
    except:
        pass
    # print(handbooks)
    return handbooks
def assemble_handbook_description(handbook_files):
    descriptions = []
    data_source_dict = {}
    for idx, book in enumerate(handbook_files):
        with open(book, "rb") as f:
            handbook = tomllib.load(f)
        data_source_ID = os.path.basename(book)[:-5]   # data_source_ID is the name of .toml file
        data_source_name =  handbook['data_source_name'].strip()
        description = f"{idx + 1}. {data_source_name}. {handbook['brief_description'].strip()}"
        # print(description)
        descriptions.append(description)
        data_source_dict[data_source_name] = {"ID": data_source_ID}
    data_source_dict['Unknown'] = {"ID": "Unknown"}
    descriptions_str = "\n".join(descriptions)
    return descriptions_str, data_source_dict

def collect_key_for_a_datasource(source_dir='Handbooks'):

    return "tested ok."

class Handbook():
    """
    class for the handbook. Carefully maintain it.  
    
    by Huan Ning, 2024-08-31
    """
    def __init__(self, 
                 handbook_file,
                 verbose=True,
                ):        
        self.handbook_file = handbook_file        
         
        self.verbose = verbose

         

    def get_LLM_reply(self,
            prompt,
            verbose=True,
            temperature=1,
            stream=True,
            retry_cnt=3,
            sleep_sec=10,
            system_role=None,
            model=None,
            ):


        if system_role is None:
            system_role = self.role

        if model is None:
            model = self.model

        # Query ChatGPT with the prompt
        # if verbose:
        #     print("Geting LLM reply... \n")
        count = 0
        isSucceed = False
        self.chat_history.append({'role': 'user', 'content': prompt})
        while (not isSucceed) and (count < retry_cnt):
            try:
                count += 1
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
                print(f"Error in get_LLM_reply(), will sleep {sleep_sec} seconds, then retry {count}/{retry_cnt}: \n",
                      e)
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

        response = response_chucks  # good for saving

        content = helper.extract_content_from_LLM_reply(response)

        self.chat_history.append({'role': 'assistant', 'content': content})

        return response
