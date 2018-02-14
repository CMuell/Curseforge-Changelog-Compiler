# Written by https://www.reddit.com/user/CJDAM/
# Written in Python 3

import format_func
import pip

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

from filecmp import dircmp
import logging

logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
import time
import sys
import re

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
        print('- {0}'.format(error))
    time.sleep(5)
    sys.exit()

else:
    time.sleep(1)
    strip_tags = format_func.ask_mode()
    # Creates the changelog.html file and writes the changelog title
    if strip_tags == 'no':
        new_file = open('changelog.html', 'w')
        new_file.write(f'<h1>{modpack_name} Changelog</h1>\n')
        new_file.write('<p>Written by /u/CJDAM<p>')
        new_file.write('<br><br><br>')
    else:
        new_file = open('changelog.txt', 'w')
        new_file.write(f'=-=-=-=-=-=-=-=-=-=- {modpack_name} Changelog -=-=-=-=-=-=-=-=-=-=\n')
        new_file.write('written by reddit.com/user/CJDAM\n\n\n')

    new_file.close()

    dcmp = dircmp(path_old, path_new)
    old_jars = dcmp.left_only
    new_jars = dcmp.right_only

    sub = '\.jar'
    old_jar_obj = format_func.list_to_object(old_jars, sub)
    new_jar_obj = format_func.list_to_object(new_jars, sub)
    search_jars = {}

    key = 0

    # Fills the search_jars object with paired new/old mod versions
    for k, newval in new_jar_obj.items():

        new_cleaned = format_func.clean_string(newval, 'all')
        count = 0
        for ke, oldval in old_jar_obj.items():

            old_cleaned = format_func.clean_string(oldval, 'all')

            if new_cleaned in old_cleaned:
                entry = {key: {'new': newval, 'old': oldval}}
                search_jars.update(entry)
                key += 1
                break
            else:
                count += 1

            if count > (len(old_jar_obj) - 1):
                # Checked all old mods, new mod was not matched
                entry = {key: {'new': newval, 'old': None}}
                search_jars.update(entry)
                key += 1

    # Uses search_jars[i]['new'] in google search query

    # For each search_jars object {'new':value, 'old':value}
    for key, value in search_jars.items():

        term = value['new']
        # Do google search on minecraft.curseforge.com
        search = format_func.google_search(term, api_key, cse_id, num=2)
        # Parse link from search and format to projects/modname/files
        link = format_func.find_link(search)

        # If a valid link was found and formatted
        if link is not None:
            # Finds the versions container div
            versions_div = format_func.find_in_link(link, 'div', 'listing-container')
            # Gets all version link elements
            versions = format_func.get_all_elem(versions_div, 'a', 'overflow-tip twitch-link')

            log_links = format_func.compare_versions(versions, value['new'], value['old'])

            log_list = []

            for k, href in log_links.items():
                changelog = format_func.find_in_link(href, 'div', 'logbox', 'none')
                if strip_tags == 'no':

                    entry = changelog
                    output = format_func.create_entry(entry, k)
                    log_list.append(output)
                    # Take entry and use it in create_entry directly
                    # Use k as the changelog version
                    # Append output to list before `for loop`
                    # final_string = ' '.join(list)

                elif strip_tags == 'yes':

                    output = format_func.create_stripped_entry(changelog, k)
                    log_list.append(output)

            # Opens changelog.html to append the retrieved changelog to EOF
            if strip_tags == 'no':
                file_object = open('changelog.html', 'a')
                modname_clean = format_func.clean_string(value['new'], 'special')
                mod_header = f'<div class="mod-log" id={modname_clean}>' \
                             f'<h2 class="mod-log-header" id={modname_clean}-header>{value["old"]} => {value["new"]}</h2>'
                mod_body = '<br>'.join(log_list)
                mod_footer = '</div><br><br>'

                final_entry = mod_header + mod_body + mod_footer
                file_object.write(final_entry)

            elif strip_tags == 'yes':
                file_object = open('changelog.txt', 'a')
                mod_header = f'==================== {value["old"]} => {value["new"]} ====================\n'
                mod_body = '\n'.join(log_list)
                mod_footer = '\n========================================'

                final_entry = mod_header + mod_body + mod_footer
                file_object.write(final_entry)

            file_object.close()

    print('Finished!')
    time.sleep(5)
    sys.exit()
