from flask import render_template, flash, request, session
import re, time
from app.reports.forms import *
from app.reports import bp
from app.api_calls import *

def get_stat_by_name(character, stat_name, profile_id='0'):
    stats = character['character_list'][0]['stats']['stat']
    for stat in stats:
        if stat['stat_name'] == stat_name and stat['profile_id'] == profile_id:
            return stat
    return None

def get_stat_value_forever(character, stat_name, profile_id='0'):
    stat = get_stat_by_name(character, stat_name, profile_id)
    if stat:
        return stat.get('value_forever', 0)
    return 0

def get_stat_by_faction_by_name(character, stat_name, profile_id='0'):
    if 'stat_by_faction' in character['character_list'][0]['stats']:
        stats = character['character_list'][0]['stats']['stat_by_faction']
        for stat in stats:
            if stat['stat_name'] == stat_name and stat['profile_id'] == profile_id:
                return stat
    return None

def get_stat_by_faction_value_forever(character, stat_name, profile_id='0'):
    stat = get_stat_by_faction_by_name(character, stat_name, profile_id)
    if stat:
        value_forever_vs = int(stat.get('value_forever_vs', 0))
        value_forever_nc = int(stat.get('value_forever_nc', 0))
        value_forever_tr = int(stat.get('value_forever_tr', 0))
        return [value_forever_vs, value_forever_nc, value_forever_tr]
    else:
        return 0

def combine_stat_by_faction(character, stat_list):
    if stat_list != 0:
        faction = character['character_list'][0]['faction_id']
        if faction == '1':
            return stat_list[1] + stat_list[2]
        elif faction == '2':
            return stat_list[0] + stat_list[2]
        elif faction == '3':
            return stat_list[0] + stat_list[1]
        elif faction == '4':
            return stat_list[0] + stat_list[1] + stat_list[2]
    else:
        return 0

