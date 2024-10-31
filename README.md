This is a project of custom extensible stream overlays for casting Unreal Tournament events, although it can be easily used for other games. Core of the project is Flask python app that is used to control the overlays and doubles as the webserver that serves the overlays. Note that this project was initially made for an AS cup, so the way it works may be quite specific and not generic enough for other modes. These overlays are currently won't do well duels or TDM games.

Main goals for this project were:
- Create high-quality overlays that are easy to control via UI
- Allow control from a secondary device in the same local network (e.g. phone or a tablet) to reduce the need to switching from game window
- For big tournaments and cups use stored data to display extended stats for better insights and team records. Currently this is done via json, however can be just as easily set up to update manually from the Google Sheets via Google Cloud API.

**Installation:**
- Download and put in the folder of your choice
- Install python 3.8 if you don't have it installed
- Install dependencies from requirements.txt (navigate to the folder with the file and run "pip install -r requirements.txt")

To use run the updater_v3.py script, this will start the Flask server.
To open control web-interface, go open http://localhost:5000 in your browser

**Key principes:**
- Both scoreboard control pages only save data when you choose to do so. Make the changes and click "update match" to save the changes. Overlay will pick those up in a couple of seconds.
- If this is a series of matches, save the current values of all fields with "add result" button. If you made a mistake, just correct the wrong field and press "add result" again. If you need to delete the entry, you can do it from the list at the bottom of the control page
- 

**URLs for overlays:**
- http://localhost:5000/scoreboard - this is a tournament version of scoreboard that has more limited controls, e.g. max score is 4 since this is designed for bo-3/5/7 matches and uses a predefined team and map lists from tournament.json file.
- http://localhost:5000/sb_gen - more generic version of the scoreboard, "one-off" that lets you set any score or type in any map name. You can save time on typing by adding the maps using the one-off maplist updater that can be accessed via control web-interface
- http://localhost:5000/lastv - tournament version of last 5 game results. Uses match history from matches.json file add "?t=0" to the URL to get team A stats and "?t=1" for team B stats.
- http://localhost:5000/map_breakdown - shows the results of previous games in currently played series. This is a tournament version, that relies on predefined maplist from tournament.json file with links to screenshots.
- http://localhost:5000/map_breakdownl - one-off version that shows the text list of the maps and their scores.
- http://localhost:5000/stinger - this is a stinger transition for OBS. Duration is 3s, shows score for games after the first. For OBS you'll need this plugin to be able to use it: https://obsproject.com/forum/resources/browser-transition.1653/
- http://localhost:5000/stinger_gen - non-tournament version of the stinger
- http://localhost:5000/bans - map ban UI for the tournaments, uses maplist from a predefined maplist from tournament.json file and match.json to determine already played maps and store the banlist

Most of the functionality is intended for cups and doesn't really work without extra data in json files.
- matches.json - database of matches for the tournament, currently used to display last 5 matches for the specific team
- tournament.json - database of tournament maps with links to screenshots
- match.json - current match information: scores, team names, results of the previous games in the series, banned maps for tiebreakers.
- match_lite.json - same for the one-off scoreboard, currently doesn't support bans
- simple_maplist.json - simple list of maps for one-off scoreboard that can be edited through web-interface

Notes for scoreboard control pages:
- Event name for both scoreboards can be set under "Base scoreboard settings"
- "short names" on tourney scoreboard control will remove "Team " from the beginning of the team names if there is one to save space.
- Tourney scoreboard swaps the colors for even games, because teams alternate who attacks first and in UT2004 Red team will always be the one attacking first. Set "Team on Attack" to "Non-AS mode" to stop this.
- Win Type  on tourney scoreboard control is specifically to track type of win in AS. This scoreboard is not well tailored for other modes now
- Team on Attack controls the "Currently attacking" block under the team's name for AS rounds. Select "non-AS mode" and click "update match" to hide it on both teams
- For the one-off scoreboard set match type to "Best of 0" to hide the "GAME X OF Y" block at the top
- Update Tourney data option  be ignored, this option if for other streamers of the AS Cup to download the updated tournament and matches .json files from the URLs provided in the Settings.

