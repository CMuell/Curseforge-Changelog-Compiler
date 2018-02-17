import re
import time
import sys
from bs4 import BeautifulSoup
from urllib import request
from googleapiclient.discovery import build


def google_search(term, api, cse, **kwargs):
    service = build('customsearch', 'v1', developerKey=api)
    result = service.cse().list(q=term, cx=cse, **kwargs).execute()
    return result['items']


def verify_config(api, cse, dir1, dir2):
    error = []
    if api == 'API_KEY':
        error.append('api_key')
    if cse == 'CSE_ID':
        error.append('cse_id')
    if dir1 == 'OLD_DIR':
        error.append('path_old')
    if dir2 == 'NEW_DIR':
        error.append('path_new')

    if error.__len__() > 0:
        print('Please configure the following in config.txt:')
        for err in error:
            print(f'- {err}')
        time.sleep(5)
        sys.exit()
    else:
        return False


def list_to_object(alist, sub):
    # alist = list to make object with
    # sub = regex expression
    count = 0
    output = {}
    for name in alist:
        this = re.sub(sub, '', name)
        key_value = {count: this}
        output.update(key_value)
        count += 1
    return output


def clean_string(string, mode):
    # int = strip all integers
    # special = strip all special characters
    # all = strip everything except letters
    if mode is 'int':
        this = re.sub('[0-9]', '', string).lower()
    elif mode is 'special':
        this = re.sub('[^\w]', '', string).lower()
    elif mode is 'all' or mode is None:
        this = re.sub('[^a-zA-Z0-9]+', '', string)
        this = re.sub('[^a-zA-Z]\w.+', '', this).lower()
    return this


def find_link(search):
    count = 0
    for s in search:
        if '/files' in s['link']:
            # If link with /files is found, it is the correct link. Stop for loop.
            link = s['link']
            break
        # If /files not found in link, increment count
        else:
            count += 1
        if count > 1:
            # If count eclipses the number of search results, the correct link was not found for this mod.
            break
    if 'link' in locals():
        # Format all links to: /projects/modname/files
        link = link.rsplit('files', 1)
        link = f'{link[0]}files'
        return link
    else:
        return None


def find_in_link(link, element, aclass=None, mode='str'):
    req = request.urlopen(link)
    resp = BeautifulSoup(req, 'html5lib')
    if aclass is not None:
        find_in_resp = resp.find_all(element, class_=aclass)
    else:
        find_in_resp = resp.find_all(element)

    if mode == 'str':
        return str(find_in_resp)
    elif mode == 'none':
        return find_in_resp


def get_all_elem(text, element, aclass=None):
    search = BeautifulSoup(text, 'html5lib')
    if aclass is not None:
        search = search.find_all(element, class_=aclass)
    else:
        search = search.find_all(element)

    return search


def compare_versions(web_versions, new_version, old_version):
    new_found = False
    old_found = False

    for a_tag in web_versions:
        # Format web version to comparable string
        compare_with = re.sub('\.jar', '', a_tag['data-name'])
        compare_with = str(clean_string(compare_with, 'special'))
        # Format local versions
        new_ver = str(clean_string(new_version, 'special'))

        if old_version is not None:
            old_ver = str(clean_string(old_version, 'special'))

            if new_found is not True and new_ver in compare_with:
                new_found = True

            if old_found is not True and old_ver in compare_with:
                old_found = True
        else:
            if new_found is not True and new_ver in compare_with:
                new_found = True

    # Prepare arguments for get_log_links()
    if new_found is True:
        if old_found is False:
            this = get_log_links(new_version, web_versions)
            return this
        elif old_found is True:
            this = get_log_links(new_version, web_versions, old_version)
            return this

    elif new_found is False:
        this = None
        return this