@bp.route('/general', methods=['GET', 'POST'])
def general():
    form = CharacterForm2()
    char_list = {'total': 0, 'chars': []}
    totals = {'characters': 0, 'minutes_played': 0, 'score': 0, 'spm': 0, 'kills': 0, 'assists': 0, 'deaths': 0, 'k/d': 0, 'true_deaths': 0, 'true k/d': 0, 'kpm': 0, 'captures': 0, 'defenses': 0, 'adr': 0}
    chart_info = {'chars': [], 'factions': [], 'hours_played': [], 'score': [], 'spm': [], 'kills': [], 'assists': [], 'deaths': [], 'k/d': [], 'true_deaths': [], 'true k/d': [], 'kpm': [], 'captures': [], 'defenses': [], 'adr': []}
    if form.validate_on_submit():
        char_list = {'total': 0, 'chars': []}
        chars = re.split(r'[,\s]+', form.characters2.data)
        unique_dict = {}
        not_found = []
        duplicates = []
        over_limit = []
        response_timeout = []
        max_processing_time = 30
        start_time = time.time()
        if chars != ['']:
            print(f'Expected characters: {len(chars)}')
            for char in chars:
                if time.time() - start_time > max_processing_time:
                    flash('Failed to receive a timely response from the API, please try again or contact Wazix on Discord if this happens frequently.', 'danger')
                    break
                print(char)
                lowercase_char = char.lower()
                if lowercase_char in unique_dict:
                    duplicates.append(char)
                else:
                    unique_dict[lowercase_char] = char
                    if char_list['total'] < 16:
                        char_info = get_char_general_info(char)
                        if char_info == None:
                            response_timeout.append(char)
                        elif 'returned' in char_info:
                            if char_info['returned'] and char != '':
                                char_list['total'] += 1
                                char_list['chars'].append(char_info)
                            else:
                                if char != '':
                                    not_found.append(char)
                    else:
                        over_limit.append(char)
            if not_found:
                flash(f'Not found: {not_found}', 'danger')
            if duplicates:
                flash(f'Duplicate(s) removed: {duplicates}', 'danger')
            if over_limit:
                flash(f'Not included due to character limit: {over_limit}', 'danger')
            if response_timeout:
                flash(f'Some characters not included due to API response timeout', 'danger')
        elif 'characters' in session:
            print(f'Expected characters: {session["characters"]["total"]}')
            if session['characters']['chars']:
                for char in session['characters']['chars']:
                    if time.time() - start_time > max_processing_time:
                        flash('Failed to receive a timely response from the API, please try again or contact Wazix on Discord if this happens frequently.', 'danger')
                        break
                    print(char['character_list'][0]['name']['first'])
                    char_info = get_char_general_info(char['character_list'][0]['name']['first'])
                    if char_info == None:
                        response_timeout.append(char)
                    elif 'returned' in char_info:
                        if char_info['returned'] and char['character_list'][0]['name']['first'] != '':
                            char_list['total'] += 1
                            char_list['chars'].append(char_info)
                        else:
                            if char['character_list'][0]['name']['first'] != '':
                                not_found.append(char)
                if not_found:
                    flash(f'Not found: {not_found}', 'danger')
                if response_timeout:
                    flash(f'Some characters not included due to API response timeout', 'danger')
            else:
                flash(f'No characters entered or found from the "Characters" page', 'danger')
        else:
            flash(f'No characters entered or found from the "Characters" page', 'danger')
        for character in char_list['chars']:
            totals['characters'] += 1
            totals['minutes_played'] += int(character['character_list'][0]['times']['minutes_played'])
            totals['score'] += int(character['character_list'][0]['stats']['stat_history'][8]['all_time']) if 'stat_history' in character['character_list'][0]['stats'] else 0
            totals['kills'] += int(character['character_list'][0]['stats']['stat_history'][5]['all_time']) if 'stat_history' in character['character_list'][0]['stats'] else 0
            totals['assists'] += int(get_stat_value_forever(character, 'assist_count'))
            totals['deaths'] += int(character['character_list'][0]['stats']['stat_history'][2]['all_time']) if 'stat_history' in character['character_list'][0]['stats'] else 0
            totals['true_deaths'] += int(get_stat_value_forever(character, 'weapon_deaths'))
            totals['captures'] += int(character['character_list'][0]['stats']['stat_history'][3]['all_time']) if 'stat_history' in character['character_list'][0]['stats'] else 0
            totals['defenses'] += int(character['character_list'][0]['stats']['stat_history'][4]['all_time']) if 'stat_history' in character['character_list'][0]['stats'] else 0
            chart_info['chars'].append(character['character_list'][0]['name']['first'])
            chart_info['factions'].append(character['character_list'][0]['faction_id'])
            chart_info['hours_played'].append(round(int(character['character_list'][0]['times']['minutes_played']) / 60, 2))
            chart_info['score'].append(int(character['character_list'][0]['stats']['stat_history'][8]['all_time'])) if 'stat_history' in character['character_list'][0]['stats'] else 0
            chart_info['spm'].append(round(int(character['character_list'][0]['stats']['stat_history'][8]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) / int(character['character_list'][0]['times']['minutes_played']) if int(character['character_list'][0]['times']['minutes_played']) > 0 else 0, 2))
            chart_info['kills'].append(int(character['character_list'][0]['stats']['stat_history'][5]['all_time'])) if 'stat_history' in character['character_list'][0]['stats'] else 0
            chart_info['assists'].append(int(get_stat_value_forever(character, 'assist_count')))
            chart_info['deaths'].append(int(character['character_list'][0]['stats']['stat_history'][2]['all_time'])) if 'stat_history' in character['character_list'][0]['stats'] else 0
            chart_info['k/d'].append(round(int(character['character_list'][0]['stats']['stat_history'][5]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) / int(character['character_list'][0]['stats']['stat_history'][2]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) if int(character['character_list'][0]['stats']['stat_history'][2]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) > 0 else 0, 2))
            chart_info['true_deaths'].append(int(get_stat_value_forever(character, 'weapon_deaths')))
            chart_info['true k/d'].append(round(int(character['character_list'][0]['stats']['stat_history'][5]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) / int(get_stat_value_forever(character, 'weapon_deaths')) if int(get_stat_value_forever(character, 'weapon_deaths')) > 0 else 0, 2))
            chart_info['kpm'].append(round(int(character['character_list'][0]['stats']['stat_history'][5]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) / int(character['character_list'][0]['times']['minutes_played']) if int(character['character_list'][0]['times']['minutes_played']) > 0 else 0, 2))
            chart_info['captures'].append(int(character['character_list'][0]['stats']['stat_history'][3]['all_time'])) if 'stat_history' in character['character_list'][0]['stats'] else 0
            chart_info['defenses'].append(int(character['character_list'][0]['stats']['stat_history'][4]['all_time'])) if 'stat_history' in character['character_list'][0]['stats'] else 0
            chart_info['adr'].append(round(int(character['character_list'][0]['stats']['stat_history'][3]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) / int(character['character_list'][0]['stats']['stat_history'][4]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) if int(character['character_list'][0]['stats']['stat_history'][4]['all_time'] if 'stat_history' in character['character_list'][0]['stats'] else 0) > 0 else 0, 2))
        totals['spm'] = totals['score'] / totals['minutes_played'] if totals['minutes_played'] > 0 else 0
        totals['k/d'] = totals['kills'] / totals['deaths'] if totals['deaths'] > 0 else 0
        totals['true k/d'] = totals['kills'] / totals['true_deaths'] if totals['true_deaths'] > 0 else 0
        totals['kpm'] = totals['kills'] / totals['minutes_played'] if totals['minutes_played'] > 0 else 0
        totals['adr'] = totals['captures'] / totals['defenses'] if totals['defenses'] > 0 else 0
    return render_template('reports/general.html', title='General', form=form, char_list=char_list, totals=totals, chart_info=chart_info)

