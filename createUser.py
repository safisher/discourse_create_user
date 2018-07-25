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

usage: createUser.py [-h] [-c] -u username -e email [-n name]

Add a new user to Discourse forum. The user will be active and approved.

See: https://docs.discourse.org
"""

#------------------------------------------------------------------------------------------
# REQUIRED 
#------------------------------------------------------------------------------------------

DISCOURSE_API_KEY = 'PUT YOUR API KEY HERE'
DISCOURSE_API_USER = 'PUT YOUR API USERNAME HERE'
DISCOURSE_URL = 'PUT YOUR URL HERE'

#------------------------------------------------------------------------------------------
# INITIALIZATIONS
#------------------------------------------------------------------------------------------

import sys, os, string, argparse
from subprocess import Popen, PIPE

DEBUG = False
if DEBUG: print 'DEBUG MODE: ON'

VERSION = '0.1'

PASSWORD_CHARS = string.ascii_uppercase + string.digits + string.ascii_lowercase + "(" + ")"
PASSWORD_LENGTH = 20

argParser = argparse.ArgumentParser(version=VERSION, 
                                    description='Add user.',
                                    formatter_class=argparse.RawDescriptionHelpFormatter,
                                    epilog='' +
                                    'Add a new user to Discourse forum. The user will be active and approved.\n')
argParser.add_argument( '-c', dest='checkOnly', action='store_true', default=False,
                        help='Check username and email without creating a new account.' )
argParser.add_argument( '-u', dest='username', action='store', required=True, 
                        help='Unique username.' )
argParser.add_argument( '-e', dest='email', action='store', required=True, 
                        help='Unique email address.' )
argParser.add_argument( '-n', dest='fullname', action='store', required=False, default='',
                        help='User full name. If not present then username will be used.' )

clArgs = argParser.parse_args()
if DEBUG: print clArgs

# Flag if username or email exists
checkFlag = False

#------------------------------------------------------------------------------------------
# Get URL
#------------------------------------------------------------------------------------------

def runCommand(cmd):
    if DEBUG: print cmd

    # shell=True should be safe here since we're controlling the arguments
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    output, err = p.communicate()

    # if return code not 0 then curl failed
    if p.returncode != 0:
        sys.stderr.write('ERROR: ' + err + '\n')
        sys.exit(0)

    if DEBUG: print output

    return output

#------------------------------------------------------------------------------------------
# Check if email is unique
#------------------------------------------------------------------------------------------

def checkEmail():
    global checkFlag

    args = 'email=' + clArgs.email
    args += '&api_key=' + DISCOURSE_API_KEY
    args += '&api_username=' + DISCOURSE_API_USER
    
    args = '-s -X GET "' + DISCOURSE_URL + '/admin/users/list/all.json?' + args + '" ' 
    cmd = 'curl ' + args
    
    output = runCommand(cmd)    

    if not output == "[]" :
        user = output.split(",")[1].split(":")[1]
        sys.stderr.write('ERROR: Email "' + clArgs.email + '" already exists under account ' + user + ' for new user "' + clArgs.username + '".\n')
        checkFlag = True

#------------------------------------------------------------------------------------------
# Check if username is unique
#------------------------------------------------------------------------------------------

def checkUsername():
    global checkFlag

    args = clArgs.username + '.json'
    args += '?api_key=' + DISCOURSE_API_KEY
    args += '&api_username=' + DISCOURSE_API_USER
    args = '-s -X GET "' + DISCOURSE_URL + '/users/' + args + '" ' 
    cmd = 'curl ' + args
    
    output = runCommand(cmd)

    if '"error_type":"not_found"' not in output:
        # we've already tested the username and email so this should never fail
        sys.stderr.write('ERROR: User "' + clArgs.username + '" already exists.\n')
        checkFlag = True

#------------------------------------------------------------------------------------------
# Add user
#------------------------------------------------------------------------------------------

def addUser():
    # use username as the account name if a full name isn't provided
    fullname = clArgs.fullname
    if not fullname:
        fullname = clArgs.username
    
    # generate a random password for the account
    password = ""
    i = PASSWORD_LENGTH
    while i > 0:
        password += PASSWORD_CHARS[ord(os.urandom(1)) % len(PASSWORD_CHARS)]
        i -= 1

    # the new user will be approved and active.
    args = 'approved=true'
    args += '&active=true'
    args += '&name=' + fullname
    args += '&username=' + clArgs.username
    args += '&email=' + clArgs.email
    args += '&password=' + password
    args += '&api_key=' + DISCOURSE_API_KEY
    args += '&api_username=' + DISCOURSE_API_USER
    
    args = '-s -X POST --data "' + args + '" ' + DISCOURSE_URL + '/users'
    cmd = 'curl ' + args

    output = runCommand(cmd)

    if '"success":true' not in output:
        sys.stderr.write('ERROR: creating user.\n' + output + '\n')
        sys.exit(0)
    
# ------------------------------------------------------------------------------------------
# Run program
# ------------------------------------------------------------------------------------------

checkUsername()
checkEmail()

# allow both email and username checks to complete before exiting program
if checkFlag:
    sys.exit(0)

# if we got this far then we have a unique username and email address, so go ahead and add user.
if clArgs.checkOnly:
    print 'Unique username and email:', clArgs.username, clArgs.email
    
else:
    # if we got this far then we can add the user
    addUser()
    print "User added:", clArgs.username



#------------------------------------------------------------------------------------------
# EXAMPLE USER-ADD OUTPUT
#
# SUCCESS:
#     {"success":true,
#      "active":true,
#      "message":"Thanks for signing up.",
#      "user_id":1388}
#
# FAIL - duplicate email:
#     {"success":false,
#      "message":"Primary email has already been taken",
#      "errors":{"email":["has already been taken"]},
#      "values":{"name":"Test User",
#      "username":"test.user0",
#      "email":"test@gmail.com"},
#      "is_developer":false}
#
# FAIL - duplicate username:
#     {"success":false,
#      "message":"Username must be unique",
#      "errors":{"username":["must be unique"]},
#      "values":{"name":"Test User",
#                "username":"test.user",
#                "email":"test@gmail.com"},
#      "is_developer":false}
#
# FAIL - duplicate email & username:
#     {"success":false,
#      "message":"Username must be unique\nPrimary email has already been taken",
#      "errors":{"username":["must be unique"],
#                "email":["has already been taken"]},
#      "values":{"name":"Test User",
#                "username":"test.user",
#                "email":"test@gmail.com"},
#      "is_developer":false}
# ------------------------------------------------------------------------------------------

