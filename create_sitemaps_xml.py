from models import Data, Unit, News

BASE_URL = 'https://metrolog.online'
SEARCH_LINK = 'search'
CONVERTER_LINK = 'converter'
NEWS_LINK = 'news'
COUNT = 0


def main():
    with open('../static/sitemap.xml', "w") as file:
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n\t<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        global COUNT
        for i in Data.query.all():
            COUNT += 1
            link = f"\n\t\t<url>\n\t\t\t<loc>{BASE_URL}/{SEARCH_LINK}/{i.Slug}</loc>\n\t\t</url>"
            # print(f'{COUNT}) {link}')
            file.write(link)

        for i in Unit.query.all():
            COUNT += 1
            link = f"\n\t\t<url>\n\t\t\t<loc>{BASE_URL}/{CONVERTER_LINK}/{i.category.slug}/{i.type.slug}/{i.slug}</loc>\n\t\t</url>"
            # print(f'{COUNT}) {link}')
            file.write(link)

        for i in News.query.all():
            COUNT += 1
            link = f"\n\t\t<url>\n\t\t\t<loc>{BASE_URL}/{NEWS_LINK}/{i.category}/{i.slug}</loc>\n\t\t</url>"
            # print(f'{COUNT}) {link}')
            file.write(link)

        file.write('\n\t</urlset>')

    return 'Карта сайта обновлена'

if __name__ == '__main__':
    main()

