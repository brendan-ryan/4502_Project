"""
    shows deep stats for the MPD

    usage:

        python deeper_stats.py path-to-mpd-data/

"""
#***************************************************************************************
#*    Title: deeper_stats.py
#*    Author: Unknown - Part of the AIcrowd public challenge
#*    Date: unkown
#*    Code version: unkown
#*    Availability: https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge/dataset_files
#*
#*    Title: NumPy.histogram() Method in Python
#*    Author: jeeteshgavande30
#*    Date: 16 Dec, 2021
#*    Code version: unkown
#*    Availability: https://www.geeksforgeeks.org/numpy-histogram-method-in-python/
#*
#*    Title: Find average of a list in python
#*    Author: Chinmoy Lenka
#*    Date: 08 July, 2022
#*    Code version: unkown
#*    Availability: https://www.geeksforgeeks.org/find-average-list-python/
#***************************************************************************************/




import sys
import json
import re
import collections
import os
import csv
from matplotlib import pyplot as plt
import numpy as np

total_playlists = 0
total_tracks = 0
tracks = set()
artists = set()
albums = set()
titles = set()
ntitles = set()
full_title_histogram = collections.Counter()
title_histogram = collections.Counter()
artist_histogram = collections.Counter()
track_histogram = collections.Counter()
track_len = collections.Counter()
track_lens =[]


quick = False
max_files_for_quick_processing = 50


def process_mpd(path):
    count = 0
    filenames = os.listdir(path)
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            process_info(mpd_slice["info"])
            for playlist in mpd_slice["playlists"]:
                process_playlist(playlist)
            count += 1

            if quick and count > max_files_for_quick_processing:
                break

    show_summary()
    #Counter_tracks(track_histogram)
    #print("Counter: ", Counter_tracks(track_histogram))
    #print("hist values: ", histogram_values(Counter_tracks(track_histogram)))



def show_summary():
    print()
    print("number of playlists", total_playlists)
    print("number of tracks", total_tracks)
    print("number of unique tracks", len(tracks))
    print("number of unique albums", len(albums))
    print("number of unique artists", len(artists))
    print("number of unique titles", len(titles))
    print("number of unique normalized titles", len(ntitles))
    print("avg playlist length", float(total_tracks) / total_playlists)
    print()
    print("full playlist titles")
    for title, count in full_title_histogram.most_common():
        print("%7d %s" % (count, title))
    print()

    print("top playlist titles")
    for title, count in title_histogram.most_common():
        print("%7d %s" % (count, title))
    print()

    print("top tracks")
    #count_tracker = []
    for track, count in track_histogram.most_common(20):
        #count_tracker.append(count)
        print("%7d, %s" % (count, track))
    #print("count_tracker: ", count_tracker)

##    print()
####    for track, count in 
##    print(track_len)

    print()
    #histo(track_lens)
    boxplot(track_lens)
    #print(track_lens)

    print("Track Length Stats")
    print(average(track_lens))
    print("Q1: ", Q1(track_lens))
    print("Median: ", median(track_lens))
    print("Q3: ", Q3(track_lens))

    print()
    print("top artists")
    for artist, count in artist_histogram.most_common(20):
        print("%7d %s" % (count, artist))


def normalize_name(name):
    name = name.lower()
    name = re.sub(r"[.,\/#!$%\^\*;:{}=\_`~()@]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def process_playlist(playlist):
    global total_playlists, total_tracks

    track_lens.append(playlist["num_tracks"])
    track_len[playlist["num_tracks"]] += 1
    total_playlists += 1
    # print playlist['playlist_id'], playlist['name']

    titles.add(playlist["name"])
    nname = normalize_name(playlist["name"])
    ntitles.add(nname)
    title_histogram[nname] += 1
    full_title_histogram[playlist["name"].lower()] += 1

    for track in playlist["tracks"]:
        total_tracks += 1
        albums.add(track["album_uri"])
        tracks.add(track["track_uri"])
        artists.add(track["artist_uri"])

        full_name = track["track_name"] + " by " + track["artist_name"]
        artist_histogram[track["artist_name"]] += 1
        track_histogram[full_name] += 1


def histo(track_lens):
    data = track_lens
    plt.hist(data, bins= [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    plt.show()
    #code source - https://www.geeksforgeeks.org/numpy-histogram-method-in-python/
    return 0

def boxplot(track_lens):
    data = track_lens
    plt.boxplot(data)
    plt.show()
    #code source - https://www.geeksforgeeks.org/numpy-histogram-method-in-python/
    return 0

def average(tracks):
    sum_of_list = 0
    for i in range(len(tracks)):
        sum_of_list += tracks[i]
    average = sum_of_list/len(tracks)
    #code source - https://www.geeksforgeeks.org/find-average-list-python/
    return float(average)

def Q1(tracks):
    values = sorted(tracks)
    #print("here", tracks)
    if isinstance(len(values)/4, int):
        return values[int((len(values)/4))]
    else:
        v1 = float(values[math.floor(len(values)/4)])
        v2 = float(values[math.ceil(len(values)/4)])
        return float((v1+v2)/2)
    return 0

def Q3(tracks):
    values = sorted(tracks)
    #print("here", tracks)
    if isinstance(len(values)/4*3, int):
        return values[int((len(values)/4*3))]
    else:
        v1 = float(values[math.floor(len(values)/4*3)])
        v2 = float(values[math.ceil(len(values)/4*3)])
        return float((v1+v2)/2)
    return 0

def median(tracks):
    values = sorted(tracks)
    if isinstance(len(values)/2, int):
        return values[int(len(values)/2)]
    else:
        v1 = float(values[math.floor(len(values)/2)])
        v2 = float(values[math.ceil(len(values)/2)])
        return float((v1+v2)/2)
    return 0

def process_info(info):
    for k, v in list(info.items()):
        print("%-20s %s" % (k + ":", v))
    print()

if __name__ == "__main__":
    quick = False
    path = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "--quick":
        quick = True
    process_mpd(path)
