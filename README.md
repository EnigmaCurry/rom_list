This is tool I made a long time ago that helps me with my emulator rom
files. This figures out the "best" version of a rom from a huge
directory of roms with lots of duplicates.

To scan the rom directory and create a list of "best" versions:

    python rom_list scan /your/roms/directory > roms.txt

To copy those roms to another directory:

    rsync -av --files-from=roms.txt /your/roms/directory /your/new/directory

To rename roms to be compatible with DOS filesystems (super useful for Super UFO SNES cart):

    python rom_list rename /your/new/directory/to/rename

This will rename all roms to use an 8.3 file format, making sure to
not reuse the same name for different roms. Also outputs a new file
called gamelist.txt that you can use as a reference for which roms is
which.