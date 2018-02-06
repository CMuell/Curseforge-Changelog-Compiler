# Written by https://www.reddit.com/user/CJDAM/
# Written in Python 3

import urllib.request
import bs4
import re
from filecmp import dircmp
from googleapiclient.discovery import build


def google_search(term, api, cse, **kwargs):
    service = build('customsearch', 'v1', developerKey=api)
    result = service.cse().list(q=term, cx=cse, **kwargs).execute()
    return result['items']

# Create a Google Custom Search Engine here FIRST => https://cse.google.com/
# IMPORTANT!!! MUST SET 'SITES TO SEARCH' TO https://minecraft.curseforge.com/ OR THIS WILL NOT WORK

# GET GOOGLE PYTHON API KEY HERE => https://developers.google.com/api-client-library/python/guide/aaa_apikeys


# Google customsearch API key
api_key = ''
# Google customsearch ID (cx)
cse_id = ''
# Old modpack mods directory
path_old = ''
# New modpack mods directory
path_new = ''
# Eg => FTB Revelations - 1.4.0
modpack_name = ''

# Creates the changelog.html file and writes the changelog title
new_file = open('changelog.html', 'w')
new_file.write('<h1>{0} Changelog</h1>\n'.format(modpack_name))
new_file.write('<p>Written by /u/CJDAM<p>')
new_file.write('<br><br><br>')
new_file.close()

# Compares the two mod directories and returns unique files from the new version
dcmp = dircmp(path_old, path_new)
right_only = dcmp.right_only
# Separates the returned file names into individual strings
mod_array = str(right_only).split(',')

print('Working on it...\n')

# For each string in the mod_array list do the following:
for name in mod_array:
    # Defines search_term as the current file name
    search_term = name

    print('Getting ' + name + '\n')

    # Initializes a new google search using the file name, api_key, cse_id. Returns first search result
    new_search = google_search(name, api_key, cse_id, num=1)

    for search in new_search:
        # Retrieves the curseforge file link from the query
        res = search['link']
        # Opens the link and views the html
        response = urllib.request.urlopen(res)
        response_html = response.read()
        soup = bs4.BeautifulSoup(response_html, 'html.parser')
        # Searches for the 'logbox' class containing changelog information
        logbox = soup.find('div', class_='logbox')
        # Converts the retrieved information to a string
        logbox = str(logbox)
        # Some prettifying
        logbox = re.sub('<h1>', '<h4>', logbox)
        logbox = re.sub('</h1>', '</h4>', logbox)
        logbox = re.sub('<h2>', '<h3>', logbox)
        logbox = re.sub('</h2>', '<h3>', logbox)

        content = logbox

        # Opens changelog.html to append the retrieved changelog to EOF
        file_object = open('changelog.html', 'a')
        # Writes file name to changelog.html
        file_object.write('<div>')
        file_object.write('<h2>{0}</h2>\n'.format(name))
        file_object.write('<p>{0}</p>\n'.format(content))
        file_object.write('</div>')
        file_object.write('<br><br>')
        file_object.close()
