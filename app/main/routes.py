from flask import render_template, flash, request, session
import re, time
from app.main.forms import *
from app.main import bp
from app.api_calls import *

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/characters', methods=['GET', 'POST'])
def characters():
    form = CharacterForm()
    if 'characters' not in session: # initializes session['characters']
        session['characters'] = {'total': 0, 'chars': []}
    if form.validate_on_submit():
        chars = re.split(r'[,\s]+', form.characters.data)
        print(f'Expected characters: {chars}')
        unique_dict = {}
        not_found = []
        duplicates = []
        over_limit = []
        response_timeout = []
        for char in session['characters']['chars']:
            unique_dict[char['character_list'][0]['name']['first_lower']] = char['character_list'][0]['name']['first']
        max_processing_time = 30
        start_time = time.time()
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
                if session['characters']['total'] < 16:
                    char_info = get_char_info(char)
                    if char_info == None:
                        response_timeout.append(char)
                    elif 'returned' in char_info:
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
        if response_timeout:
            flash(f'Some characters not included due to API response timeout', 'danger')
        form.characters.data = ''
    session.permanent = True
    return render_template('characters.html', title='Characters', form=form)

@bp.route('/clear_chars', methods=['POST'])
def clear_chars():
    session['characters'] = {'total': 0, 'chars': []}
    session.modified = True
    return {'cleared': True}

@bp.route('/delete_char', methods=['POST'])
def delete_char():
    data = request.get_json()
    char_id = data['id']

    i = 0
    if 'characters' in session:
        for char in session['characters']['chars']:
            if char['character_list'][0]['character_id'] == char_id:
                session['characters']['chars'].pop(i)
                session['characters']['total'] -= 1
                session.modified = True
                return {'total': session['characters']['total'], 'deleted': True, 'id': char_id}
            i += 1
    return char_id