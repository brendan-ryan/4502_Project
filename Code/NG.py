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
#***************************************************************************************/




import sys
import json
import re
import collections
import os
import csv
import matplotlib.pyplot as plt
##import numpy as np
import networkx as nx
import scipy as sp
import pylab

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
G = nx.Graph()


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
    #print(G.edges)
##    nx.draw(G)
##    plt.show()
    #G = nx.petersen_graph()
    print("GOING INTO NETWORK GRAPH.....")
    G.remove_edges_from(nx.selfloop_edges(G))
    nx.draw(G)
    pylab.show()
    print("Done")



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
        G.add_node(full_name)

    for track in playlist["tracks"]:
        N1 = track["track_name"] + " by " + track["artist_name"]
        for track in playlist["tracks"]:
            N2 = track["track_name"] + " by " + track["artist_name"]
            G.add_edge(N1, N2)


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
