#!/usr/bin/env python
#
# Funf: Open Sensing Framework
# Copyright (C) 2010-2011 Nadav Aharony, Wei Pan, Alex Pentland.
# Acknowledgments: Alan Gardner
# Contact: nadav@media.mit.edu
# 
# This file is part of Funf.
# 
# Funf is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
# 
# Funf is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with Funf. If not, see <http://www.gnu.org/licenses/>.
# 

'''Attempts to salvage as much data as possible from a corrupted file, by dumping its contents to a new db file.
'''
from optparse import OptionParser
import sqlite3
import shutil
import os

_default_extension = 'corrupted'

def backup_file(file_name, extension=None):
    extension = extension or _default_extension
    return file_name + '.' + extension



def salvage(db_file, extension=None):
    
    # Make sure the file exists so we don't create a new file
    with open(db_file, 'rb') as existing_file:
        pass
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA integrity_check")
    if cursor.next()[0] == 'ok':
        conn.close()
    else:
        print "%s is corrupted.  Attempting to salvage." % (db_file,)
        new_db_file = db_file + ".new"
        with sqlite3.connect(new_db_file) as new_conn:
            new_cursor = new_conn.cursor()
            try:
                dumped_file_info_table = False
                for line in conn.iterdump():
                    if 'file_info' in line:
                        dumped_file_info_table = True
                    new_cursor.execute(line)
            except sqlite3.DatabaseError as e:
                # Reached the end of valid data
                # Ensure that we have the file_info table
                if not dumped_file_info_table:
                    file_info_schema = cursor.execute("select sql from sqlite_master where type='table' and name='file_info'").fetchone()[0]
                    new_cursor.execute(file_info_schema)
                    file_info_data = cursor.execute("select * from file_info").fetchone()
                    param_slots = '(' + ', '.join(['?' for item in file_info_data]) + ')'
                    new_cursor.execute("insert into file_info values %s" % param_slots,  file_info_data )
            new_conn.commit()
        conn.close()
        
        backup_file_name = backup_file(db_file, extension)
        if not os.path.exists(backup_file_name):
            shutil.copy2(db_file, backup_file_name)
        shutil.move(new_db_file, db_file)


if __name__ == '__main__':
    usage = "%prog [options] [sqlite_file1.db [sqlite_file2.db...]]"
    description = "Attempts to salvage as much data as possible from a corrupted file, by starting a new file and dumping in the contents of the corrupted file."
    parser = OptionParser(usage="%s\n\n%s" % (usage, description))
    parser.add_option("-i", "--inplace", dest="extension", default=None,
                      help="The extension to rename the original file to.  Will not overwrite file if it already exists. Defaults to '%s'." % _default_extension,)
    (options, args) = parser.parse_args()
    for file_name in args:
        salvage(file_name, options.extension)