def get_log_links(new_version, web_ver, old_ver=None):
    base_url = 'https://minecraft.curseforge.com'
    links = {}

    if old_ver is None:
        for a_tag in web_ver:
            compare_with = re.sub('\.jar', '', a_tag['data-name'])
            compare_with = str(clean_string(compare_with, 'special'))
            new_ver = str(clean_string(new_version, 'special'))
            if new_ver in compare_with:
                entry = {new_version: f'{base_url}{a_tag["href"]}'}
                links.update(entry)
                break

        # Prepare return
        return links

    if old_ver is not None:

        new_found = False
        old_found = False
        count = 0

        for a_tag in web_ver:
            compare_with = re.sub('\.jar', '', a_tag['data-name'])
            compare_with = str(clean_string(compare_with, 'special'))
            new_ver = str(clean_string(new_version, 'special'))
            old_ver = str(clean_string(old_ver, 'special'))
            if new_ver in compare_with and new_found is False:
                new_found = True
                entry = {new_version: f'{base_url}{a_tag["href"]}'}
                links.update(entry)
                count += 1
            elif new_found is True and old_found is False:
                if old_ver in compare_with:
                    break
                else:
                    entry = {a_tag['data-name']: f'{base_url}{a_tag["href"]}'}
                    links.update(entry)
                    count += 1

        # Prepare return
        return links


def ask_mode():
    while True:
        choice = input('Strip HTML Tags? [y/n]: ')
        if choice not in ('y', 'yes', 'n', 'no'):
            print('Try Again')
        else:
            if choice in ('y', 'yes'):
                return 'yes'
            elif choice in ('n', 'no'):
                return 'no'


def create_entry(entry, version):  # Processes each changelog format

    edit_me = None
    base_name = clean_string(version, 'all')

    # For mods that include 20 changelogs on 1 page (I hate you)
    # Show most recent changelog, delete from second <h3> onward
    if base_name == 'forestry':
        edit_me = str(entry[0])
        soup = BeautifulSoup(edit_me, 'html5lib')

        # Deletes everything including and after second <h3></h3> (wrong version)
        delete_from_here = soup.select_one('h3:nth-of-type(2)')
        edit_me = re.sub('(' + str(delete_from_here) + ')([\s\S]*)', '', edit_me)
        # Table row/cell formatting
        edit_me = strip_tag_type('h3', edit_me)
        edit_me = strip_tag_type('div', edit_me)
        edit_me = strip_tag_type('ul', edit_me)
        edit_me = strip_tag_type('li', edit_me, '<tr class="text-row"><td class="text-cell">', 'opening')
        edit_me = strip_tag_type('li', edit_me, '</th></tr>', 'closing')
        edit_me = strip_tag_type('p', edit_me, '<tr class="text-row"><td class="text-cell>', 'opening')
        edit_me = strip_tag_type('p', edit_me, '</th></tr>', 'closing')
        # Replaces 2+ consecutive spaces with single space (for visuals)
        edit_me = re.sub(' {2,}(?=<)', '', edit_me)

        sub_header = f'<h3 class="sub-header">{version}</h3>'
        table = f'<table class="sub-log-table">{edit_me}</table>'
        mod_div = f'<div class="sub-log" id="{version}">' + sub_header + table + '</div>'

        return_str = mod_div
        return return_str

    else:
        for e in entry:

            edit_me = str(e)
            edit_me = strip_tag_type('div', edit_me)  # Remove all <div> tags

            edit_me = strip_tag_type('h1', edit_me)  # Remove all <h1> tags
            edit_me = strip_tag_type('h2', edit_me)  # Remove all <h2> tags
            edit_me = strip_tag_type('h3', edit_me)  # Remove all <h3> tags
            edit_me = strip_tag_type('ul', edit_me)  # Remove all <ul> tags
            edit_me = strip_tag_type('li', edit_me, '<tr class="text-row"><td class="text-cell">', 'opening')  # Replace opening <li> tags with <tr><td>
            edit_me = strip_tag_type('li', edit_me, '</td></tr>', 'closing')  # Replace closing </li> tags with </td></tr>
            edit_me = re.sub('(<p>([^\w<])+|<p>)', '<tr class="text-row"><td class="text-cell">', edit_me)  # Format all <p> to <tr><td>
            edit_me = re.sub('</p>', '</td></tr>', edit_me)

            edit_me = re.sub(' {2,}(?=<)', '', edit_me)  # Remove double spaces

            sub_header = f'<h3 class="sub-header">{version}</h3>'
            table = f'<table class="sub-log-table">{edit_me}</table>'
            mod_div = f'<div class="sub-log" id="{version}">' + sub_header + table + '</div>'

            return_str = mod_div
            return return_str


