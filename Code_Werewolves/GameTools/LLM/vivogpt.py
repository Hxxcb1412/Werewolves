import json
import uuid
import time
import requests
from .auth_util import gen_sign_headers

class VivoClass(object):
    """
    Vivogpt API封装类

    Returns:
        None

    """
    APP_ID = '3034766937'
    APP_KEY = 'JNvcUCJwCBwkCaya'
    URI = '/vivogpt/completions'
    DOMAIN = 'api-ai.vivo.com.cn'
    METHOD = 'POST'

    def __init__(self, APP_ID, APP_KEY, URI, DOMAIN, METHOD):
        APP_ID = APP_ID
        APP_KEY = APP_KEY
        URI = URI
        DOMAIN = DOMAIN
        METHOD = METHOD
        self.chat_history = []

    def get_llm_answer(self, prompt):
        data = {
            'message': [{'role': 'user', 'content': prompt}],
            'model': 'vivo-BlueLM-TB',
            'sessionId': str(uuid.uuid4()),
            'extra': {
            'temperature': 0.9
            }
        }
        params = {
            'requestId': str(uuid.uuid4())
        }
        headers = gen_sign_headers(self.APP_ID, self.APP_KEY, self.METHOD, self.URI, params)
        headers['Content-Type'] = 'application/json'

        url = 'https://{}{}'.format(self.DOMAIN, self.URI)
        response = requests.post(url, json=data, headers=headers, params=params)
        if response.status_code == 200:
            res_obj = response.json()
            # print(f'response:{res_obj}')
            return res_obj
            if res_obj['code'] == 0 and res_obj.get('data'):
                content = res_obj['data']['content']
                # print(f'final content:\n{content}')
                json_dict = get_llm_json_answer(content)
                return json_dict
        else:
            # print(response.status_code, response.text)
            return response.text

    def extract_json_from_llm_answer(self, result, replace_list=["\n", " ", "\t"]):
        # 清理JSON字符串
        for replace_str in replace_list:
            result = result.replace(replace_str, "")

            # 解析JSON字符串为字典
        json_dict = json.loads(result)
        return json_dict

    def get_llm_json_answer(self, prompt):
        result = self.get_llm_answer(prompt)
        print(result)
        # json_dict = self.extract_json_from_llm_answer(result)
        return result