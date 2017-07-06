#!/usr/bin/python


"""
Usage -


%(scriptName)s -s [-c char]
%(scriptName)s -s [-r char]
Get csv data from an input source--  stdin, a file, a Python string, a Python list, and read it into a Python list of lists of strings.

%(scriptName)s [-c char] -f csv_file_name
%(scriptName)s -s [-c char]
%(scriptName)s -s [-r char]
%(scriptName)s -s
%(scriptName)s -t csv_string
%(scriptName)s -l

-s = Read from stdin.
-t csv_string = Read from a csv_string.
-f csv_file = Read from a file of csv strings.
-l = Read from a Python list.
-c char = Comment char.  Ignore lines with this char in line char position 0.
-r char = Raw print char.  Print out lines with this char in line char position 0 but do not use these lines to aid in calculating column spacing.
Options -c and -r cannot be set to the same character.

Blank lines will be printed out and not ignored.

Fields with embedded commas must be double-quoted, not single-quoted:
'echo test1,"test2,200",test3 | %(scriptName)s -s  # good

But for stdin, you must quote the quotes to shield them from the shell:
'echo test1,\"test2,200\",test3 | %(scriptName)s -s  # good
'echo \'test1,"test2,200",test3\' | %(scriptName)s -s  # good

"""

import sys
import os
import re
import csv
import string
import getopt
from logging_wrappers import debug_option
import select

scriptName = os.path.basename(os.path.realpath(__file__))
scriptDir = os.path.dirname(os.path.realpath(__file__))

#=========================================================

try:
    debug
except NameError:
    # print "well, it WASN'T defined after all!"
    debug = False

#=========================================================

def get_csv(csv_input_source, list_of_csv_strings = [], csv_string = '', csv_file = '', comment_char = '', raw_print_char = ''):

    import io

    # list_of_csv_strings is a Python list of csv list strings.

    global debug

    max_num_columns = 0

    columnized_output = []
    list_of_lists = []

    if debug: print("Entering get_csv")
    if debug: print("csv_input_source = " + csv_input_source)
    if debug: print("csv_string = " + csv_string)

    if csv_input_source == 'string':
        # f = io.StringIO(unicode(csv_string))
        f = io.StringIO(csv_string)
        list_of_lists = csv.reader(f, delimiter=',')
        '''
        Alternate method not using StringIO:
        for row in csv.reader([csv_string]):
           csv_row_list = []
           for field in row:
              # print "field_csv = " + field
              csv_row_list.append(field)
           list_of_lists.append(csv_row_list)
        # print "len(list_of_lists) = " + len(list_of_lists)
        '''
    elif csv_input_source == 'list':
        # print "list_of_csv_strings = " + str(list_of_csv_strings)
        if len(list_of_csv_strings) == 0:
            print("ERROR: csv_input_source = 'list' but len(list_of_csv_strings) = 0.")
            sys.exit(3)
        else:
            if debug: print(scriptName + ": csv input from list_of_csv_strings")
            for row in list_of_csv_strings:
                # print "row = " + str(row)
                list_of_lists.append(row.split(','))

    elif csv_input_source == 'stdin':
        if debug: print(scriptName + ": csv input from stdin")
        reader = csv.reader(sys.stdin)
        list_of_lists = reader

    # elif csv_input_source == 'sys.stdin':
    #    if debug: print scriptName + ": csv input from sys.stdin"
    #    list_of_lists = sys.stdin

    elif csv_input_source == 'file':
        # lines = open( csv_input_source, 'r').read().splitlines()

        # csvfile = open( csv_input_source, 'r')
        # lines = csvfile.read().splitlines()

        # with open(csv_input_source, 'r') as f:
        #    lines = f.read().splitlines()

        if debug: print(scriptName + ": csv input from file")
        csvfile = open( csv_input_source, 'rb')
        reader = csv.reader( csvfile )
        list_of_lists = reader
    else:
        print("ERROR: Unexpected csv_input_source = " + csv_input_source)
        sys.exit(3)

    # if debug: print "len(list_of_lists) = " + str(len(list_of_lists))
    if debug: print("before for loop")
    filtered_list = []
    # if debug: print "len(list_of_lists) = " + str(len(list_of_lists))
    if debug: print("before for loop")

    for row in list_of_lists:
        # if debug: print "row = " + str(row)
        # print "row = " + str(row)
        if len(row) != 0:
            if len(row) > max_num_columns:
                max_num_columns = len(row)

            if comment_char != '':
                # if re.search('"^' + comment_char + '"', row):
                # if re.search('"^' + comment_char + '"', row):
                # if re.search("^" + comment_char, row):
                # if re.search('^\#', row[0]):
                if debug: print("comment_char = " + comment_char)
                if re.search('^'+comment_char, row[0]):
                    continue
        filtered_list.append(row)

    list_of_lists = filtered_list

    return 0, list_of_lists, max_num_columns


#========================================================

def usage():
    print(__doc__ % {'scriptName' : scriptName,})
    sys.exit(1)



#========================================================

if __name__ == '__main__':

    debug = debug_option()

    if len( sys.argv ) < 2 :
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:sh:r:f:lt", [])
    except getopt.GetoptError as err:
        usage()

    list_of_csv_strings = []
    csv_string = ''
    comment_char = ''
    raw_print_char = ''
    num_header_lines = 0
    input_source = ''
    arg = ''
    opt = ''
    for opt, arg in opts:
        # print "arg = " + arg
        if opt == '-h':
            num_header_lines = int(arg)
            continue
        if opt == '-f':
            input_source = 'file'
            continue
        if opt == '-s':
            input_source = 'stdin'
            print("Test stdin: ")
            continue
        if opt == '-c':
            comment_char = arg
            continue
        if opt == '-r':
            raw_print_char = arg
            continue
        if opt == '-l':
            input_source = 'list'
            list_of_csv_strings = [ "abc,def,hij", "123,456,789", "lmo,321,xyz" ]
            print("Test list: ", list_of_csv_strings)
            continue
        if opt == '-t':
            input_source = 'string'
            csv_string = 'abc, def,"hij,123",456,,,789, lmo,321,xyz'
            print("Test string: ", csv_string)
            continue

    if debug: print("len(sys.argv) = " + str(len(sys.argv)))
    if debug: print("arg last index = " + str(sys.argv.index(arg)))

    if raw_print_char == comment_char and comment_char != '':
        print("ERROR: raw_print_char and comment_char cannot be set to the same character.")
        sys.exit(3)

    # if arg != '' and (sys.argv.index(arg) + 1 < len(sys.argv)):
    #    input_source = sys.argv[-1]

    # elif select.select([sys.stdin,],[],[],0.0)[0]:
    #    input_source = 'stdin'
    #
    # else:
    #    # input_source = 'sys.stdin'
    #    input_source = 'stdin'

    if debug: print("opt = " + opt)
    if debug: print("comment_char = " + comment_char)
    if debug: print("sys.argv[-1] = " + sys.argv[-1])
    if debug: print("input_source = " + input_source)

    # rc, results = columnize_output(input_source, list_of_csv_strings, csv_string, comment_char, raw_print_char)
    # print "211: list_of_csv_strings = " + str(list_of_csv_strings)
    rc, results, max_cols = get_csv(input_source, list_of_csv_strings, csv_string, comment_char, raw_print_char)
    print("len(results) = " + str(len(results)))
    print("max_cols = " + str(max_cols))
    for row in results:
        print(row)
