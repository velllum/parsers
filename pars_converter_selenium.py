import os
from app import db
from time import sleep
from models import Unit, Type
from slugify import slugify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_URL = 'https://www.translatorscafe.com/unit-converter/'


# собьрать данные с сайта и запоковать в словарь
def get_data(verbose, response, url):
    verbose.get(f'{BASE_URL}ru-RU/{url}')
    response.get(f'{BASE_URL}ru-RU/{url}/verbose/')

    verbose.find_element_by_xpath("//input[@name='bindid=left&base=1']").send_keys('1')
    select = verbose.find_element_by_xpath("//select[@name='right']")
    option = select.find_elements_by_tag_name('option')

    data = []
    for e, i in enumerate(option, 1):
        i.click()

        """получаем название ед.изм """
        try:
            name = i.text
        except:
            name = ''

        """создаем название ед.изм. для подстановки в BASE_URL (адрес сайта) на латинском"""
        try:
            slug = slugify(name)
        except:
            slug = ''

        """получаем величину ед.изм """
        try:
            unit = verbose.find_element_by_xpath("//input[@name='bindid=right&base=1']").get_attribute('value')
        except:
            unit = ''

        """получаем обозначение ед.изм"""
        try:
            string = response.find_element_by_xpath(f"//div[@class='UntCnvrtTbl']//div[@class='uc-unit']//*[contains(text(), '{name}')]").get_attribute("innerHTML")
            name_symbol = string.split('[')[1].split(']')[0]
        except:
            name_symbol = ''

        """создаем обозначение ед.изм. для подстановки в BASE_URL (адрес сайта) на латинском"""
        try:
            symbol = slugify(name_symbol)
        except:
            symbol = ''

        """
        получаем описание ед. изм. (текст)  Метр (м) — единица измерения
        длины и расстояния в Международной системе единиц (СИ). Метр равен расстоянию,
        которое проходит свет в вакууме за промежуток времени, равный 1/299 792 458 секунды.
        """
        try:
            sleep(0.5)
            description = verbose.find_element_by_xpath("//div[@id='ucDsr']").get_attribute("innerHTML")
        except:
            description = ''

        print(f'{e}) | {name} | {slug} | {unit} | {name_symbol} | {symbol} | {description}')

        data.append({
            'name': name,
            'slug': slug,
            'name_symbol': name_symbol,
            'symbol': symbol,
            'unit': unit,
            'description': description
        })

    verbose.close()
    response.close()

    return data


# обновляем полученые данные в нашей базе
def save_base(data):
    print('===================================== Заполняем базу =============================================')
    for e, i in enumerate(data, 1):
        try:
            req = db.session.query(Unit).filter(Unit.name == i['name'])

			# сморим на полученный ответ из базы данных
            for a in req:
                print(f' ***СТАРЫЕ ДАННЫЕ*** {e}) {a.name} | {a.slug} | {a.description}')

            dic = dict(
                name=i['name'],
                slug=i['slug'],
                name_symbol=i['name_symbol'],
                symbol=i['symbol'],
                unit=i['unit'],
                description=i['description']
            )

            req.update(dic)
            
            db.session.commit()

			# просматриваем созданнный словарь
            print(f"***НОВЫЕ ДАННЫЕ*** {e}) {dic}")

        except Exception as ex:
            print(f'ошибка {ex}')
            db.session.rollback()


def main():
    for url in db.session.query(Type):
        print(f'====================== Собираем данные с сайта BASE_URL {BASE_URL}{url.slug} ==========================')

		# Запускаем без графического интерфейса
        options = Options()
        options.add_argument('--headless')

        verbose = webdriver.Chrome(executable_path=os.path.abspath('chromedriver.exe'), options=options)
        response = webdriver.Chrome(executable_path=os.path.abspath('chromedriver.exe'), options=options)

        try:
            data = get_data(verbose, response, url.slug)
        except Exception as ex:
            print(f'Ошибка , такой классс UntCnvrtTbl не найден {ex}')
            continue

        save_base(data)


if __name__ == '__main__':
    main()
