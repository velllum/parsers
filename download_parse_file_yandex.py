from models import updated_data
from datetime import datetime
import yadisk


YANDEX = yadisk.YaDisk(token="token_ya_disk")

BASE_URL = 'https://fgis.gost.ru/fundmetrology'
# DIR_PATH = f'/sate-pdf-files-{datetime.now().month}-{datetime.now().year}/'
DIR_PATH = f'/pdf-files/'  # папка для хронения файлов
COUNT = 0


# проверка директории
def check_directory(directory):
    try:
        if not YANDEX.is_dir(path=directory):
            YANDEX.mkdir(path=directory)
        return True
    except yadisk.exceptions.PathExistsError:
        print(f'Ошибка! Директория {directory} уже существуе!')


# сохранить файл в яндекс диск
def save_file(name_file, link):

    URL = f'{BASE_URL}{link}'
    PACH = f'{DIR_PATH}{name_file}'

    global COUNT
    COUNT += 1

    try:
        if not YANDEX.is_file(path=PACH):
            YANDEX.upload_url(url=URL, path=PACH)
            print(f'{COUNT}) файл {name_file} сохранён в яндекс диске')
        else:
            print(f'{COUNT}) файл {name_file} существует в яндекс диске')
    except yadisk.exceptions.PathExistsError as e:
        print(f'Ошибка | {name_file} | {e}')


def main():

    print(YANDEX.check_token())

    start = datetime.now()

    DATA = updated_data.query.all()

    METHOD_LINK_NAME = tuple( {i.MethodVerifSI: i.MethodVerifSiName} for i in DATA if i.MethodVerifSI)
    DESCRIPTION_LINK_NAME = tuple( {i.DescriptionSI: i.DescriptionSiName} for i in DATA if i.DescriptionSI)

    LINK_NAME = DESCRIPTION_LINK_NAME + METHOD_LINK_NAME

    print(len(LINK_NAME))

    if YANDEX.check_token() and check_directory(DIR_PATH):
        print('ok')
        for i in LINK_NAME:
            name_file=list(i.values())[0]
            link=list(i.keys())[0]
            print(name_file, link)
            save_file(name_file, link)

    print(datetime.now() - start)


if __name__ == '__main__':
    main()
