from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, render_template
from flask_cors import CORS  # Import CORS
import json
import os
import logging
import requests
import shutil
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# Path to the JSON files
MATCH_JSON_PATH = 'static/match.json'
MATCHLITE_JSON_PATH = 'static/match_lite.json'
MATCHES_JSON_PATH = 'static/matches.json'
SIMPLEMAPLIST_JSON_PATH = 'static/simple_maplist.json'
TOURNAMENT_JSON_PATH = 'static/tournament.json'
SETTINGS_PATH = 'static/settings.json'

# Load Tournament JSON (this is static data)
def load_tournament_data():
    if os.path.exists(TOURNAMENT_JSON_PATH):
        with open(TOURNAMENT_JSON_PATH, 'r') as file:
            return json.load(file)
    return {"teams": [], "maps": []}

# Load Match JSON
def load_match_data():
    if os.path.exists(MATCH_JSON_PATH):
        with open(MATCH_JSON_PATH, 'r') as file:
            return json.load(file)
    return {"match_type": 3, "current_map": "", "teams": [], "game_history": []}

def load_smaplist_data():
    if os.path.exists(SIMPLEMAPLIST_JSON_PATH):
        with open(SIMPLEMAPLIST_JSON_PATH, 'r') as file:
            return json.load(file)
    return {"maps": []}

def load_matchl_data():
    if os.path.exists(MATCHLITE_JSON_PATH):
        with open(MATCHLITE_JSON_PATH, 'r') as file:
            return json.load(file)
    return {"match_type": 3, "current_map": "", "teams": [], "game_history": []}

# Save Match JSON
def save_match_data(data):
    with open(MATCH_JSON_PATH, 'w') as file:
        json.dump(data, file, indent=2)
        
def save_matchl_data(data):
    with open(MATCHLITE_JSON_PATH, 'w') as file:
        json.dump(data, file, indent=2)

def save_smaplist_data(data):
    with open(SIMPLEMAPLIST_JSON_PATH, 'w') as file:
        json.dump(data, file, indent=2)        

# Serve the update.html file
@app.route('/')
def serve_html():
    return send_from_directory('.', 'main.html')

@app.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('.', 'favicon.ico')

@app.route('/update')
def serve_update():
    return send_from_directory('.', 'update.html')

@app.route('/ban')
def serve_band():
    return send_from_directory('.', 'map_ban.html')

@app.route('/lite')
def serve_updatel():
    return send_from_directory('.', 'update_lite.html')

@app.route('/settings')
def serve_settings():
    settings = load_settings()
    remote_url = settings.get('remote_url', '')    
#    return send_from_directory('.', settings.html)
    return render_template('settings.html', remote_url=remote_url)

# Serve the scoreboard.html file
@app.route('/scoreboard')
def serve_scoreboard():
    return send_from_directory('.', 'scoreboard.html')

@app.route('/sb_gen')
def serve_scoreboard_generic():
    return send_from_directory('.', 'scoreboard_generic.html')

# Serve the last5.html file
@app.route('/lastv')
def serve_lastvgames():
    return send_from_directory('.', 'last5.html')

# Serve the map_breakdown.html file
@app.route('/map_breakdown')
def serve_map_breakdown():
    return send_from_directory('.', 'map_breakdown.html')

@app.route('/map_breakdownl')
def serve_map_breakdown_lite():
    return send_from_directory('.', 'map_breakdown_lite.html')

# Serve the map_record_team.html file
@app.route('/map_record_team')
def serve_map_record_team():
    return send_from_directory('.', 'map_record_team.html')

@app.route('/map_editor')
def serve_map_editor():
    return send_from_directory('.', 'simple_maplist_editor.html')

# Serve the map_record_team.html file
@app.route('/stinger')
def serve_stinger():
    return send_from_directory('.', 'stinger.html')

# Serve the map_record_team.html file
@app.route('/stinger_gen')
def serve_stinger_generic():
    return send_from_directory('.', 'stinger_generic.html')

# Serve the map_record_team.html file
@app.route('/bans')
def serve_ban_ui():
    return send_from_directory('.', 'bans.html')

# Serve the map_record_team.html file
@app.route('/map_history')
def serve_map_history():
    return send_from_directory('.', 'map_history.html')

# API to get tournament data
@app.route('/tournament', methods=['GET'])
def get_tournament():
    tournament_data = load_tournament_data()
    return jsonify(tournament_data)

# API to get existing matches
@app.route('/matches', methods=['GET'])
def get_matches():
    match_data = load_match_data()
    return jsonify(match_data['game_history'])

@app.route('/matchesl', methods=['GET'])
def get_matchesl():
    match_data = load_matchl_data()
    return jsonify(match_data['game_history'])

@app.route('/smaplist', methods=['GET'])
def get_maps():
    map_data = load_smaplist_data()
    return jsonify(map_data['maps'])

# API to update match data
@app.route('/match', methods=['POST'])
def update_match():
    match_data = load_match_data()
    data = request.json

    # Update the match type and current map
    match_data['match_type'] = data['match_type']
    match_data['match_no'] = data['match_no']
    match_data['attack'] = data['attack']
    match_data['short_names'] = data['short_names']
    match_data['swap'] = data['swap']
    match_data['current_map'] = data['current_map']
    match_data['teams'] = data['teams']

    save_match_data(match_data)
    return jsonify({"message": "Match updated successfully!"})

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

