#!/usr/bin/env python

# Copyright (c) 2018, Stephen Fisher and Junhyong Kim, University of
# Pennsylvania.  All Rights Reserved.
#
# You may not use this file except in compliance with the Kim Lab License
# located at
#
#     http://kim.bio.upenn.edu/software/LICENSE
#
# Unless required by applicable law or agreed to in writing, this
# software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied.  See the License
# for the specific language governing permissions and limitations
# under the License.

"""
by: S. Fisher, 2018

usage: importUsers.py [-h] [-c] -f tsv_file -k api_key -a api_user -w base_url

Import users from a tab-delimited file into a Discourse forum. The user will be active and approved.

See: https://docs.discourse.org
"""

#------------------------------------------------------------------------------------------
# INITIALIZATIONS
#------------------------------------------------------------------------------------------

import sys, os, string, argparse
from subprocess import Popen, PIPE

import createUser

DEBUG = False
if DEBUG: print 'DEBUG MODE: ON'

VERSION = '0.1'

argParser = argparse.ArgumentParser(version=VERSION, 
                                    description='Import users.',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog='' +
                                    'Import users from a tab-delimited file into a Discourse forum. The user will be active and approved.\n')
argParser.add_argument( '-c', dest='checkOnly', action='store_true', default=False,
                        help='Check usernames and emails without creating new accounts.' )
argParser.add_argument( '-f', dest='tsv_file', action='store', required=False, default='',
                        help='Tab delimited file containing users to be imported. One user per line in the format: "full name<tab>username<tab>email".' )
argParser.add_argument( '-k', dest='apiKey', action='store', required=True, 
                        help='API Key.' )
argParser.add_argument( '-a', dest='apiUser', action='store', required=True, 
                        help='API user.' )
argParser.add_argument( '-w', dest='url', action='store', required=True, 
                        help='Base URL for forum (e.g. https://discourse.org).' )

clArgs = argParser.parse_args()
if DEBUG: print clArgs

#------------------------------------------------------------------------------------------
# OPEN INPUT FILE
#------------------------------------------------------------------------------------------

# open input file
inFile = ''
try: 
    inFile = open(clArgs.tsv_file, 'r')
except: 
    sys.stderr.write('ERROR: Unable to load input file ' + clArgs.tsv_file + '\n')
    sys.exit(1)

#------------------------------------------------------------------------------------------
# Process users
#------------------------------------------------------------------------------------------

count = 0
numAdded = 0
numExisting = 0
while 1:
    line = inFile.readline().rstrip()
    if len(line) == 0:
        break

    count += 1
    
    newUser = line.split('\t')
    
    if (len(newUser) < 3) or (not newUser[1]) or (not newUser[2]):
        # the user is missing a username and/or email
        sys.stderr.write('ERROR: Invalid user: ' + line + '\n')
        continue
    
    fullname = newUser[0]
    username = newUser[1]
    email = newUser[2]
    
    if createUser.isExisting(email, username, clArgs.apiKey, clArgs.apiUser, clArgs.url):
        # the username and/or email exists so move on to next user
        numExisting += 1
        continue
        
    # if we got this far then we have a unique username and email address, so go ahead and add user, if relevant.
    if clArgs.checkOnly:
        print 'Unique username and email:', username, email
    
    else:
        # time to add the user

        # use username as the account name if a full name isn't provided
        if not fullname:
            fullname = username

        createUser.addUser(fullname, email, username, clArgs.apiKey, clArgs.apiUser, clArgs.url)
        print "User added:", username

        numAdded += 1


print "Processed users:", count
print "Number Added:", numAdded
print "Number Existing:", numExisting