@bp.route('/infantry', methods=['GET', 'POST'])
def infantry():
    form = CharacterForm2()
    char_list = {'total': 0, 'chars': []}
    totals = {'characters': 0, 'minutes_played': 0, 'kills': 0, 'deaths_by': 0,
              'infil': {'minutes_played': 0, 'score': 0, 'kills': 0, 'deaths_as': 0, 'deaths_by': 0, 'shots_hit': 0, 'shots_fired': 0}, 
              'la': {'minutes_played': 0, 'score': 0, 'kills': 0, 'deaths_as': 0, 'deaths_by': 0, 'shots_hit': 0, 'shots_fired': 0}, 
              'medic': {'minutes_played': 0, 'score': 0, 'kills': 0, 'deaths_as': 0, 'deaths_by': 0, 'shots_hit': 0, 'shots_fired': 0}, 
              'engi': {'minutes_played': 0, 'score': 0, 'kills': 0, 'deaths_as': 0, 'deaths_by': 0, 'shots_hit': 0, 'shots_fired': 0}, 
              'ha': {'minutes_played': 0, 'score': 0, 'kills': 0, 'deaths_as': 0, 'deaths_by': 0, 'shots_hit': 0, 'shots_fired': 0}, 
              'max': {'minutes_played': 0, 'score': 0, 'kills': 0, 'deaths_as': 0, 'deaths_by': 0, 'shots_hit': 0, 'shots_fired': 0}}
    if form.validate_on_submit():
        char_list = {'total': 0, 'chars': []}
        chars = re.split(r'[,\s]+', form.characters2.data)
        unique_dict = {}
        not_found = []
        duplicates = []
        over_limit = []
        response_timeout = []
        max_processing_time = 30
        start_time = time.time()
        if chars != ['']:
            print(f'Expected characters: {len(chars)}')
            for char in chars:
                if time.time() - start_time > max_processing_time:
                    flash('Failed to receive a timely response from the API, please try again or contact Wazix on Discord if this happens frequently.', 'danger')
                    break
                print(char)
                lowercase_char = char.lower()
                if lowercase_char in unique_dict:
                    duplicates.append(char)
                else:
                    unique_dict[lowercase_char] = char
                    if char_list['total'] < 16:
                        char_info = get_char_infantry_info(char)
                        if char_info == None:
                            response_timeout.append(char)
                        elif 'returned' in char_info:
                            if char_info['returned'] and char != '':
                                char_list['total'] += 1
                                char_list['chars'].append(char_info)
                            else:
                                if char != '':
                                    not_found.append(char)
                    else:
                        over_limit.append(char)
            if not_found:
                flash(f'Not found: {not_found}', 'danger')
            if duplicates:
                flash(f'Duplicate(s) removed: {duplicates}', 'danger')
            if over_limit:
                flash(f'Not included due to character limit: {over_limit}', 'danger')
            if response_timeout:
                flash(f'Some characters not included due to API response timeout', 'danger')
        elif 'characters' in session:
            print(f'Expected characters: {session["characters"]["total"]}')
            if session['characters']['chars']:
                for char in session['characters']['chars']:
                    if time.time() - start_time > max_processing_time:
                        flash('Failed to receive a timely response from the API, please try again or contact Wazix on Discord if this happens frequently.', 'danger')
                        break
                    print(char['character_list'][0]['name']['first'])
                    char_info = get_char_infantry_info(char['character_list'][0]['name']['first'])
                    if char_info == None:
                        response_timeout.append(char)
                    elif 'returned' in char_info:
                        if char_info['returned'] and char['character_list'][0]['name']['first'] != '':
                            char_list['total'] += 1
                            char_list['chars'].append(char_info)
                        else:
                            if char['character_list'][0]['name']['first'] != '':
                                not_found.append(char)
                if not_found:
                    flash(f'Not found: {not_found}', 'danger')
                if response_timeout:
                    flash(f'Some characters not included due to API response timeout', 'danger')
            else:
                flash(f'No characters entered or found from the "Characters" page', 'danger')
        else:
            flash(f'No characters entered or found from the "Characters" page', 'danger')
        for character in char_list['chars']:
            totals['characters'] += 1
            # infil totals - profile id 1
            totals['infil']['minutes_played'] += int(int(get_stat_value_forever(character, 'play_time', '1')) / 60)
            totals['infil']['score'] += int(get_stat_value_forever(character, 'score', '1'))
            totals['infil']['kills'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'kills', '1'))
            totals['infil']['deaths_as'] += int(get_stat_value_forever(character, 'deaths', '1'))
            totals['infil']['deaths_by'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'killed_by', '1'))
            totals['infil']['shots_hit'] += int(get_stat_value_forever(character, 'hit_count', '1'))
            totals['infil']['shots_fired'] += int(get_stat_value_forever(character, 'fire_count', '1'))
            # la totals - profile id 3
            totals['la']['minutes_played'] += int(int(get_stat_value_forever(character, 'play_time', '3')) / 60)
            totals['la']['score'] += int(get_stat_value_forever(character, 'score', '3'))
            totals['la']['kills'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'kills', '3'))
            totals['la']['deaths_as'] += int(get_stat_value_forever(character, 'deaths', '3'))
            totals['la']['deaths_by'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'killed_by', '3'))
            totals['la']['shots_hit'] += int(get_stat_value_forever(character, 'hit_count', '3'))
            totals['la']['shots_fired'] += int(get_stat_value_forever(character, 'fire_count', '3'))
            # medic totals - profile id 4
            totals['medic']['minutes_played'] += int(int(get_stat_value_forever(character, 'play_time', '4')) / 60)
            totals['medic']['score'] += int(get_stat_value_forever(character, 'score', '4'))
            totals['medic']['kills'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'kills', '4'))
            totals['medic']['deaths_as'] += int(get_stat_value_forever(character, 'deaths', '4'))
            totals['medic']['deaths_by'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'killed_by', '4'))
            totals['medic']['shots_hit'] += int(get_stat_value_forever(character, 'hit_count', '4'))
            totals['medic']['shots_fired'] += int(get_stat_value_forever(character, 'fire_count', '4'))
            # engi totals - profile id 5
            totals['engi']['minutes_played'] += int(int(get_stat_value_forever(character, 'play_time', '5')) / 60)
            totals['engi']['score'] += int(get_stat_value_forever(character, 'score', '5'))
            totals['engi']['kills'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'kills', '5'))
            totals['engi']['deaths_as'] += int(get_stat_value_forever(character, 'deaths', '5'))
            totals['engi']['deaths_by'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'killed_by', '5'))
            totals['engi']['shots_hit'] += int(get_stat_value_forever(character, 'hit_count', '5'))
            totals['engi']['shots_fired'] += int(get_stat_value_forever(character, 'fire_count', '5'))
            # ha totals - profile id 6
            totals['ha']['minutes_played'] += int(int(get_stat_value_forever(character, 'play_time', '6')) / 60)
            totals['ha']['score'] += int(get_stat_value_forever(character, 'score', '6'))
            totals['ha']['kills'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'kills', '6'))
            totals['ha']['deaths_as'] += int(get_stat_value_forever(character, 'deaths', '6'))
            totals['ha']['deaths_by'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'killed_by', '6'))
            totals['ha']['shots_hit'] += int(get_stat_value_forever(character, 'hit_count', '6'))
            totals['ha']['shots_fired'] += int(get_stat_value_forever(character, 'fire_count', '6'))
            # max totals - profile id 7
            totals['max']['minutes_played'] += int(int(get_stat_value_forever(character, 'play_time', '7')) / 60)
            totals['max']['score'] += int(get_stat_value_forever(character, 'score', '7'))
            totals['max']['kills'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'kills', '7'))
            totals['max']['deaths_as'] += int(get_stat_value_forever(character, 'deaths', '7'))
            totals['max']['deaths_by'] += combine_stat_by_faction(character, get_stat_by_faction_value_forever(character, 'killed_by', '7'))
            totals['max']['shots_hit'] += int(get_stat_value_forever(character, 'hit_count', '7'))
            totals['max']['shots_fired'] += int(get_stat_value_forever(character, 'fire_count', '7'))
        totals['minutes_played'] = totals['infil']['minutes_played'] + totals['la']['minutes_played'] + totals['medic']['minutes_played'] + totals['engi']['minutes_played'] + totals['ha']['minutes_played'] + totals['max']['minutes_played']
        totals['kills'] = totals['infil']['kills'] + totals['la']['kills'] + totals['medic']['kills'] + totals['engi']['kills'] + totals['ha']['kills'] + totals['max']['kills']
        totals['deaths_by'] = totals['infil']['deaths_by'] + totals['la']['deaths_by'] + totals['medic']['deaths_by'] + totals['engi']['deaths_by'] + totals['ha']['deaths_by'] + totals['max']['deaths_by']
    return render_template('reports/infantry.html', title='Infantry', form=form, totals=totals, char_list=char_list)
