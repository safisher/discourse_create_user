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

usage: createUser.py [-h] [-c] [-n name] -u username -e email -k api_key -a api_user -w base_url

Add a new user to Discourse forum. The user will be active and approved. The program returns an exit code of 1 if the username or email exists and an exit code of 2 on error.

See: https://docs.discourse.org
"""

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
        sys.exit(2)

    if DEBUG: print output

    return output

#------------------------------------------------------------------------------------------
# Check if email and/or username is unique
#------------------------------------------------------------------------------------------

def emailExists(email, username, apiKey, apiUser, url):
    args = 'email=' + email
    args += '&api_key=' + apiKey
    args += '&api_username=' + apiUser
    
    args = '-s -X GET "' + url + '/admin/users/list/all.json?' + args + '" ' 
    cmd = 'curl ' + args
    
    output = runCommand(cmd)    

    if not output == "[]" :
        # email exists
        existingUser = output.split(",")[1].split(":")[1].replace('"', '')
        if existingUser != username:
            sys.stderr.write('ERROR: Email "' + email + '" already exists under username ' + existingUser + ', not username "' + username + '".\n')
        return True

    return False

def usernameExists(username, apiKey, apiUser, url):
    args = username + '.json'
    args += '?api_key=' + apiKey
    args += '&api_username=' + apiUser
    args = '-s -X GET "' + url + '/users/' + args + '" ' 
    cmd = 'curl ' + args
    
    output = runCommand(cmd)

    if '"error_type":"not_found"' not in output:
        # username exists
        return True

    return False

def isExisting(email, username, apiKey, apiUser, url):
    # do both email and username checks before exiting program
    usernameFlag = usernameExists(username, apiKey, apiUser, url)
    emailFlag = emailExists(email, username, apiKey, apiUser, url)
    if (usernameFlag and emailFlag):
        sys.stderr.write('ERROR: User "' + username + '" and email "' + email + '" already exist.\n')
        return True
    elif usernameFlag:
        sys.stderr.write('ERROR: User "' + username + '" already exist.\n')
        return True
    elif emailFlag:
        # we already output the error in emailExists()
        return True
    return False

#------------------------------------------------------------------------------------------
# Add user
#------------------------------------------------------------------------------------------

def addUser(fullname, email, username, apiKey, apiUser, url):
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
    args += '&username=' + username
    args += '&email=' + email
    args += '&password=' + password
    args += '&api_key=' + apiKey
    args += '&api_username=' + apiUser
    
    cmd = 'curl -s -X POST --data "' + args + '" ' + url + '/users'
    output = runCommand(cmd)

    if '"success":true' not in output:
        # we've already tested the username and email so this should never fail
        sys.stderr.write('ERROR: creating user.\n' + output + '\n')
        sys.exit(2)
    
# ------------------------------------------------------------------------------------------
# Run program
# ------------------------------------------------------------------------------------------

# allow for this file to be loaded into another Python script
if __name__ == '__main__':
    argParser = argparse.ArgumentParser(version=VERSION, 
                                        description='Add user.',
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog='' +
                                        'Add a new user to Discourse forum. The user will be active and approved. The program returns an exit code of 1 if the username or email exists and an exit code of 2 on error.\n')
    argParser.add_argument( '-c', dest='checkOnly', action='store_true', default=False,
                            help='Check username and email without creating a new account.' )
    argParser.add_argument( '-n', dest='fullname', action='store', required=False, default='',
                            help='User full name. If not present then username will be used.' )
    argParser.add_argument( '-u', dest='username', action='store', required=True, 
                            help='Unique username.' )
    argParser.add_argument( '-e', dest='email', action='store', required=True, 
                            help='Unique email address.' )
    argParser.add_argument( '-k', dest='apiKey', action='store', required=True, 
                            help='API Key.' )
    argParser.add_argument( '-a', dest='apiUser', action='store', required=True, 
                            help='API user.' )
    argParser.add_argument( '-w', dest='url', action='store', required=True, 
                            help='Discourse base URL (e.g. https://discourse.org).' )
    
    clArgs = argParser.parse_args()
    if DEBUG: print clArgs
    
    if isExisting(clArgs.email, clArgs.username, clArgs.apiKey, clArgs.apiUser, clArgs.url):
        sys.exit(1)
        
    # if we got this far then we have a unique username and email address, so go ahead and add user, if relevant.
    if clArgs.checkOnly:
        print 'Unique username and email:', clArgs.username, clArgs.email
    
    else:
        # if we got this far then we can add the user

        # use username as the account name if a full name isn't provided
        fullname = clArgs.fullname
        if not fullname:
            fullname = clArgs.username

        addUser(fullname, clArgs.email, clArgs.username, clArgs.apiKey, clArgs.apiUser, clArgs.url)
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

