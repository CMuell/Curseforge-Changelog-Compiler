import re
from bs4 import BeautifulSoup
from urllib import request
import json
import inspect
import html5lib
from googleapiclient.discovery import build


def google_search(term, api, cse, **kwargs):
    service = build('customsearch', 'v1', developerKey=api)
    result = service.cse().list(q=term, cx=cse, **kwargs).execute()
    return result['items']


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
        link = '{}files'.format(link[0])
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
                entry = {new_version: '{}{}'.format(base_url, a_tag['href'])}
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
                entry = {new_version: '{}{}'.format(base_url, a_tag['href'])}
                links.update(entry)
                count += 1
            elif new_found is True and old_found is False:
                if old_ver in compare_with:
                    break
                else:
                    entry = {a_tag['data-name']: '{}{}'.format(base_url, a_tag['href'])}
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

    for e in entry:

        edit_me = str(e)

        edit_me = strip_tag_type('div', edit_me)  # Remove all <div> tags

        # If statements for tag formatting
        if edit_me.find('ul') is not None:
            edit_me = strip_tag_type('ul', edit_me)  # Remove all <ul> tags
        if edit_me.find('li') is not None:
            edit_me = strip_tag_type('li', edit_me, '<p class="row full">- ', 'opening')  # Replace opening <li> tags with <p class="row">
            edit_me = strip_tag_type('li', edit_me, '</p>', 'closing')  # Replace closing </li> tags with </p>
        if edit_me.find('p') is not None:
            edit_me = re.sub('(<p>([^\w<])+)', '<p class="row full">- ', edit_me)  # Format all <p> tags to <p>-

        edit_me = re.sub(' {2,}(?=<)', '', edit_me)

        header = f'<h3>{version}:</h3><br>'
        edit_me = f'<div class="sub-log" id="{version}" name="{version}">' + header + edit_me + '</div>'

    # Join each edited string as one
    return_str = edit_me
    return return_str


def strip_tag_type(elem, target, rep='', mode='both'):

    # Replace opening and closing tag
    if mode == 'both':
        this = re.sub('<(' + elem + '.*?|/' + elem + ')>', rep, target)
    if mode == 'opening':
        this = re.sub('<' + elem + '.+?>', rep, target)
    if mode == 'closing':
        this = re.sub('</' + elem + '>', rep, target)

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

    header = '--------------------\n{}\n--------------------\n'.format(version)
    section = edit_me
    footer = '\n\n'

    changelog_entry = header + section + footer

    return changelog_entry