def strip_tag_type(elem, target, rep='', mode='both'):
    # Replace opening and closing tag
    if mode == 'both':
        this = re.sub('<(' + elem + '.*?|/' + elem + ')>', rep, target)
    elif mode == 'opening':
        this = re.sub('<' + elem + '.*?>', rep, target)
    elif mode == 'closing':
        this = re.sub('</' + elem + '>', rep, target)
    else:
        print(f'Invalid argument [4: {mode}] in strip_tag_type')
        time.sleep(2)
        sys.exit()

    return this


def create_stripped_entry(entry, version):
    edit_me = None

    for e in entry:

        edit_me = str(e)

        if edit_me.find('h3') is not None:
            edit_me = strip_tag_type('h3', edit_me, '', 'opening')
            edit_me = strip_tag_type('h3', edit_me, '\n', 'closing')

        if edit_me.find('ul') is not None:
            edit_me = strip_tag_type('ul', edit_me)

        if edit_me.find('li') is not None:
            edit_me = strip_tag_type('li', edit_me, '- ', 'opening')
            edit_me = strip_tag_type('li', edit_me, '\n', 'closing')

        edit_me = strip_tag_type('p', edit_me, '\n', 'closing')
        edit_me = re.sub('<.*?>', '', edit_me)

    header = f'--------------------\n{version}\n--------------------\n'
    section = edit_me
    footer = '\n\n'

    changelog_entry = header + section + footer

    return changelog_entry


def this_style():
    style = '\n<style>' \
            '\nhtml {background-color:#d9d9d9; padding: 0px; margin: 0 auto; width: 100%; position: absolute; ' \
            'font-family:Arial, Helvetica, sans-serif} ' \
            '\n.mod-log {padding: 2em; text-align: justify; position: relative; display: inline-block; ' \
            'width: 50%; background-color:  #FCFCFC; border: 1px solid #F4F4F4;} ' \
            '\n.mod-log-header {padding-bottom:0.5em; border-bottom:2px solid #d9d9d9; color:#404040;}' \
            '\nth, h3 {color:#404040}' \
            '\ntable {margin-top:2em}' \
            '\ntr:nth-child(even) {background-color:#f2f2f2}' \
            '\nth, td {padding:0.5em; text-align:left}' \
            '\n.container {position: relative; width: 100%;} ' \
            '\n.filler {position: relative; display: inline-block; width: 25%;} ' \
            '\n.title {padding: 2em; text-align: center; position: relative; display: inline-block; width: 50%}' \
            '\n</style>'

    return style


def this_header(config_mn, strip):

    if strip == 'no':
        header = '\n<div class="filler">&nbsp</div>' \
                 '\n<div class="title" id="changelog_title" name="changelog_title">' \
                 f'\n<h1>{config_mn} Changelog</h1>' \
                 '\n<a href="https://www.reddit.com/user/CJDAM/"><sup>made by /u/CJDAM</sup></a>' \
                 '\n</div>' \
                 '\n<div class="filler">&nbsp</div><br><br>'
        return header

    elif strip == 'yes':
        header = f'=-=-=-=-=-=-=-=-=-=- {config_mn} Changelog -=-=-=-=-=-=-=-=-=-=' \
                 '\nmade by /u/CJDAM' \
                 '\n\n\n'
        return header

    else:
        print('Invalid argument: this_header(arg1, ->arg2<- )')
        print('[yes/no] are accepted strings for arg2')
        print(f'Your input: {strip}')
        time.sleep(2)
        sys.exit()


def write_entry_to_file(new_version, old_version, logs):

    base_name = clean_string(new_version, 'all')

    if base_name == 'forestry':
        logs = logs[0]

    else:
        logs = '<br>'.join(logs)

    name_word = clean_string(new_version, 'all')

    entry = '\n<div class="container">' \
            '\n<div class="filler">&nbsp</div>' \
            f'\n<div class="mod-log" id={name_word}>' \
            f'\n<h2 class="mod-log-header" id={name_word}-header>' \
            f'{old_version} => {new_version}</h2>' \
            f'\n{logs}</div>' \
            '\n<div class="filler">&nbsp</div>' \
            '\n</div>' \
            '<br>'

    return entry
