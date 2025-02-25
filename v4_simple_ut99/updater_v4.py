from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, render_template
from flask_cors import CORS  # Import CORS
import json
import sys
import os
import logging
import requests
import shutil
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# Path to the JSON files
MATCHLITE_JSON_PATH = 'static/match_lite.json'
SIMPLEMAPLIST_JSON_PATH = 'static/simple_maplist.json'
SETTINGS_PATH = 'static/settings.json'
SCHEDULE_PATH = 'static/schedule.json'


# Load Match JSON
def load_smaplist_data():
    if os.path.exists(SIMPLEMAPLIST_JSON_PATH):
        with open(SIMPLEMAPLIST_JSON_PATH, 'r') as file:
            return json.load(file)
    return {"maps": []}

def load_schedule_data():
    if os.path.exists(SCHEDULE_PATH):
        with open(SCHEDULE_PATH, 'r') as file:
            return json.load(file)
    return {"games": []}

def load_matchl_data():
    if os.path.exists(MATCHLITE_JSON_PATH):
        with open(MATCHLITE_JSON_PATH, 'r') as file:
            return json.load(file)
    return {"match_type": 3, "current_map": "", "teams": [], "game_history": []}

        
def save_matchl_data(data):
    with open(MATCHLITE_JSON_PATH, 'w') as file:
        json.dump(data, file, indent=2)

def save_smaplist_data(data):
    with open(SIMPLEMAPLIST_JSON_PATH, 'w') as file:
        json.dump(data, file, indent=2)

def save_schedule_data(data):
    with open(SCHEDULE_PATH, 'w') as file:
        json.dump(data, file, indent=2)  

# Main menu
@app.route('/')
def serve_html():
    return send_from_directory('.', 'main.html')

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('.', 'favicon.ico')

# ban 
@app.route('/ban')
def serve_bans():
    return send_from_directory('.', 'map_ban.html')

# scoreboard controls for generic scoreboard
@app.route('/lite')
def serve_updatel():
    return send_from_directory('.', 'update_lite.html')

# Predefined maplist editor for simple scoreboard
@app.route('/map_editor')
def serve_map_editor():
    return send_from_directory('.', 'simple_maplist_editor.html')

# Schedule editor 
@app.route('/sch_edit')
def serve_schedule_editor():
    return send_from_directory('.', 'schedule_editor.html')

@app.route('/settings')
def serve_settings():
    settings = load_settings()
    remote_url = settings.get('remote_url', '')    
#    return send_from_directory('.', settings.html)
    return render_template('settings.html', remote_url=remote_url)

# scoreboard
@app.route('/scoreboard')
def serve_scoreboard_generic():
    return send_from_directory('.', 'scoreboard_generic.html')

# scoreboard
@app.route('/scoreboard2')
def serve_scoreboard_alt():
    return send_from_directory('.', 'scoreboard_alt.html')

# breakdown of best-of-X match by maps for generic setup, uses saved results from generic scoreboard control
@app.route('/map_breakdown')
def serve_map_breakdown():
    return send_from_directory('.', 'map_breakdown_lite.html')

# Transition stinger for OBS
@app.route('/stinger')
def serve_stinger():
    return send_from_directory('.', 'stinger_generic.html')

@app.route('/table')
def serve_table():
    return send_from_directory('.', 'table.html')

# waiting screen for the first game listed in the schedule that's within an hour
@app.route('/next')
def serve_wait():
    return send_from_directory('.', 'game_wait.html')

# upcoming games schedule
@app.route('/schedule')
def serve_schedule():
    return send_from_directory('.', 'schedule.html')

# upcoming games schedule
@app.route('/map_results')
def serve_map_results():
    return send_from_directory('.', 'map_results.html')

# generic scoreboard control panel API to get the list of past games within a best-of-X match 
@app.route('/matchesl', methods=['GET'])
def get_matchesl():
    match_data = load_matchl_data()
    return jsonify(match_data['game_history'])

# generic scoreboard control panel API to retrive the list of maps from simple_maplist.json
@app.route('/smaplist', methods=['GET'])
def get_maps():
    map_data = load_smaplist_data()
    return jsonify(map_data['maps'])

# API to retyrive list of scheduled games from schedule.json
@app.route('/schlist', methods=['GET'])
def get_scheduled_games():
    schedule_data = load_schedule_data()
    return jsonify(schedule_data['games'])

# API to update game data within a generic best-of-X match
@app.route('/matchl', methods=['POST'])
def update_matchl():
    match_data = load_matchl_data()
    data = request.json

    # Update the match type and current map
    match_data['match_type'] = data['match_type']
    match_data['match_no'] = data['match_no']
    match_data['attack'] = data['attack']
    match_data['short_names'] = data['short_names']
    match_data['current_map'] = data['current_map']
    match_data['teams'] = data['teams']

    save_matchl_data(match_data)
    return jsonify({"message": "Match updated successfully!"})

# generic scoreboard API to add match result
@app.route('/resultl', methods=['POST'])
def add_resultl():
    match_data = load_matchl_data()
    data = request.json

    # Initialize game_history if it's empty
    if 'game_history' not in match_data:
        match_data['game_history'] = []
        logging.info("match data sent had no game history")

    for index, match in enumerate(match_data['game_history']):
        if match['match_number'] == data['match_number']:
            # Overwrite existing match entry
            match_data['game_history'][index] = data
            save_matchl_data(match_data)
            return jsonify({"message": "Match entry updated successfully!"}), 200

    # Add the new result to the game history
    match_data['game_history'].append(data)
    save_matchl_data(match_data)
    return jsonify({"message": "Result added successfully!"})


