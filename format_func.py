import re
from bs4 import BeautifulSoup
import inspect
from difflib import SequenceMatcher
from googleapiclient.discovery import build


def google_search(term, api, cse, **kwargs):
    service = build('customsearch', 'v1', developerKey=api)
    result = service.cse().list(q=term, cx=cse, **kwargs).execute()
    return result['items']


def get_line():
    return inspect.currentframe().f_back.f_lineno


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


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


def format_tags(response):

    # soup = BeautifulSoup(response, 'html.parser')

    headerlist = {}
    contentlist = {}
    cnt = 0

    for element in response.find_all(class_='logbox'):
        for header in element.find_all('h3'):
            headerlist[cnt] = header

        for content in element.find_all('ul'):
            contentlist[cnt] = content

        cnt += 1

    print(headerlist[0])
    print(contentlist[0])


def strip_tags(response, modname):

    # CHANGE: response = soup = str(soup.find('div', class_='logbox'))
    # print(response)

    soup = BeautifulSoup(response, 'html.parser')

    h3_tag = soup.find('h3')
    ul_tag = soup.find('ul')

    if h3_tag is not None and ul_tag is not None:
        header = str(h3_tag)
        content = str(ul_tag)
        formatting = header + content
        print('format_func.py line {}: IF'.format(get_line()))

    else:
        formatting = str(soup)
        print('format_func.py line {}: ELSE'.format(get_line()))

#    formatting = re.sub('<p>|<p> \+|<p>\+|<p> \*|<p>\*|<p>-', '\n- ', formatting)
    if soup.find('li') is not None:
        formatting = re.sub('<li>', '\n- ', formatting)
    formatting = re.sub('</p>', '', formatting)
    formatting = re.sub('<.*?>', '', formatting)
    # Remove ' & [ characters
    name_format = re.sub('(\'|\[|])(?!\w\s)', '', modname)
    changelog_entry = '\n\n' \
                      '========================================\n' \
                      '{}\n' \
                      '========================================' \
                      '{}'.format(name_format, formatting)

    print(changelog_entry)

    return changelog_entry
