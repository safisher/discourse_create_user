# discourse_create_user
Create new users in Discourse

This is a stand-alone Python script that will add users to a Discourse forum using the Discourse API.

For help with the API see: https://docs.discourse.org

This is provided "as is". It was written for Python 2.7 and I have no idea if it will work with newer versions of Python. Use it at your own peril.

The program license can be found here: http://kim.bio.upenn.edu/software/LICENSE

**Usage**

createUser.py [-h] [-c] -u username -e email [-n name]

Example usage:
	./createUser.py -u test.user -e test@gmail.com -n "Test User"

The program will verify that the username and email address are unique before attempting to add the new user. You can use the -c option to just test for uniqueness without creating a new user.

The new user will be active and approved. This appears to happen without an email being sent, at least in my setup. New user accounts will be created with a random password. So users will need to use the password-reset ("YOUR-DISCOURSE-URL/password-reset") form to log in.

Note that you need to add your API Key, API User and URL at the top of the program before this will run (see the "Required" section at the top of the program).

**Other Info**

These threads might be helpful to anyone wishing to hack their own solution:
  https://meta.discourse.org/t/creating-user-via-api/36133
  https://meta.discourse.org/t/creating-active-users-via-the-api-gem/33133/36
  https://meta.discourse.org/t/creating-a-user-through-restful-users-api/9359

