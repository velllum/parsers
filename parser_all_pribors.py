import requests
from bs4 import BeautifulSoup
from slugify import slugify

from parse.mod import Data_test, Device
from app import db

# получаем значение по указанному урлу
def get_url(url):
    return requests.get(url=url).text

# получаем всех ссылоки в каталоге указанные в "Измерительные приборы от А до Я" 'https://all-pribors.ru/groups'
def get_groups_url(url):
    soup = BeautifulSoup(get_url(url=url), "lxml")
    res_url = soup.find_all('div', class_='col-sm-6 col-md-4 col-lg-3 text-truncate')
    list_group = []
    for i in res_url:
        list = [i.a.get('href'), i.span.text]
        list_group.append(list)
    return list_group

# получаем всех ссылоки в каталоге указанные в наименование прибора с пиагинацией https://all-pribors.ru/groups/ampermetry-8/grsi-devices?page=1
def get_grsi_devices_url(link):
    list_devices_url = []
    for i in link:
        num_prefix = 2
        if int(i[1])%10 == 0:
            num_prefix = 1
        for j in range(1, (int(i[1])//10)+num_prefix):
            list_link = f'{i[0]}/grsi-devices?page={j}'
            list_devices_url.append(list_link)
    return list_devices_url

# получаем данные с странице наименование приборов
def get_register(link):
    soup = BeautifulSoup(get_url(url=link), "lxml")
    h1 = soup.find('div', class_='h1 h1-big text-center')
    register_list = [i.text for i in soup.find_all('div', class_='h4 text-center')]
    return h1.text, register_list

# сохранеие спарсенных данных в базу
def save_value_to_data(name, register):
    try:
        for data, device in db.session.query(Data_test, Device).filter(Data_test.NumberSI == register).filter(Device.name == name):
            print(f'{register} - {data.NumberSI} - {name} | {device.name} - {device.id}')
            data.device_id = device.id

            # db.session.add(data)
            # db.session.commit()
    except:
        print(f'{register} - нет данных')


def get_device(url):
    soup = BeautifulSoup(get_url(url=url), "lxml")
    div = soup.find_all('div', class_='col-sm-6 col-md-4 col-lg-3 text-truncate')
    list_name = [ i.a.text for i in div ]
    list_description = [ i.a.get('title') for i in div ]

    return list_name, list_description


def save_device(list_name, list_description):
    for name, description in zip(list_name, list_description):
        try:
            device = Device.query.filter(Device.name == name).first()
            print(f'Данные под именем {device.name} уже присутствует')
        except:
            device = Device(name=name, description=description, slug=slugify(name))
            # db.session.add(device)
            # db.session.commit()
            print(f'ОШИБКА! Данные под именем {name} были добавлены')

# сохраняем количество типов приборов из базы Data в Device
def save_count_values():
    for dev in Device.query.all():
        try:
            count = Data_test.query.filter(Data_test.device_id == dev.id).count()
            dev.count = count
            # db.session.add(dev)
            # db.session.commit()
            print(f'{dev.count} - {count}')
        except:
            print(f'Ошибка !')

def main():
    url = 'https://all-pribors.ru/groups'
    list_name, list_description = get_device(url)
    save_device(list_name, list_description)

    list_url_groups = get_groups_url(url)
    list_devices_url = get_grsi_devices_url(list_url_groups)

    for e, i in enumerate(list_devices_url, start=1):
        name, register_list = get_register(i)
        for j in register_list:
            save_value_to_data(name, j)

    save_count_values()


if __name__ == '__main__':
    main()
