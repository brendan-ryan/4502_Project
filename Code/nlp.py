import os
import json
import sys
from nltk import metrics, stem, tokenize
from nltk.metrics import edit_distance
from nltk import FreqDist

'''
    rap
    run
    dance

    https://streamhacker.com/2011/10/31/fuzzy-string-matching-python/
    Fuzzy String Matching

    https://www.nltk.org/install.html
    Installation Steps
    
    https://realpython.com/nltk-nlp-python/
    Natural Language Toolkit

    https://tedboy.github.io/nlps/generated/generated/nltk.edit_distance.html
    Levenshtein Distance

'''

final_playlists = []
search_term = "rap"
stemmer  = stem.PorterStemmer()
playlist_counter = 0

# First Call
def processPlaylistNames(playlist):
    # if playlist is within Levenshtein distance, add atrist and tracks to list
    playlist_counter = 0
    if (fuzzyMatch(playlist["name"], search_term)):
        # this will append all tracks in playlist
        playlist_counter = playlist_counter + 1
        for track in playlist["tracks"]:
            final_playlists.append((track["artist_name"], track["track_name"]))
    return playlist_counter

def normalize(s):
    # remove punctuation, remove white space, lower case
    words = tokenize.wordpunct_tokenize(s.lower().strip())
    return ' '.join([stemmer.stem(w) for w in words])

def fuzzyMatch(s1, s2, max_distance=1):
    # calculate the Levenshtein distance between playlist and search term
    return edit_distance(normalize(s1), normalize(s2)) <= max_distance

# Algorithm begins here
def processSlices(path):
    # open files and read json data
    spotify_playlists = []
    playlist_counter = 0
    filenames = os.listdir(path)
    for filename in sorted(filenames):
        if filename.startswith("mpd.slice.") and filename.endswith(".json"):
            fullpath = os.sep.join((path, filename))
            f = open(fullpath)
            js = f.read()
            f.close()
            mpd_slice = json.loads(js)
            # iterate through each playlist
            for playlist in mpd_slice["playlists"]:
                counter = processPlaylistNames(playlist)
                playlist_counter += counter
    frequency_dist = FreqDist(final_playlists)
    print(frequency_dist.most_common(10))
    print("\n\nTotal songs: ", len(final_playlists))
    print("\nTotal playlists: ", playlist_counter)

if __name__ == "__main__":
    path = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "--quick":
        quick = True
    processSlices(path)