"""
@bp.route('/vehicle', methods=['GET', 'POST'])
def vehicle():
    form = CharacterForm2()
    return render_template('reports/vehicle.html', title='Vehicle', form=form)
"""
@bp.route('/weapons', methods=['GET', 'POST'])
def weapons():
    form = CharacterForm2()
    char_list = {'total': 0, 'chars': []}
    medals = {'total_auraxium': 0, 'total_gold': 0, 'total_silver': 0, 'total_bronze': 0, 'chars': []}
    chart_info = {'chars': []}
    if form.validate_on_submit():
        char_list = {'total': 0, 'chars': []}
        chars = re.split(r'[,\s]+', form.characters2.data)
        unique_dict = {}
        not_found = []
        duplicates = []
        over_limit = []
        response_timeout = []
        max_processing_time = 30
        start_time = time.time()
        if chars != ['']:
            print(f'Expected characters: {len(chars)}')
            for char in chars:
                if time.time() - start_time > max_processing_time:
                    flash('Failed to receive a timely response from the API, please try again or contact Wazix on Discord if this happens frequently.', 'danger')
                    break
                print(char)
                lowercase_char = char.lower()
                if lowercase_char in unique_dict:
                    duplicates.append(char)
                else:
                    unique_dict[lowercase_char] = char
                    if char_list['total'] < 16:
                        char_info = get_char_weapon_medals(char)
                        if char_info == None:
                            response_timeout.append(char)
                        elif 'returned' in char_info:
                            if char_info['returned'] and char != '':
                                char_list['total'] += 1
                                char_list['chars'].append(char_info)
                            else:
                                if char != '':
                                    not_found.append(char)
                    else:
                        over_limit.append(char)
            if not_found:
                flash(f'Not found: {not_found}', 'danger')
            if duplicates:
                flash(f'Duplicate(s) removed: {duplicates}', 'danger')
            if over_limit:
                flash(f'Not included due to character limit: {over_limit}', 'danger')
            if response_timeout:
                flash(f'Some characters not included due to API response timeout', 'danger')
        elif 'characters' in session:
            print(f'Expected characters: {session["characters"]["total"]}')
            if session['characters']['chars']:
                for char in session['characters']['chars']:
                    if time.time() - start_time > max_processing_time:
                        flash('Failed to receive a timely response from the API, please try again or contact Wazix on Discord if this happens frequently.', 'danger')
                        break
                    print(char['character_list'][0]['name']['first'])
                    char_info = get_char_weapon_medals(char['character_list'][0]['name']['first'])
                    if char_info == None:
                        response_timeout.append(char)
                    elif 'returned' in char_info:
                        if char_info['returned'] and char['character_list'][0]['name']['first'] != '':
                            char_list['total'] += 1
                            char_list['chars'].append(char_info)
                        else:
                            if char['character_list'][0]['name']['first'] != '':
                                not_found.append(char)
                if not_found:
                    flash(f'Not found: {not_found}', 'danger')
                if response_timeout:
                    flash(f'Some characters not included due to API response timeout', 'danger')
            else:
                flash(f'No characters entered or found from the "Characters" page', 'danger')
        else:
            flash(f'No characters entered or found from the "Characters" page', 'danger')
        
        for character in char_list['chars']:
            chart_info['chars'].append(character['character_list'][0]['name']['first'])
            char_medals = {'name': character['character_list'][0]['name']['first'],'auraxium': 0, 'weapons': []}
            for achievment in character['character_list'][0]['character_id_join_characters_achievement']:
                achiev_desc = achievment['achievement_id_join_achievement']['description']['en']
                achiev_name = achievment['achievement_id_join_achievement']['name']['en']

                if achiev_desc == '10 Enemies Killed':
                    medals['total_bronze'] += 1
                elif achiev_desc == '50 Enemies Killed':
                    medals['total_silver'] += 1
                elif achiev_desc == '100 Enemies Killed':
                    medals['total_gold'] += 1
                elif achiev_desc == '1000 Enemies Killed':
                    medals['total_auraxium'] += 1
                    char_medals['auraxium'] += 1
                    char_medals['weapons'].append({'name': achiev_name, 'finish_date': achievment['finish_date']})
            medals['chars'].append(char_medals)
    return render_template('reports/weapons.html', title='Weapons', form=form, char_list=char_list, chart_info=chart_info, medals=medals)
