#!/usr/bin/env python3

# Usage: photolib.py SOURCE DESTINATION
#
# Where SOURCE is the bundle directory of the photo library and DESTINATION
# is a directory you want the results to go in. I use a bunch of text file
# append operations in here, so make sure you delete the destination
# directory if you want to re-run it; the image files will happily get
# overwritten, but you'll end up with confusing or duplicated indices.

import os
import plistlib
import shutil
import sys

# thanks StackOverflow1
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
# meaningful semantic information for us. Skip 'em so they don't
# end up in the albums index.
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
for album in plist["List of Albums"]:
    name = album["AlbumName"]
    if name in skipAlbums:
        continue

    albumlist = open(os.path.join(dest, "albums.txt"), "a")
    print(name, file=albumlist)
    for key in album["KeyList"]:
        pic = plist["Master Image List"][key]
        path = remove_prefix(pic["ImagePath"], path_prefix)
        print(" ", path, file=albumlist)
    albumlist.close()

# Copy pictures over
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

    # write captions and comments to the index
    i = open(os.path.join(dstdir, "index.txt"), "a")
    print(filename, file=i)
    if pic["Caption"]:
        print(" ", pic["Caption"], file=i)
    if pic["Comment"]:
        print(" ", pic["Comment"], file=i)
    print("", file=i)
    i.close()

