import requests, json, os

SERVICE_ID = os.environ.get('SECRET_KEY', 's:example')

# returns information from census api as a json string
def call_census(url):
    try:
        response = requests.get(url, timeout=2)
        return json.loads(response.text)
    except:
        print('Timed out')
        return 0

def get_char_info(name, max_retries=3):
    name_lower = name.lower()
    url = f'https://census.daybreakgames.com/{SERVICE_ID}/get/ps2:v2/character/?name.first_lower={name_lower}&c:resolve=world'
    for _ in range(max_retries):
        response = call_census(url)
        if response:
            return response
    return None

def get_char_general_info(name, max_retries=3):
    name_lower = name.lower()
    url = f'https://census.daybreakgames.com/{SERVICE_ID}/get/ps2:v2/character?name.first_lower={name_lower}&c:resolve=stat,stat_history,world'
    for _ in range(max_retries):
        response = call_census(url)
        if response:
            return response
    return None

def get_char_infantry_info(name, max_retries=3):
    name_lower = name.lower()
    url = f'https://census.daybreakgames.com/{SERVICE_ID}/get/ps2:v2/character?name.first_lower={name_lower}&c:resolve=stat,stat_by_faction,world'
    for _ in range(max_retries):
        response = call_census(url)
        if response:
            return response
    return None

def get_char_weapon_medals(name, max_retries=3):
    name_lower = name.lower()
    url = f'https://census.daybreakgames.com/{SERVICE_ID}/get/ps2:v2/character?name.first_lower={name_lower}&c:join=characters_achievement^list:1^terms:earned_count=1^outer:0^hide:character_id%27earned_count%27start%27last_save%27last_save_date%27start_date(achievement^terms:repeatable=0^outer:0^show:name.en%27description.en^terms:description.en=*Enemies%20Killed)'
    for _ in range(max_retries):
        response = call_census(url)
        if response:
            return response
    return None