import efficient_apriori as ea
import json
import os
MAX_FILES = 100 # Use this to cut the data set for quicker runtime.  Each file = 1000 playlists

def extract_playlists(path, search_track):
    global MAX_FILES
    track_loader = []
    extracted_playlists = []
    playlist_matches = []
    file_count = 0
    filenames = os.listdir(path) #From MPD
    for filename in sorted(filenames): #From MPD
        print(file_count)
        if file_count == MAX_FILES: #Stop at MAX_FILES
            break
        if filename.startswith("mpd.slice.") and filename.endswith(".json"): #From MPD
            fullpath = os.sep.join((path, filename)) #From MPD
            f = open(fullpath) #From MPD
            js = f.read() #From MPD
            f.close() #From MPD
            mpd_slice = json.loads(js) #From MPD
            for playlist in mpd_slice["playlists"]:
                for track in playlist["tracks"]:
                    if track["track_name"] == search_track: # If track = search track, save playlist
                        playlist_matches.append(playlist["tracks"])
                    else:
                        continue
            for playlist in playlist_matches:
                track_loader.clear()
                for track in playlist: #Skip over search track, don't need this in output
                    if track['track_name'] == search_track:
                        continue
                    else: #Build tuple from list of tracks
                        track_loader.append(track['track_name'])
                extracted_playlists.append(tuple(track_loader)) #save tuple to master list
        file_count += 1
    return extracted_playlists #return master list

def gen_itemset(playlists):
    itemsets = ea.itemsets_from_transactions(transactions= playlists, min_support=.2, max_length=5)
    return itemsets

def gen_rules(playlists):
    rules = ea.generate_rules_apriori(playlists, min_confidence= .2)
    return rules

def gen_rules_items(playlists):
    output = ea.apriori(playlists, min_support= .2, min_confidence= .2, max_length=5)
    return output