"""
@bp.route('/alt_search', methods=['POST'])
def alt_search():
    try:
        data = request.json
        user_input = data.get('characters')
        alts = ['Wazix11', 'WazixVuzix', '1Wazix1', 'botWaz', 'Wazixx', 'Wazix', 'xWazix', 'WaziBot', 'iWazix']
        result = {'status': 'success', 'choices': alts}
        return jsonify(result)
    except Exception as e:
        error_message = str(e)
        result = {'status': 'error', 'message': error_message}
        return jsonify(result)

@bp.route('/test', methods=['GET', 'POST'])
def test():
    form = TestAltCharacterForm()
    if 'characters' not in session: # initializes session['characters']
        session['characters'] = {'total': 0, 'chars': []}
    if form.validate_on_submit():
        chars = re.split(r'[,\s]+', form.characters.data)
        unique_dict = {}
        not_found = []
        duplicates = []
        over_limit = []
        for char in session['characters']['chars']:
            unique_dict[char['character_list'][0]['name']['first_lower']] = char['character_list'][0]['name']['first']
        for char in chars:
            print(char)
            lowercase_char = char.lower()
            if lowercase_char in unique_dict:
                duplicates.append(char)
            else:
                unique_dict[lowercase_char] = char
                if session['characters']['total'] < 16:
                    char_info = get_char_info(char)
                    if char_info['returned']:
                        session['characters']['total'] += 1
                        session['characters']['chars'].append(char_info)
                        session.modified = True
                    else:
                        not_found.append(char)
                else:
                    over_limit.append(char)
        if not_found:
            flash(f'Not found: {not_found}', 'danger')
        if duplicates:
            flash(f'Duplicate(s) removed: {duplicates}', 'danger')
        if over_limit:
            flash(f'Not included due to character limit: {over_limit}', 'danger')
        form.characters.data = ''
    session.permanent = True
    return render_template('reports/test.html', title='Characters', form=form)
"""