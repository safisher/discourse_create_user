### Create new users in Discourse

This is a set of Python scripts that will add users to a Discourse forum using the Discourse API.

For help with the API see: https://docs.discourse.org

This is provided "as is". It was written for Python 2.7 and I have no idea if it will work with newer versions of Python. Use it at your own peril.

The program license can be found here: http://kim.bio.upenn.edu/software/LICENSE

***

### Usage

**Add a single user:**
<pre>
	createUser.py [-h] [-v] [-c] [-n FULLNAME] -u USERNAME -e EMAIL -k API_KEY -a API_USER -w URL
</pre>

**Example usage:**
<pre>
	createUser.py -n "Test User" -u test.user -e test@gmail.com -k yourAPIKey -a yourAPIUsername -w https://1.1.1.1
</pre>

The program will verify that the username and email address are unique before attempting to add the new user. You can use the -c option to just test for uniqueness without creating a new user.

The new user will be active and approved. This appears to happen without an email being sent, at least in my setup. New user accounts will be created with a random password. So users will need to use the password-reset ("YOUR-DISCOURSE-URL/password-reset") form to log in.

**Add a list of user from a tab delimited file:**
<pre>
	importUsers.py [-h] [-v] [-c] [-f TSV_FILE] -k APIKEY -a APIUSER -w URL
</pre>

**Example usage:**
<pre>
	./importUsers.py -c -f users.tsv -k yourAPIKey -a yourAPIUsername -w https://1.1.1.1
</pre>

**The tab delimited file should be formatted as follows with one user per line. **
<pre>
	full name \t username \t email
</pre>

**Examples:**
<pre>
	Test User	test.user	test@gmail.com
		no_full_name	no_full_name@gmail.com
	Another User	another.user	testing@gmail.com
<pre>

***

### Other Info

These threads might be helpful to anyone wishing to hack their own solution:

https://meta.discourse.org/t/creating-user-via-api/36133

https://meta.discourse.org/t/creating-active-users-via-the-api-gem/33133/36

https://meta.discourse.org/t/creating-a-user-through-restful-users-api/9359

Here is another solution using Bash

https://github.com/pfaffman/discourse-user-creator/blob/master/create-user


