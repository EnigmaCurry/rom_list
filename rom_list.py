#!/bin/env python2
"""Creates a ROM list for a given directory that tries to remove duplicate copies, hacks, and alternate versions.

Basically, I want a list of the best version of each title.

Assumes the filenames are in GoodTools format.

How to copy the roms in the list from a larger directory of roms:

    rsync -av --files-from=roms.txt . /path/to/copy/to

"""

import sys
import os
import re
from collections import defaultdict
import operator

def scan_dir(directory, desired_country='U', desired_lang='Eng', exclude_countries=['J']):
    """Scan a directory of roms, sort by title, and score each one by based on it's attributes.
    
    Scoring:
    Has [!] tag = +100
    Desired country = +10
    [T-Lang] tag for desired language = +10
    [T-Lang] tag for undesired language = -50
    tagless = +5
    Has [b] bad tag = -100
    Has [h] hack tag = -50
    Has [p] pirate tag = -25
    """
    titles = defaultdict(dict) # title -> {filename: score}

    file_parts_re = re.compile('([^\(\[\]]*)(.*)')
    exclude_countries_re = re.compile('\(['+''.join(exclude_countries)+']\)')
    desired_country_re = re.compile('\('+desired_country+'\)')
    good_dump_re = re.compile('\[!\]')
    bad_dump_re = re.compile('\[b')
    hack_dump_re = re.compile('\[h')
    pirate_dump_re = re.compile('\[p')
    good_translation_re = re.compile('\[T[-+]'+desired_lang)
    bad_translation_re = re.compile('\[T[-+]')
    tags_re = re.compile('\[')
    
    # Just remove these entirely:
    filters = ['Hack)', '(PD)', 'BIOS']

    for file in os.listdir(directory):
        if exclude_countries_re.search(file):
            continue
        pass_filters = True
        for f in filters:
            if f in file:
                pass_filters = False
                break
        if not pass_filters:
            continue

        # Strip off the extension:
        fn = ".".join(file.split(".")[:-1])
        m = file_parts_re.match(fn)
        assert m, "file_parts_re couldn't match the filename: %s" % file
        title, tags = m.groups()
        title = title.strip()
        # Score the title based on its tags:
        score = 0
        if good_dump_re.search(tags):
            score += 100
        if desired_country_re.search(tags):
            score += 10

        if not tags_re.search(tags):
            score += 5

        if good_translation_re.search(tags):
            score += 5
        elif bad_translation_re.search(tags):
            score -= 50

        if bad_dump_re.search(tags):
            score -= 100
        if hack_dump_re.search(tags):
            score -= 50
        if pirate_dump_re.search(tags):
            score -= 25
        
        titles[title][file] = score

    # Pick a single ROM per title:
    roms = []
    for scores in titles.values():
        rom, score = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)[0]
        if score >= 0 :
            roms.append(rom)
    return sorted(roms)

def translate_files_83(directory):
    """Translate long filenames to 8.3 format, making sure not to overwrite a name already used"""
    translations_used = set([])
    translations = {} # old -> new
    for f in os.listdir(directory):
        fn = ".".join(f.split(".")[:-1])
        ext = f.split(".")[-1]
        fn = fn.replace(" ","_")
        fn = fn.replace(".","_")
        
        attempt = 0
        while True:
            if attempt == 0:
                new_fn = ("%s.%s" % (fn[:8], ext[:3])).upper()
            else:
                new_fn = ("%s%02d.%s" % (fn[:6],attempt,ext[:3])).upper()
            if new_fn in translations_used:
                attempt +=1 
                continue
            translations_used.add(new_fn)
            translations[f] = new_fn
            break

    return translations

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: rom_list.py scan|rename /your/roms/directory"
        sys.exit(1)

    oper = sys.argv[1]
    directory = sys.argv[2]
    if oper == 'scan':
        roms = scan_dir(directory)
        for rom in roms:
            print rom
    elif oper == 'rename':
        f = open(os.path.join(directory, 'gamelist.txt'), 'w')
        for old, new in [(k,v) for (k,v) in translate_files_83(directory).items()]:
            if old != 'gamelist.txt':
                f.write('%s\t%s\n' % (new, old))
                os.rename(os.path.join(directory, old), os.path.join(directory, new))
        f.close()


