import os
import random
# from .LLM.vivogpt import VivoClass
from .LLM.auth_util import gen_sign_headers
import uuid
import time
import requests
import json
import datetime

# llm = VivoClass(APP_ID = '3034766937', APP_KEY = 'JNvcUCJwCBwkCaya', URI = '/vivogpt/completions', DOMAIN = 'api-ai.vivo.com.cn', METHOD = 'POST')
APP_ID = '3034766937'
APP_KEY = 'JNvcUCJwCBwkCaya'
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'

def init_state():
    state = {
        "in_game": False,
        "step":0,
        "current_round": 0,
        "alive_flag": [1, 1, 1, 1, 1, 1],
        "player_identities": ["", "", "", "", "", ""],
        "wolves_kill_count":[0, 0, 0, 0, 0, 0],
        "guard_flag":[0, 0, 0, 0, 0, 0],
        "player1_history": [],
        "player2_history": [],
        "player3_history": [],
        "player4_history": [],
        "player5_history": [],
        "player6_history": [],
    }
    return state

def get_llm_json_answer(result):
    json_dict = extract_json_from_llm_answer(result)
    return json_dict

def extract_json_from_llm_answer(result, replace_list=["\n", " ", "\t"]):
    for replace_str in replace_list:
        result = result.replace(replace_str, "")

        # 解析JSON字符串为字典
    json_dict = json.loads(result)
    return json_dict


def fn_start_or_restart():
    # 初始化state
    state = init_state()
    state["in_game"] = True

    params = {
        'requestId': str(uuid.uuid4())
    }
    print('requestId:', params['requestId'])
    prompt = f'''狼人杀是一款多人参与的，通过语言描述推动、较量口才和分析判断能力的策略类桌面游戏。
    你作为一个狼人杀法官，你需要给出六个身份牌，其中包含两个平民，一个预言家，一个守卫和两个狼人。请你每次都随机地打乱并给出六个身份牌,通过json的格式返回。
    返回内容是一个字典{"{"}"身份1":str, "身份2":str, "身份3":str, "身份4":str, "身份5":str, "身份6":str{"}"}。
        '''
    data = {
        'prompt': prompt,
        'model': 'vivo-BlueLM-TB',
        'sessionId': str(uuid.uuid4()),
        'extra': {
            'temperature': 0.9
        }
    }
    headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
    headers['Content-Type'] = 'application/json'

    # start_time = time.time()
    url = 'https://{}{}'.format(DOMAIN, URI)
    response = requests.post(url, json=data, headers=headers, params=params)

    if response.status_code == 200:
        res_obj = response.json()
        print(f'response:{res_obj}')
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']

            json_dict = get_llm_json_answer(content)
            print(json_dict)
            # state['player_identities'] = json_dict.values()
            state['player_identities'] = [value for value in json_dict.values()]

            for i in range(0, 5):
                index_1 = random.choice([0])
                index_2 = random.choice([1, 2, 3, 4, 5])
                if(index_1 != index_2):
                    temp = state['player_identities'][index_1]
                    state['player_identities'][index_1] = state['player_identities'][index_2]
                    state['player_identities'][index_2] = temp
                else:
                    continue
            print(state['player_identities'])

    else:
        print(response.status_code, response.text)

    if (state['player_identities'][0] == "守卫"):
        return state, f"你的身份是 `{state['player_identities'][0]}`，你每晚可以守护一名玩家免受狼人杀害。", "", "", "", "", "", "","未选择", "", "", "", "", "", "Source/start.jpg"

    if (state['player_identities'][0] == "狼人"):
        return state, f"你的身份是 `{state['player_identities'][0]}`，你晚上可以投票杀死其他玩家。", "", "", "", "", "", "","未选择", "", "", "", "", "", "Source/start.jpg"

    if (state['player_identities'][0] == "平民"):
        return state, f"你的身份是 `{state['player_identities'][0]}`，你没有任何特殊技能，主要任务是在白天通过发言和投票帮助好人阵营获胜。", "", "", "", "", "", "","未选择", "", "", "", "", "", "Source/start.jpg"

    if (state['player_identities'][0] == "预言家"):
        return state, f"你的身份是 `{state['player_identities'][0]}`，你每晚可以选择查验一名玩家的身份，判断其是好人还是狼人。", "", "", "", "", "", "","未选择", "", "", "", "", "", "Source/start.jpg"


def fn_skills_use(state, skills_prompt):
    system_text = ""
    player_select = [int(str(skills_prompt)), 0, 0, 0, 0, 0]

    if state["in_game"] == False:
        system_text = "游戏未开始，请点击重新开始/开始按钮进行游戏"
    elif state["step"] == 1:
        system_text = f"你的身份是 `{state['player_identities'][0]}`，请先投票"
    else:
        system_text = f"你的身份是 `{state['player_identities'][0]}`，请根据其他玩家的发言进行投票"
        state["step"] = 1

    # 玩家0是守卫
    if state['player_identities'][0] == "守卫":
        index = player_select[[0] - 1]
        if(index >= 0 and len(state['player_identities'])):
            state['guard_flag'][index] = 1

    # 玩家0是狼人
    if (state['player_identities'][0] == "狼人"):
        state['wolves_kill_count'][player_select[[0] - 1]] = 2

    # 玩家0是预言家
    if (state['player_identities'][0] == "预言家"):
        system_text = f"你查验玩家的身份是{state['player_identities'][player_select[0]]}"

    # Skills of other players
    for i in range(1, 6):
        # Wolf
        wolves_count = 0
        # 如果当前玩家是狼人
        if(state['player_identities'][i] == "狼人"):
            wolves_count += 1
            # 如果狼人count为2，则为第二个狼人
            if(wolves_count == 2):
                # 随机选一位玩家刀
                wolves_sign = random.choice([0, 1, 2, 3, 4, 5])
                # 如果第一位狼人标记为第二位狼人，则重新标记
                while (wolves_sign == wolves_flag):
                    wolves_sign = random.choice([0, 1, 2, 3, 4, 5])
                continue
            wolves_flag = i

        # Guard
        # 如果玩家是Guard，随机选一位玩家守护
        if(state['player_identities'][i] == "守卫"):
            guard_sign = random.choice([0, 1, 2, 3, 4, 5])
            state['guard_flag'][guard_sign] = 1

        # Prophet
        # 如果是Prophet，随机选一位玩家查验
        if(state['player_identities'][i] == "预言家"):
            prophet_sign = random.choice([0, 1, 2, 3, 4, 5])

    return state, system_text

def skills_is_dead(state):
    for i in range(0, 5):
        # 玩家存活，狼人票数为2，无人守护
        if (state['alive_flag'][i] == 1 and state['wolves_kill_count'][i] == 2 and state['guard_flag'][i] == 0):
            return True
        else:
            return False


def fn_check_kill(state):
    state = init_state()
    for i in range(0, 5):
        if(state["wolves_kill_count"][i] == 2):
            state["alive_flag"] = 0
    return state

def fn_speek(state, prompt):
    system_text = ""
    player_text = [str(prompt), "", "", "", "", "", ""]

    return (state, system_text,
            player_text[1], player_text[2], player_text[3], player_text[4], player_text[5])

def fn_vote(state, vote_prompt):
    system_text = ""
    player_vote = ["", "", "", "", "", ""]
    img = ""

    return (state, system_text,
            "", "", "", "", "", "",
            player_vote[1], player_vote[2], player_vote[3], player_vote[4], player_vote[5],
            img)

