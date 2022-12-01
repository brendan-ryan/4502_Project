import csv
import efficient_apriori as ea
import json
import os
MAX_FILES = 50 # Use this to cut the data set for quicker runtime.  Each file = 1000 playlists
OUTPUT_COUNT = 1

# Usage, run process_playlists_single_seed or process playlist and provide relevant pathways

def create_submission(data_path, challenge_path):
    final_playlists = [['team_info', 'CU Boulder Data-Mining', 'chris.lescinskas@gmail.com']]
    dummy_playlist0 = gen_dummy_playlist_set0()
    playlist_loader = []
    pids = []
    for i in range(9):
        print("Len final: ",len( final_playlists))
        pids.clear()
        print("Seed num: ", i)
        seeds, pids = read_seed_playlists("./Challenge_data", i)
        seed_count = 0
        if i == 0:
            for i in range(1000):
                playlist_loader.clear()
                playlist_loader.append(pids[i])
                for item in dummy_playlist0:
                    playlist_loader.append(item)

                final_playlists.append(playlist_loader)
            print(final_playlists)
        elif i != 2 and i != 0:
            for i in range(1000):
                print("Dummy playlist #: ", i)
                playlist_loader.clear()
                dummy_playlist = gen_dummy_playlist(seeds, seed_count)
                playlist_loader.append(pids[i])
                seed_count+=1
                for item in dummy_playlist:
                    playlist_loader.append(item)
                final_playlists.append(playlist_loader)
        elif i == 2:
            mined_playlists = process_playlists_single_seed(data_path, challenge_path, i)
            for item in mined_playlists:
                final_playlists.append(item)
    convert_csv(final_playlists)

def process_playlists_single_seed(data_path, challenge_path, seed_num):  # Run on a single challenge dataset
    return_playlists = []
    track_loader = []
    playlist_count = 0
    seeds, pid_set = read_seed_playlists(challenge_path, seed_num) # extract seed playlists and IDs
    for playlist in seeds:
        sensitivity_offset = 0
        file_offset = 0
        track_loader.clear()
        track_loader.append(pid_set[playlist_count])
        print("Mining for playlist number: ", playlist_count)  # print progress
        while(len(track_loader) < 501):
            length_begin = len(track_loader)
            for song in playlist:

                if(len(track_loader) == 501):
                    break
                print("Number of songs in generated playlist: ", len(track_loader) - 1)
                MPD_playlists = extract_playlists(data_path, song, file_offset)  # extract playlist matches
                cands = try_support(MPD_playlists, sensitivity_offset)  # run a priori until matches found

                try:  # if no matches found, skip
                    extraxted_cands = extract_cands(cands)
                except IndexError:
                    break

                for song in extraxted_cands:  # add top cand set to playlist, skip any tracks already added
                    if len(track_loader) >= 501:
                        break
                    if song not in track_loader:
                        track_loader.append(song)
            if length_begin == len(track_loader):
                file_offset +=MAX_FILES
            sensitivity_offset +=1
        return_playlists.append(tuple(track_loader))  # final set of playlists
        print("completed playlist:")
        print(track_loader)
        playlist_count += 1
    convert_csv(return_playlists)
    return return_playlists


def extract_playlists(path, search_track, file_offset):
    global MAX_FILES
    track_loader = []
    extracted_playlists = []
    playlist_matches = []
    playlist_count = 0
    file_count = 0
    filenames = os.listdir(path)  # From MPD
    for filename in sorted(filenames):  # from MPD
        if file_count == MAX_FILES + file_offset: # Stop at MAX_FILES
            break
        if file_count < file_offset:
            file_count += 1
            continue
        elif filename.startswith("mpd.slice.") and filename.endswith(".json"):  # From MPD
            fullpath = os.sep.join((path, filename))  # From MPD
            f = open(fullpath)  # From MPD
            js = f.read()  # From MPD
            f.close()  # From MPD
            mpd_slice = json.loads(js)  # From MPD
            for playlist in mpd_slice["playlists"]:
                #if playlist_count == 100:
                    #break
                for track in playlist["tracks"]:
                    if track["track_uri"] == search_track: # If track = search track, save playlist
                        playlist_count += 1
                        playlist_matches.append(playlist["tracks"])
                    else:
                        continue

            for playlist in playlist_matches:
                extracted_playlist_max_size = 0
                track_loader.clear()
                for track in playlist:  # Skip over search track, don't need this in output
                    if track['track_uri'] == search_track:
                        continue
                    #if extracted_playlist_max_size == 75:
                        #break
                    else:  # Build tuple from list of tracks
                        track_loader.append(track['track_uri'])
                        extracted_playlist_max_size += 1
                extracted_playlists.append(tuple(track_loader))  # save tuple to master list
        file_count += 1
    print("Playlists analyzed for song: ", search_track, playlist_count)
    return extracted_playlists  # return master list


