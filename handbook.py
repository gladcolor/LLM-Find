import toml
from glob import glob
import os

def collect_a_handbook():

    return


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
    for idx, book in enumerate(handbook_files):
        handbook = toml.load(book)
        basename = os.path.basename(book)[:-4]
        description = f"{idx + 1}. {basename}. {handbook['brief_description']}"
        print(description)

    descriptions_str = r"\n".join(descriptions)
    return descriptions_str

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
