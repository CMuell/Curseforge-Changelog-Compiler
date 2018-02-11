# Written by https://www.reddit.com/user/CJDAM/
# Written in Python 3

import format_func
import pip
# NEW -->
from difflib import SequenceMatcher
#
pip.main(['install', 'configparser==3.5.0'])

from backports import configparser


def install(package):
    pip.main(['install', package])


reqParse = configparser.RawConfigParser()
reqFilePath = r'required_modules.txt'
reqParse.read(reqFilePath)


for each_section in reqParse.sections():
    for (each_key, each_val) in reqParse.items(each_section):
        install(each_val)

import urllib.request
from filecmp import dircmp
from googleapiclient.discovery import build
import time
import sys


def google_search(term, api, cse, **kwargs):
    service = build('customsearch', 'v1', developerKey=api)
    result = service.cse().list(q=term, cx=cse, **kwargs).execute()
    return result['items']


# Parses data from 'config.txt'
configParser = configparser.RawConfigParser()
configFilePath = r'config.txt'
configParser.read(configFilePath)

# Retrieves script parameters from configparser
api_key = configParser.get('keys', 'api_key')
cse_id = configParser.get('keys', 'cse_id')
path_old = configParser.get('mod_paths', 'path_old_ver')
path_new = configParser.get('mod_paths', 'path_new_ver')
modpack_name = configParser.get('misc', 'modpack_name')
errors = []

if api_key == 'API_KEY':
    errors.append('api_key')
if cse_id == 'CSE_ID':
    errors.append('cse_id')
if path_old == 'OLD_DIR':
    errors.append('path_old')
if path_new == 'NEW_DIR':
    errors.append('path_new')

if errors.__len__() > 0:
    print('Please configure the following in config.txt:')
    for error in errors:
        print('- {0}'.format(error));
    time.sleep(5)
    sys.exit()

else:
    # Creates the changelog.html file and writes the changelog title
    new_file = open('changelog.txt', 'w')
    new_file.write('<h1>{0} Changelog</h1>\n'.format(modpack_name))
    new_file.write('<p>Written by /u/CJDAM<p>')
    new_file.write('<br><br><br>')
    new_file.close()

    # Compares the two mod directories and returns unique files from the new version
    dcmp = dircmp(path_old, path_new)
    right_only = dcmp.right_only

    mod_dict = {}
    i = 0

    # Inserts key/value pairs into mod_dict (Integer:FileName)
    for filename in right_only:
        pair = {i: filename}
        mod_dict.update(pair)
        i += 1

    strip_tags = format_func.ask_mode()

    # For each string in the mod_array list do the following:
    for name in mod_array:
        # Defines search_term as the current file name
        search_term = name

        print('Getting ' + name + '\n')

        # Initializes a new google search using the file name, api_key, cse_id. Returns first search result
        new_search = google_search(search_term, api_key, cse_id, num=1)

        for search in new_search:
            # Retrieves the curseforge file link from the query
            res = search['link']
            # Opens the link and views the html
            response = urllib.request.urlopen(res)

            if strip_tags == 'no':
                content = format_func.format_tags(response)
            elif strip_tags == 'yes':
                content = format_func.strip_tags(response, name)

            # Opens changelog.html to append the retrieved changelog to EOF
            file_object = open('changelog.txt', 'a')
            # Writes file name to changelog.txt
            file_object.write(content)
            file_object.close()