# API to add match result
@app.route('/result', methods=['POST'])
def add_result():
    match_data = load_match_data()
    data = request.json

    # Initialize game_history if it's empty
    if 'game_history' not in match_data:
        match_data['game_history'] = []
        logging.info("match data sent had no game history")

    for index, match in enumerate(match_data['game_history']):
        if match['match_number'] == data['match_number']:
            # Overwrite existing match entry
            match_data['game_history'][index] = data
            save_match_data(match_data)
            return jsonify({"message": "Match entry updated successfully!"}), 200

    # Add the new result to the game history
    match_data['game_history'].append(data)
    save_match_data(match_data)
    return jsonify({"message": "Result added successfully!"})


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

# Add simple match entry
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

# API to get team name by ID
@app.route('/team/name/<int:team_id>', methods=['GET'])
def get_team_name(team_id):
    tournament_data = load_tournament_data()

    for index, team in enumerate(tournament_data['teams']):
        if team['id'] == team_id:
            return jsonify({"name": team['name']}), 200

# API to delete a match
@app.route('/match/<int:match_number>', methods=['DELETE'])
def delete_match(match_number):
    match_data = load_match_data()
    logging.info("deleting item " + str(match_number))

    if 'game_history' not in match_data:
        return jsonify({"message": "No matches found to delete."}), 404  # Return a 404 if no matches exist

    for index, match in enumerate(match_data['game_history']):
        logging.info("looking for " + str(match_number) + ", this is " + str(match['match_number']))
        if match['match_number'] == match_number:
            logging.info("item no " + str(match_number) + " exists, removing")
            match_data['game_history'].remove(match)

    save_match_data(match_data)
    return jsonify({"message": "Match deleted successfully!"})

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

@app.route('/map/<int:map_number>', methods=['DELETE'])
def delete_map(map_number):
    maplist_data = load_smaplist_data()
    logging.info("Maplist: " + str(maplist_data))
    logging.info("deleting item " + str(map_number))

    maplist_data['maps'].pop(map_number)

    save_smaplist_data(maplist_data)
    return jsonify({"message": "maps deleted successfully!"})

# Route to add a new map ban
@app.route('/add_map_ban', methods=['POST'])
def add_map_ban():
    map_id = request.json.get("id")
    map_name = request.json.get("name")
    team = request.json.get("team")
    banning_team_id = request.json.get("banning_team_id")
    match_data = load_match_data()
    
    # Append the new ban entry
    new_ban = {
        "id": map_id,
        "name": map_name,
        "team": team,
        "banning_team_id": banning_team_id
    }
    match_data.setdefault("map_bans", []).append(new_ban)
    save_match_data(match_data)
    return jsonify(success=True)

# Route to undo the last map ban
@app.route('/undo_map_ban', methods=['POST'])
def undo_map_ban():
    match_data = load_match_data()
    if "map_bans" in match_data and match_data["map_bans"]:
        match_data["map_bans"].pop()  # Remove the last entry
        save_match_data(match_data)
        return jsonify(success=True)
    return jsonify(success=False)

@app.route('/reset_map_ban', methods=['POST'])
def reset_map_ban():
    match_data = load_match_data()
    if "map_bans" in match_data and match_data["map_bans"]:
        match_data["map_bans"].clear()  # Remove the last entry
        save_match_data(match_data)
        return jsonify(success=True)
    return jsonify(success=False)

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

@app.route('/set-t-url', methods=['POST'])
def set_t_url():
    remote_t_url = request.form['remote_t_url']
    settings = load_settings()
    settings['remote_t_url'] = remote_t_url
    save_settings(settings)
    return redirect(url_for('serve_settings'))

@app.route('/set-m-url', methods=['POST'])
def set_m_url():
    remote_m_url = request.form['remote_m_url']
    settings = load_settings()
    settings['remote_m_url'] = remote_m_url
    save_settings(settings)
    return redirect(url_for('serve_settings'))

# Route to download JSON file from the remote URL
@app.route('/download-json', methods=['POST'])
def download_json():
    settings = load_settings()
    remote_t_url = settings.get('remote_t_url')
    remote_m_url = settings.get('remote_m_url')


    if not remote_t_url:
        return jsonify({"error": "Remote tournament URL is not set."}), 400
        
    if not remote_m_url:
        return jsonify({"error": "Remote matches URL is not set."}), 400
    
    try:
        response_t = requests.get(remote_t_url)
        response_t.raise_for_status()
        response_m = requests.get(remote_m_url)
        response_m.raise_for_status()        

        backup_json(TOURNAMENT_JSON_PATH)
        backup_json(MATCHES_JSON_PATH) 

        # Save the downloaded JSON file to static/downloaded.json
        with open(TOURNAMENT_JSON_PATH, 'w') as file:
            json.dump(response_t.json(), file, indent=0)

        with open(MATCHES_JSON_PATH, 'w') as file:
            json.dump(response_m.json(), file, indent=0)
        
        return jsonify({"message": "JSON files downloaded successfully!"}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download one or both JSON files: {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')
#    app.run(debug=True)