def gen_itemset(playlists, support):
    itemsets = ea.itemsets_from_transactions(transactions= playlists, min_support=support, max_length=2 )
    return itemsets


def gen_rules(playlists):  # NOT IN USE
    rules = ea.generate_rules_apriori(playlists, min_confidence= .1)
    return rules


def gen_rules_items(playlists):  # NOT IN USE
    output = ea.apriori(playlists, min_support=.2, min_confidence=.2, max_length=3)
    return output


def read_seed_playlists(path, seed_num):  # seed_num is Challenge # from challenge data set
    filename = os.listdir(path)
    pid_set = [] # playlist IDs to be included in output
    start, end, counter = 0, 0, 0
    return_playlists, tuple_loader = [], []
    for file in filename:
        if file == 'challenge_set.json':
            full_path = os.sep.join((path, file))
            f = open(full_path)
            js = f.read()
            f.close()
            seeds = json.loads(js)
            if seed_num == 0:
                end = 999
                for playlist in seeds["playlists"]:

                    if counter > end:
                        break
                    else:
                        pid_set.append(playlist["pid"])
                        for track in playlist["tracks"]:
                            tuple_loader.append(track["track_name"])
                        return_playlists.append(tuple(tuple_loader))
                        counter += 1
            else:  # offset to pull challenge seeds
                start = (seed_num*1000)
                end = ((seed_num+1)*1000)-1

                for playlist in seeds["playlists"]:

                    tuple_loader.clear()
                    if counter < start:
                        counter +=1
                        continue
                    elif counter > end:
                        break
                    else:
                        pid_set.append(playlist["pid"])
                        for track in playlist["tracks"]:
                            tuple_loader.append(track["track_uri"])
                        return_playlists.append(tuple(tuple_loader))
                        counter += 1
    return return_playlists, pid_set


def try_support(playlists, offset): # try different support until a candidate set is found
    try:
        cand = gen_itemset(playlists, (.10/(offset+1)))
    except IndexError:
        return []
    return cand


def find_top_cand(cand):  # pull out top cand from candidate set NOT IN USE
    sets = cand[0]
    print(sets)
    keys = sorted(cand[0].keys())
    max_set = keys[-1]
    top_cands = sorted(sets[max_set].values())
    top_cand_val = top_cands[-1]
    for k,v in sets[max_set].items():
        if v == top_cand_val:
            return k

def extract_cands(cand):  # pull out top cand from candidate set
    return_cands = []
    sets = cand[0]
    for key in sets.values():
        for song_set in key.keys():
            for song in song_set:
                if song not in return_cands:
                    return_cands.append(song)
    return return_cands


def convert_csv(playlists):
    global OUTPUT_COUNT
    name = "Playlist" + str(OUTPUT_COUNT)+ ".csv"
    with open(name, 'w') as f:
        write = csv.writer(f)
        write.writerow(playlists)
    OUTPUT_COUNT += 1

def gen_dummy_playlist(seeds, seed_count):
    playlist_length = 0
    dummy_playlist = []
    filenames = os.listdir("./MPD_data")  # From MPD
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):  # From MPD
            fullpath = os.sep.join(("./MPD_data", filename))  # From MPD
            f = open(fullpath)  # From MPD
            js = f.read()  # From MPD
            f.close()  # From MPD
            mpd_slice = json.loads(js)  # From MPD
        for playlist in mpd_slice["playlists"]:
            for track in playlist["tracks"]:
                if len(dummy_playlist) == 500:
                    return dummy_playlist
                track_name = track["track_uri"]
                if track_name not in dummy_playlist and track_name not in seeds[seed_count]:
                    dummy_playlist.append(track_name)
                    playlist_length += 1

def gen_dummy_playlist_set0():
    playlist_length = 0
    dummy_playlist = []
    filenames = os.listdir("./MPD_data")  # From MPD
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):  # From MPD
            fullpath = os.sep.join(("./MPD_data", filename))  # From MPD
            f = open(fullpath)  # From MPD
            js = f.read()  # From MPD
            f.close()  # From MPD
            mpd_slice = json.loads(js)  # From MPD
        for playlist in mpd_slice["playlists"]:
            for track in playlist["tracks"]:
                if len(dummy_playlist) == 500:
                    return dummy_playlist
                track_name = track["track_uri"]
                print(len(dummy_playlist))
                if track_name not in dummy_playlist:
                    dummy_playlist.append(track_name)
                    playlist_length += 1




