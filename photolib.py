#!/usr/bin/env python3

import os
import plistlib
import shutil
import sys

# thanks StackOverflow!
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

# parameters to better names
source = sys.argv[1]
dest = sys.argv[2]

# output directory
if not os.path.exists(dest):
    os.makedirs(dest)

# load the album XML
f = open(os.path.join(source, "AlbumData.xml"), "rb")
plist = plistlib.load(f)

# These are default/builtin iPhoto album names that don't contain
# meaningful information for us. Skip 'em so they don't end up in
# the albums index.
skipAlbums = [
    "Photos",
    "Last 12 Months",
    "Last Import",
    "Flagged"
]

# iPhoto stores images with full pathnames, which is meaningless
# if the album is ever moved, but handily stores what it thinks
# the root directory of the album is. Bizarre.
path_prefix = plist["Archive Path"] + os.sep

# Album list and file paths out to the 'albums.txt' file
d = {}
for album in plist["List of Albums"]:
    name = album["AlbumName"]
    if name in skipAlbums:
        continue

    d[name] = []
    for key in album["KeyList"]:
        pic = plist["Master Image List"][key]
        path = remove_prefix(pic["ImagePath"], path_prefix)
        d[name].append(path)

f = open(os.path.join(dest, "albums.txt"), "w")
for key in sorted(d.keys()):
    print(key, file=f)
    for item in sorted(d[key]):
        print(" ", item, file=f)
    print("", file=f)
f.close()

# Copy pictures over
i = {}
for pic in plist["Master Image List"].values():
    path = remove_prefix(pic["ImagePath"], path_prefix)

    imagesrc = os.path.join(source, path)

    # A bunch of the pictures in the master image list appear to be
    # duplicated, and a swath of them had broken pathnames. I just 
    # skip them here, since it doesn't look like they matter, but
    # uncomment this print to find things if you can't figure out
    # why something important vanished/wasn't copied.
    if not os.path.exists(imagesrc):
        #print("Not found:", path)
        continue

    # pathname wrangling
    imagedst = os.path.join(dest, path)
    dstdir = os.path.dirname(imagedst)
    filename = os.path.basename(imagedst)
    
    # copy the file
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)

    shutil.copyfile(imagesrc, imagedst)

    # save captions and comments to the index table
    d = os.path.dirname(path)
    if not d in i.keys():
        i[d] = {}
    i[d][filename] = {}
    i[d][filename]["Caption"] = pic["Caption"]
    i[d][filename]["Comment"] = pic["Comment"]

# write out indices
for d in i.keys():
    f = open(os.path.join(dest, d, "index.txt"), "w")
    index = i[d]
    for filename in sorted(index.keys()):
        print(filename, file=f)
        caption = index[filename]["Caption"]
        comment = index[filename]["Comment"]
        if caption:
            print(" ", caption, file=f)
        if comment:
            print(" ", comment, file=f)
        print("", file=f)
    f.close()
