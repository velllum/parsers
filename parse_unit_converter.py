import requests
from bs4 import BeautifulSoup
from slugify import slugify

from models import Data, Device
from app import db


# получаем значение по указанному урлу
def get_url(url):
    with requests.Session() as s:
        response = s.get(url, timeout=(5,2))
        if response.ok:
            return response.text
        else:
            print('ОШИБКА - 404')


# получить список optgroup описание в label
def get_list_optgroups(soup):
    return [ i.get('label') for i in soup.find_all('optgroup') ]


# получить словарь option описание в value , text
def get_dict_options(soup):
    return { i.get('value'):i.text for i in soup.find_all('option') }


# создать список ссылок для сбора данных
def get_link(url, dic):
    return [ url.format(key) for key in dic.keys() ]


# получить словарь с именами и слагами измерний
def get_dict_type(link):
    soup = BeautifulSoup(get_url(url=link), "lxml")
    sel = soup.find('select', attrs={'name':'left'})
    return {i.get('value'): i.text for i in sel.find_all('option')}

# получить словарь с ед. измерний
def get_dict_unit(link):
    res = get_url(url=link)
    a = eval(res.split(',', 1)[1].rsplit(')', 1)[0])
    return dict(zip(a[::2], a[1::2]))

# получить словарь с описанием ед. измерний
def get_list_description(link, d):
    dic = {}
    for e, i in enumerate(iterable=d.keys(), start=1):
        res = get_url(url=f'{link}&i={e}&lc=ru')
        dic[i] = res
        print({i:res})
    return dic

# подготовить словарь для сохранения в базу
def create_single_dict(types, units, descriptions):
    dic = {}
    for t, u, d in zip(types, units, descriptions):
        if t == u and u == d:
            dic[t] = [types[t], units[u], descriptions[d]]
            print(dic)
    return dic


def main():

    url = 'https://www.translatorscafe.com/unit-converter/RU/'
    link_type = 'https://www.translatorscafe.com/unit-converter/RU/{0}'

    # https://www.translatorscafe.com/static/ucvt/factors/{ param }.js
    link_js = 'https://www.translatorscafe.com/static/ucvt/factors/{0}.js'

    # https://www.translatorscafe.com/unit-converter/ws.aspx?op=ui&uc={ param-1 }&i={ param-2 }&lc=ru
    link_get = 'https://www.translatorscafe.com/unit-converter/ws.aspx?op=ui&uc={0}' #&i={1}&lc=ru'

    soup = BeautifulSoup(get_url(url=url), "lxml")

    list_optgroups = get_list_optgroups(soup=soup)
    print(list_optgroups)

    dict_option = get_dict_options(soup=soup)
    print(dict_option)

    links_type = get_link(url=link_type, dic=dict_option)
    print(links_type)

    links_unit = get_link(url=link_js, dic=dict_option)
    print(links_unit)

    links_description = get_link(url=link_get, dic=dict_option)
    print(links_description)

    # get_dict_options_unit(links=links_type)

    for type, unit, description in zip(links_type, links_unit, links_description):
        print('------------------------------------------------dict_unit and dict_type-------------------------------------------------------')
        dict_type = get_dict_type(link=type)
        dict_unit = get_dict_unit(link=unit)
        print(dict_type, len(dict_type))
        print(dict_unit, len(dict_unit))
        print('----------------------------------------------dict_description---------------------------------------------------------')
        dict_description = get_list_description(link=description, d=dict_unit)
        print(dict_description, len(dict_description))
        print('----------------------------------------------dict_single---------------------------------------------------------')
        dict_single = create_single_dict(types=dict_type, units=dict_unit, descriptions=dict_description)
        print(dict_single, len(dict_single))





if __name__ == '__main__':
    main()