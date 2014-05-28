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

'''Merges data from a group of Funf sqlite files into one CSV file per table.
'''
import sqlite3
from optparse import OptionParser
import os.path
import time, logging
from dbsalvage import salvage

file_info_table = 'file_info'
data_table = 'data'

def merge(db_files=None, out_file=None, overwrite=False, attempt_salvage=True):
    logging.debug('merging')
    # Check that db_files are specified and exist
    if not db_files:
        db_files = [file for file in os.listdir(os.curdir) if file.endswith(".db") and not file.startswith("merged")]
        if not db_files: 
            raise Exception("Must specify at least one db file")
    nonexistent_files = [file for file in db_files if not os.path.exists(file)]
    if nonexistent_files:
        raise Exception("The following db files do not exist: %s" % nonexistent_files)
    
    # Use default filename if it doesn't ixist
    if not out_file:
        out_file = 'merged_%d.db' % int(time.time())
    
    if os.path.exists(out_file):
        if overwrite:
            os.remove(out_file)
        else:
            raise Exception("The file '%s' already exists." % out_file)
    
    out_conn = sqlite3.connect(out_file)
    out_conn.row_factory = sqlite3.Row
    out_cursor = out_conn.cursor()
    
    out_cursor.execute('create table data (id text, device text, probe text, timestamp long, value text)')
    logging.debug('merging2')
    
    for db_file in db_files:
        logging.debug('merging3')
        if attempt_salvage:
            salvage(db_file)
        logging.debug('merging3a')
        conn = sqlite3.connect(db_file)
        logging.debug('merging3b')
        conn.row_factory = sqlite3.Row
        logging.debug('merging4')
        cursor = conn.cursor()
        try: 
            logging.debug('merging5')
            cursor.execute("select * from %s" % file_info_table)
            logging.debug('merging6')
        except (sqlite3.OperationalError,sqlite3.DatabaseError):
            logging.debug("Unable to parse file: " + db_file)
            continue
        else:
            logging.debug('merging7')
            try:
                for row in cursor:
                    logging.debug('merging8')
                    id, name, device, uuid, created = row
            except IndexError:
                logging.debug("No file info exists in: " + db_file)
                continue
            logging.info("Processing %s" % db_file)
            cursor.execute("select * from %s" % data_table)
            for row in cursor:
                id, probe, timestamp, value = row
                new_row = (('%s-%d' % (uuid, id)), device, probe, timestamp, value)
                out_conn.execute("insert into data values (?, ?, ?, ?, ?)", new_row)
            out_conn.commit()
    out_cursor.close()


if __name__ == '__main__':
    usage = "%prog [options] [sqlite_file1.db [sqlite_file2.db...]]"
    description = "Merges many database files into one file."
    parser = OptionParser(usage="%s\n\n%s" % (usage, description))
    parser.add_option("-o", "--output", dest="file", default=None,
                      help="Filename to merge all files into.  Will not overwrite a file if it already exists.", metavar="FILE")
    (options, args) = parser.parse_args()
    try:
        merge(args, options.file)
    except Exception as e:
        import sys
        sys.exit("ERROR: " + str(e))