#!/usr/bin/env python3

"""
RatingSync synchronizes the ratings of your music collection across multiple platforms.
The program consists of a server application and a client application.
The server stores your global database of ratings for each mp3 file.
The client synchronizes updated ratings with the server.
Each rating will also contain a change date, so that the synchronization works well.

Author: Valentin Trifonov (and soon maybe some more people aswell).
"""

# imports n shit
import os
import sys
import re
import argparse
import time as timemodule
from mutagen.id3 import ID3

# reading tags
def read_tag(item):
    # maybe throw exeption if file is not an mp3 file?
    try:
        tag = ID3(item)
        rating = tag.getall('POPM')[0].rating
        if rating == 255:   return 5
        elif rating == 196: return 4
        elif rating == 128: return 3
        elif rating == 64:  return 2
        elif rating == 1:   return 1
        else:               return 0
    except:
        return 0

# parse arguments
parser = argparse.ArgumentParser(description="Start the Rating syncing client.")
parser.add_argument("-v", "--verbose", help="verbosity (print more about what is done)", action="store_true")
subparser = parser.add_subparsers()
# init using config file
conf_parser = subparser.add_parser("config", help="load settings per config file")
conf_parser.add_argument("--file", help="the path to the config file (Default: RatingSync.conf)", default="RatingSync.conf")
# init using arguments
arg_parser = subparser.add_parser("opt", help="initialize settings per options")
arg_parser.add_argument("--path", help="the path to the directory of your music collection", type=str, default=os.curdir)
arg_parser.add_argument("server", help="the server to connect to")
arg_parser.add_argument("--time", help="the time interval for syncing the database", type=int, default=60)
# parse args
args = parser.parse_args()
        
# init
verbose = args.verbose
if "file" in args:
    print("parsing %s (not implemented yet)" % args["file"])
    # TODO
    path = None
    server = None
    time = None
elif "server" in args:
    path = args.path
    server = args.server
    time = args.time
else:
    parser.print_help()
    sys.exit(1)

# implementation    
starttime = timemodule.time() # performance measuring

os.chdir(path)
music_files = {}
# Perform a DFS and put all the mp3 files in the list music_files
dfs_stack = [os.path.realpath(os.curdir)]
visited = []
while dfs_stack: # while not empty
    item = dfs_stack.pop()
    
    if item in visited: # make sure there are no cycles
        if verbose:
            print("searched file already: {}".format(item))
        continue
        
    visited.append(item)
    if os.path.isdir(item):
        if verbose:
            print("adding dir to searching list: {}".format(item))
            # push all child files to the stack
        new_dirs = [os.path.realpath(item + os.sep + c) for c in os.listdir(item)]
        dfs_stack.extend(new_dirs)
    elif os.path.isfile(item):
        if re.search(r".*\.mp3", item):
            rating = read_tag(item)
            if verbose:
                print("adding to music list ({}*): {}".format(rating, item))
            music_files[item] = rating
        elif verbose:
            print("not an mp3 file: {}".format(item))
    else:
        print("error, {} is neither a file nor a directory. exiting.".format(item))
        sys.exit(2)

elapsed = timemodule.time() - starttime

if verbose:
    print "elapsed time: {:.5f}s".format(elapsed)
    print "music files len", len(music_files)
    print "visited len", len(visited)

# first I will try a naive implementation using a dict, once that works I will optimize it and find a good data structure
