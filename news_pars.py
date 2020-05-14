import uuid
import requests
from app import db
from PIL import Image
from models import News
from slugify import slugify
from datetime import datetime
from bs4 import BeautifulSoup


RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}

BASE_URL = 'https://news.metrologu.ru'
COUNT = 0
UNIQUE_ID = 0

# получаем html
def get_html(url):
    with requests.Session() as s:
        response = s.get(url)
        if response.ok:
            return response.text
        else:
            print('ОШИБКА - 404')
            return None

# получить все ссылки с страниц
def get_page_links(html):
    ALL_LINKS = ()

    soup = BeautifulSoup(html, 'lxml')
    news = soup.find_all(class_='news_text')
    links = tuple(i.a.get('href') for i in news)

    ALL_LINKS += links

    print(ALL_LINKS)

    return ALL_LINKS

# получить количество страниц
def get_count():
    count = 0

    while True:
        URL = f'{BASE_URL}/novosti/?cur_cc=1418&curPos={count}0'
        html = get_html(URL)
        soup = BeautifulSoup(html, 'lxml')
        date = soup.find_all('p', class_='date')

        if not bool(date):
            break

        count += 1

        print(count)

    return count
	
# сохранить и обрезать файл .png
def save_image_file(image_file, name_image):
    thumbnail = f"C:/NewProject/MetrologFlask/static/news/image/{name_image}"
    image = Image.open(image_file)
    cropped = image.crop((0, 0, min(image.size), min(image.size)))
    cropped.save(str(thumbnail))

# Фильтровать контент
def get_tag_content(tag):
    if not tag.has_attr('class') and not tag.has_attr('href') and not tag.has_attr('src') and tag.name != 'span' and tag.name != 'li' and tag.name != 'br':
        return True

# преобразлование строки в дату
def convert_date(date_str):
    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
    return datetime.strptime(date_str, '%d %m %Y')

# получить контент
def get_content(links):
    LIST_CONTENT = []
    global UNIQUE_ID

    for i in links:
        URL = f'{BASE_URL}{i}'
        html = get_html(URL)

        if html is None: continue

        soup = BeautifulSoup(html, "lxml")
        content = soup.find('div', class_='news_full')

        try:
            date = content.find('p', class_='date').text.strip()
        except:
            date = None

        try:
            date_sort = convert_date(date)
        except:
            date_sort = None

        try:
            title_cont = content.find('h1').text.strip()
        except:
            title_cont = None

        try:
            UNIQUE_ID += 1
            slug = f"{slugify(content.find('h1').text.strip())}-{UNIQUE_ID}"
        except:
            slug = None

        try:
            html_content = ''.join([str(i) for i in content.find_all(get_tag_content)[1:]])
        except:
            html_content = None

        try:
            category = i.split('/')[1]
        except:
            category = None

        try:
            src_url = content.find('img', class_='news_head_img').get('src')
            image_file = requests.get(f'{BASE_URL}{src_url}', stream=True).raw
            name_image = f'img-{str(uuid.uuid5(uuid.NAMESPACE_DNS, title_cont))}.png'

            save_image_file(image_file, name_image)
        except Exception as e:
            print(e)
            name_image = None

        print(name_image)

        dir = {
            'date_cont': date,
            'date_sort': date_sort,
            'title': title_cont,
            'slug': slug,
            'image': name_image,
            'content': html_content,
            'category': category,
        }

        print(dir)

        LIST_CONTENT.append(dir)

    print(LIST_CONTENT)

    return LIST_CONTENT

# сохранить в базу
def save_base(dic,):
    LIST_SAVE = []
    global COUNT

    for d in dic:

        QUERY = News.query.filter(News.date_cont==d['date_cont']).filter(News.title==d['title']).first()

        if QUERY:
            if QUERY.date_cont and QUERY.title:

                if COUNT >= 5: break

                COUNT += 1
                print(f'{COUNT} - совпадение')
                continue

        print(d['image'])

        new = News()
        new.title=d['title']
        new.slug=d['slug']
        new.date_cont=d['date_cont']
        new.date_sort=d['date_sort']
        new.image=d['image']
        new.content=d['content']
        new.category=d['category']

        db.session.add(new)
        db.session.commit()

        dir = {
            'date_cont': d['date_cont'],
            'date_sort': d['date_sort'],
            'title': d['title'],
            'slug': d['slug'],
            'image': d['image'],
            'content': d['content'],
            'category': d['category'],
        }

        LIST_SAVE.append(dir)

        print(dir)

    return LIST_SAVE


def main():

    global COUNT
    DIR = None

    for i in range(get_count()):
        PAGE_URL = f'{BASE_URL}/novosti/?cur_cc=1418&curPos={i}0'
        html = get_html(PAGE_URL)
        links = get_page_links(html)
        content = get_content(links)
        DIR = save_base(content)

        if COUNT >= 5: break

        COUNT = 0

    return DIR


if __name__ == '__main__':
    main()

