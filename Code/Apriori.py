import csv
import efficient_apriori as ea
import json
import os
MAX_FILES = 5 # Use this to cut the data set for quicker runtime.  Each file = 1000 playlists
OUTPUT_COUNT = 1

# Usage, run process_playlists_single_seed or process playlist and provide relevant pathways


def process_playlists_single_seed(data_path, challenge_path, seed_num):  # Run on a single challenge dataset
    return_playlists = []
    track_loader = []
    playlist_count = 0
    seeds = read_seed_playlists(challenge_path, seed_num)  # extract seed playlists
    for playlist in seeds:
        print(playlist_count)  # print progress
        track_loader.clear()
        for song in playlist:
            MPD_playlists = extract_playlists(data_path, song)  # extract playlist matches
            cands = try_support(MPD_playlists)  # run a priori until matches found
            try:  # if no matches found, skip
                top_cand = find_top_cand(cands)
            except IndexError:
                break
            print("top cand of song:", song)
            print(top_cand)
            for song in top_cand:  # add top cand set to playlist, skip any tracks already added
                if song not in track_loader:
                    track_loader.append(song)
        return_playlists.append(tuple(track_loader))  # final set of playlists
        print("completed playlist:")
        print(track_loader)
        convert_csv(track_loader)
        playlist_count += 1
    return return_playlists


def process_playlists(data_path, challenge_path):  # run on full challenge dataset
    return_playlists = []
    track_loader = []
    for i in range(9):
        print("Seed num")
        print(i)
        seeds = read_seed_playlists(challenge_path, i)
        for playlist in seeds:
            track_loader.clear()
            for song in playlist:
                MPD_playlists = extract_playlists(data_path, song)
                cands = try_support(MPD_playlists)
                try:
                    top_cand = find_top_cand(cands)
                except IndexError:
                    break
                print("top cand")
                print(top_cand)
                for song in top_cand:
                    if song not in track_loader:
                        track_loader.append(song)
            return_playlists.append(tuple(track_loader))
            print("loader")
            print(track_loader)
            convert_csv(track_loader)
    return return_playlists


def extract_playlists(path, search_track):
    global MAX_FILES
    track_loader = []
    extracted_playlists = []
    playlist_matches = []
    file_count = 0
    filenames = os.listdir(path)  # From MPD
    for filename in sorted(filenames):  # from MPD
        if file_count == MAX_FILES: # Stop at MAX_FILES
            break
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):  # From MPD
            fullpath = os.sep.join((path, filename))  # From MPD
            f = open(fullpath)  # From MPD
            js = f.read()  # From MPD
            f.close()  # From MPD
            mpd_slice = json.loads(js)  # From MPD
            for playlist in mpd_slice["playlists"]:
                for track in playlist["tracks"]:
                    if track["track_name"] == search_track: # If track = search track, save playlist
                        playlist_matches.append(playlist["tracks"])
                    else:
                        continue
            for playlist in playlist_matches:
                track_loader.clear()
                for track in playlist:  # Skip over search track, don't need this in output
                    if track['track_name'] == search_track:
                        continue
                    else:  # Build tuple from list of tracks
                        track_loader.append(track['track_name'])
                extracted_playlists.append(tuple(track_loader))  # save tuple to master list
        file_count += 1
    return extracted_playlists  # return master list


def gen_itemset(playlists, support):
    itemsets = ea.itemsets_from_transactions(transactions= playlists, min_support=support, max_length=3 )
    return itemsets


def gen_rules(playlists):
    rules = ea.generate_rules_apriori(playlists, min_confidence= .1)
    return rules


def gen_rules_items(playlists):
    output = ea.apriori(playlists, min_support= .2, min_confidence= .2, max_length=5)
    return output


def read_seed_playlists(path, seed_num): #seed_num is Challenge # from challenge data set
    filename = os.listdir(path)
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
                        for track in playlist["tracks"]:
                            tuple_loader.append(track["track_name"])
                        return_playlists.append(tuple(tuple_loader))
                        counter += 1
            return return_playlists
    return


def try_support(playlists):
    for i in range(7):  # try different support until a candidate set is found
        try:
            cand = gen_itemset(playlists, (.35/(i+1)))
        except IndexError:
            continue
        if len(cand) > 2:
            break
    return cand


def find_top_cand(cand):  # pull out top cand from candidate set
    sets = cand[0]
    keys = sorted(cand[0].keys())
    max_set = keys[-1]
    top_cands = sorted(sets[max_set].values())
    top_cand_val = top_cands[-1]
    for k,v in sets[max_set].items():
        if v == top_cand_val:
            return k


def convert_csv(playlists):
    global OUTPUT_COUNT
    name = "Playlist" + str(OUTPUT_COUNT)
    with open(name, 'w') as f:
        write = csv.writer(f)
        write.writerow(playlists)
    OUTPUT_COUNT += 1