# generic scoreboard API to delete a match
@app.route('/matchl/<int:match_number>', methods=['DELETE'])
def delete_matchl(match_number):
    match_data = load_matchl_data()
    logging.info("deleting item " + str(match_number))

    if 'game_history' not in match_data:
        return jsonify({"message": "No matches found to delete."}), 404  # Return a 404 if no matches exist

    for index, match in enumerate(match_data['game_history']):
        logging.info("looking for " + str(match_number) + ", this is " + str(match['match_number']))
        if match['match_number'] == match_number:
            logging.info("item no " + str(match_number) + " exists, removing")
            match_data['game_history'].remove(match)

    save_matchl_data(match_data)
    return jsonify({"message": "Match deleted successfully!"})

# API to add simple match entry for generic scoreboard
@app.route('/addmap', methods=['POST'])
def add_map():
    maplist_data = load_smaplist_data()
    data = request.json

    # Initialize game_history if it's empty
    if 'maps' not in maplist_data:
        maplist_data['maps'] = []
        logging.info("No maps in the list")

    # Add the new result to the game history
    maplist_data['maps'].append(data)
    save_smaplist_data(maplist_data)
    return jsonify({"message": "Map added successfully!"})

# API to delete simple match entry for generic scoreboard
@app.route('/map/<int:map_number>', methods=['DELETE'])
def delete_map(map_number):
    maplist_data = load_smaplist_data()
    logging.info("Maplist: " + str(maplist_data))
    logging.info("deleting item " + str(map_number))

    maplist_data['maps'].pop(map_number)

    save_smaplist_data(maplist_data)
    return jsonify({"message": "maps deleted successfully!"})

# API to add a scheduled game
@app.route('/addschgame', methods=['POST'])
def add_scheduled_game():
    schedule_data = load_schedule_data()
    data = request.json

    # Initialize game_history if it's empty
    if 'games' not in schedule_data:
        schedule_data['games'] = []
        logging.info("No games in the list")

    # Add the new result to the game history
    schedule_data['games'].append(data)
    save_schedule_data(schedule_data)
    return jsonify({"message": "Scheduled game added successfully!"})

# API to delete a scheduled game
@app.route('/schgame/<int:game_number>', methods=['DELETE'])
def delete_scheduled_game(game_number):
    schedule_data = load_schedule_data()
    logging.info("Scheduled games: " + str(schedule_data))
    logging.info("deleting item " + str(game_number))

    schedule_data['games'].pop(game_number)

    save_schedule_data(schedule_data)
    return jsonify({"message": "game successfully deleted fropm schedule!"})

# API to add a new map ban
@app.route('/add_map_ban', methods=['POST'])
def add_map_ban():
    map_id = request.json.get("id")
    map_name = request.json.get("name")
    banning_team_id = request.json.get("banning_team_id")
    action = request.json.get("action")
    match_data = load_matchl_data()
    
    # Append the new ban entry
    new_ban = {
        "id": map_id,
        "name": map_name,      
        "banning_team_id": banning_team_id,
        "action": action
    }
    match_data.setdefault("map_bans", []).append(new_ban)
    save_matchl_data(match_data)
    return jsonify(success=True)


# API to undo the last map ban
@app.route('/undo_map_ban', methods=['POST'])
def undo_map_ban():
    match_data = load_matchl_data()
    if "map_bans" in match_data and match_data["map_bans"]:
        match_data["map_bans"].pop()  # Remove the last entry
        save_matchl_data(match_data)
        return jsonify(success=True)
    return jsonify(success=False)

# API to reset map ban list
@app.route('/reset_map_ban', methods=['POST'])
def reset_map_ban():
    match_data = load_matchl_data()
    if "map_bans" in match_data and match_data["map_bans"]:
        match_data["map_bans"].clear()  # Remove the last entry
        save_matchl_data(match_data)
        return jsonify(success=True)
    return jsonify(success=False)

# API to get map name from an id (simple)
@app.route('/getmapname//<int:map_id>', methods=['GET'])
def get_map_by_id():
    map_data = load_smaplist_data()
    return jsonify(map_data['maps'])

# ================================================
# JSON update functionalty
#
# ================================================

def load_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, 'r') as file:
            return json.load(file)
    return {}

def save_settings(settings):
    with open(SETTINGS_PATH, 'w') as file:
        json.dump(settings, file, indent=2)

def backup_json(filename):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    name, ext = os.path.splitext(filename)
    backup_filename = f"{name}.backup_{timestamp}.json"
    backup_folder = os.path.join(os.getcwd(), 'static/backup')
    
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    
    backup_file_path = os.path.join(backup_folder, os.path.basename(backup_filename))
    shutil.copy(filename, backup_file_path)        

@app.route('/set-event', methods=['POST'])
def set_event():
    eventName = request.form['eventName']
    settings = load_settings()
    settings['eventName'] = eventName
    save_settings(settings)
    return redirect(url_for('serve_settings'))

@app.route('/set-map-item-gap', methods=['POST'])
def set_map_results_gap():
    mapItemGap = request.form['mapItemGap']
    settings = load_settings()
    settings['mapItemGap'] = mapItemGap
    save_settings(settings)
    return redirect(url_for('serve_settings'))

@app.route('/set-map-item-size', methods=['POST'])
def set_map_item_size():
    mapItemSize = request.form['mapItemSize']
    settings = load_settings()
    settings['mapItemSize'] = mapItemSize
    save_settings(settings)
    return redirect(url_for('serve_settings'))

@app.route('/set-sch-disp-window', methods=['POST'])
def set_sch_disp_window():
    scheduleDisplayWindow = request.form['scheduleDisplayWindow']
    settings = load_settings()
    settings['scheduleDisplayWindow'] = scheduleDisplayWindow
    save_settings(settings)
    return redirect(url_for('serve_settings'))

if __name__ == '__main__':
    app.run(host='0.0.0.0')
#    app.run(debug=True)



