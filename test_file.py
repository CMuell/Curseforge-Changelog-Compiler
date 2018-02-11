import re
from filecmp import dircmp
from bs4 import BeautifulSoup
from urllib import request
import format_func
import time
import sys

from googleapiclient.discovery import build

api_key = ''
cse_id = ''

#######################


#print(json.dumps(new_search))
#print(search_term)

path_old = "C:\\Users\username\Documents\Curse\Minecraft\Instances\dir1\mods"
path_new = "C:\\Users\username\Documents\Curse\Minecraft\Instances\dir2\mods"

dcmp = dircmp(path_old, path_new)
right_only = dcmp.right_only

mod_dict = {}
i = 0
base_url = 'https://minecraft.curseforge.com'

for filename in right_only:
    frmt_name = filename.replace('.jar', '')
    # Strips any brackets from filename, replaces each with a space
    frmt_name = re.sub('\[|]', ' ', frmt_name)
    # If two spaces are detected (from '][' ) deletes anything past that point from the filename
    frmt_name = re.sub('  \w.+', '', frmt_name)
    pair = {i: frmt_name}
    mod_dict.update(pair)
    i += 1

# print(mod_dict)

strip_tags = format_func.ask_mode()

for key, name in mod_dict.items():
    switch = False
    error_msg = "Couldn't find the project! " \
                "Post issue at https://github.com/CMuell/Curseforge-Changelog-Compiler/issues/new"

    this_search = format_func.google_search(name, api_key, cse_id, num=2)
    for search in this_search:

        title = search['title']
        # Gets the first result that contains the mod name in the 'title' field of search

        while not switch:
            print('{}: {}'.format(key, name))
            sim_percent = format_func.similar(name, title)

            if sim_percent >= 0.25:

                print('Got to search_one')

                # Pulls changelog and jar name if on correct page
                response = request.urlopen(search['link'])
                search_one = BeautifulSoup(response, 'html5lib')
                get_jar_cont = str(search_one.find('div', class_='details-info'))
                search_one = str(search_one.find('div', class_='logbox'))

                # If this page has a changelog div and a jar name, we're in the money!
                if get_jar_cont != 'None' and search_one != 'None':
                    jar_container = BeautifulSoup(get_jar_cont, 'html5lib')
                    jar_name = str(jar_container.find('div', class_='info-data overflow-tip').getText())
                    content = format_func.strip_tags(search_one, jar_name)

                # Else if this page doesn't have a changelog div or jar name, it isn't the correct page. Continue ->
                elif get_jar_cont == 'None' and search_one == 'None':
                    print('Got to search_two')
                    # Search two only works if this is the /projects/modname/files/ directory { TEMPORARY SOLUTION }
                    response = request.urlopen(search['link'])
                    search_two = BeautifulSoup(response, 'html5lib')
                    search_two = search_two.findAll('a', class_='overflow-tip twitch-link')
                    for entry in search_two:
                        if name in entry['data-name']:
                            print('Got to search_three')
                            response = request.urlopen('{}{}'.format(base_url, entry['href']))
                            search_three = BeautifulSoup(response, 'html5lib')
                            # Gets jar file name from CurseForge (so I can skip styling it separately)
                            get_jar_cont = str(search_three.find('div', class_='details-info'))
                            jar_container = BeautifulSoup(get_jar_cont, 'html5lib')
                            jar_name = str(jar_container.find('div', class_='info-data overflow-tip').getText())

                            search_three = str(search_three.find('div', class_='logbox'))
                            if search_three != 'None':
                                if strip_tags == 'no':
                                    print('Placeholder - Strip Tags [no]')
                                if strip_tags == 'yes':
                                    print('yes')
                                    content = format_func.strip_tags(search_three, jar_name)
                            else:
                                print(error_msg)
                                time.sleep(2)

            else:
                print(error_msg)
                time.sleep(2)

            switch = True


