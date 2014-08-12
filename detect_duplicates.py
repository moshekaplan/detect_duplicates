#! /usr/bin/env python

"""
Script for detecting duplicate files on a hard disk
Files are considered to be duplicates if they have the same size and hash

Copyright (c) 2014, Moshe Kaplan
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import os
import time
import zlib
import os.path
import collections


def get_crc32(fname, blocksize=2**16):
    """Computes a CRC-32 checksum for a file"""

    with open(fname, 'rb') as fh:
        fhash = zlib.crc32('')

        data = fh.read(blocksize)
        while data:
            fhash = zlib.crc32(data, fhash)
            data = fh.read(blocksize)
        return fhash


class DupeEntry():
    def __init__(self, fhash, size, files):
        self.fhash = fhash
        self.size = size
        self.files = files

    def get_hash(self):
        return self.fhash

    def get_size(self):
        return self.size

    def get_files(self):
        return self.files


def enumerate_files(start_dirs):
    """Builds a dictionary that includes maps file sizes to file names"""
    # Speed optimization
    os_path_join = os.path.join
    os_path_getsize = os.path.getsize

    # The size will be the key, each entry will be a file
    all_files = collections.defaultdict(list)
    for start_dir in start_dirs:
        for dirpath, _, filenames in os.walk(os.path.abspath(start_dir)):
            for fname in filenames:
                fpath = os_path_join(dirpath, fname)
                size = os_path_getsize(fpath)
                all_files[size].append(fpath)
    return all_files


def find_duplicates(all_files):
    """Uses a dictionary created by `enumerate_files` to examine if files with
    the same size are the same"""

    # We'll consider a file to be a duplicate if it has the same size and hash
    # We do this by storing a dictionary of lists.

    all_dupes = []
    for fsize, files in all_files.iteritems():
        # There can't be any duplicates if there's only one file with that size
        if len(files) == 1:
            continue

        # Build a list of files with the same hash
        dupes = collections.defaultdict(list)
        for fname in files:
            fhash = get_crc32(fname)
            dupes[fhash].append(fname)

        for fhash, filelist in dupes.iteritems():
            # There can't be any duplicates if only one file has that hash
            if len(filelist) == 1:
                continue
            dupe = DupeEntry(fhash, fsize, filelist)
            all_dupes.append(dupe)
    return all_dupes


def find_and_print_dupes(paths):
    start_time = time.time()

    files = enumerate_files(paths)
    enumerate_time = time.time() - start_time

    dupes = find_duplicates(files)
    dupe_time = time.time() - enumerate_time - start_time

    print "enumerate_time", enumerate_time
    print "dupe_time", dupe_time

    print

    for dupe in dupes:
        print "*"*80
        for fname in dupe.get_files():
            print fname


def main():
    """Sample usage"""
    paths = ['Downloads', 'Desktop']
    find_and_print_dupes(paths)

if __name__ == '__main__':
    main()
