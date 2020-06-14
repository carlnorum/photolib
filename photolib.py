#!/usr/bin/env python3

import os
import plistlib
import shutil
import sys
import argparse

def create_destination_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_album_info(path):
    with open(os.path.join(path, "AlbumData.xml"), "rb") as f:
        return plistlib.load(f)

# thanks StackOverflow!
def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text

def extract_info(source, dest, album_info):
    create_destination_dir(dest)

    # These are default/builtin iPhoto album names that don't contain
    # meaningful information for us. Skip 'em so they don't end up in
    # the albums index.
    skip_albums = [
        "Photos",
        "Last 12 Months",
        "Last Import",
        "Flagged"
    ]

    # iPhoto stores images with full pathnames, which is meaningless
    # if the album is ever moved, but handily stores what it thinks
    # the root directory of the album is. Bizarre.
    path_prefix = album_info["Archive Path"] + os.sep

    # Album list and file paths out to the 'albums.txt' file
    d = {}
    for album in album_info["List of Albums"]:
        name = album["AlbumName"]
        if name in skip_albums:
            continue

        d[name] = []
        for key in album["KeyList"]:
            pic = album_info["Master Image List"][key]
            path = remove_prefix(pic["ImagePath"], path_prefix)
            d[name].append(path)

    with open(os.path.join(dest, "albums.txt"), "w") as f:
        for key in sorted(d.keys()):
            print(key, file=f)
            for item in sorted(d[key]):
                print(" ", item, file=f)
            print("", file=f)

    # Copy pictures over
    i = {}
    for pic in album_info["Master Image List"].values():
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
        create_destination_dir(dstdir)

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
        with open(os.path.join(dest, d, "index.txt"), "w") as f:
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

def process_arguments(argv):
    """Returns processed arguments."""
    parser = argparse.ArgumentParser(
        description='Extract information and photos from ancient iPhoto libraries.')
    parser.add_argument('source', help='bundle directory of the photo library source')
    parser.add_argument('dest', help='directory you want the results to go in')
    args = parser.parse_args(argv)
    return args

def main(argv=None):
    args = process_arguments(argv)
    album_info = load_album_info(args.source)
    extract_info(args.source, args.dest, album_info)
    return 0

if __name__ == '__main__':
    status = main()
    sys.exit(status)
