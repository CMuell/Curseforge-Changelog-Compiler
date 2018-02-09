import re
from bs4 import BeautifulSoup


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
    soup = BeautifulSoup(response, 'html.parser')

    headerlist = {}
    contentlist = {}
    cnt = 0

    for element in soup.find_all(class_='logbox'):
        for header in element.find_all('h3'):
            headerlist[cnt] = header

        for content in element.find_all('ul'):
            contentlist[cnt] = content

        cnt += 1

    print(headerlist[0])
    print(contentlist[0])


def strip_tags(response, modname):
    soup = BeautifulSoup(response, 'html.parser')
    soup = str(soup.find('div', class_='logbox'))

    print(soup)

    h3_tag = soup.find('h3')
    ul_tag = soup.find('ul')

    if h3_tag is not None and ul_tag is not None:
        header = str(h3_tag)
        content = str(ul_tag)
        formatting = header + content
    else:
        formatting = str(soup)

    formatting = re.sub('<p>|<p> \+|<p>\+|<p> \*|<p>\*', '\n- ', formatting)
    formatting = re.sub('<li>', '\n- ', formatting)
    formatting = re.sub('</p>', '', formatting)
    formatting = re.sub('<.*?>', '', formatting)
    name_format = re.sub('(\'|\[|])(?!\w\s)', '', modname)
    formatting = '\n\n{0}\n-----{1}\n\n'.format(name_format, formatting)

    return formatting
