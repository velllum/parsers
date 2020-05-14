import requests
from app import db
from models import Data, updated_data
from slugify import slugify
from sqlalchemy import func
from datetime import datetime

COUNT = 0
TOTAL = 0

# получаем значение по урлу
def get_url(url):
    with requests.Session() as s:
        response = s.get(url)
        if response.ok:
            return response
        else:
            print('ОШИБКА - 404')


# разобрать массив
def get_data(json):

    LIST_KEY = [
        'date', 'factory_num_si', 'name_si', 'number_si', 'mpisi', 'certificate_life_si', 'designation_si',
        'year_si', 'manufacturer_total_si', 'country_si', 'settlement_si', 'manufacturer_si', 'description_si_name',
        'description_si_link', 'method_verif_si_name', 'method_verif_si_link', 'id_si'
    ]

    DIC = dict.fromkeys(LIST_KEY)

    for i in json['properties']:

        if 'foei:date' in i.values(): DIC['date'] = i.get('value')

        if 'foei:FactoryNumSI' in i.values(): DIC['factory_num_si'] = i.get('value')

        if 'foei:NameSI' in i.values(): DIC['name_si'] = i.get('value')

        if 'foei:NumberSI' in i.values(): DIC['number_si'] = i.get('value')

        if 'foei:MPISI' in i.values(): DIC['mpisi'] = i.get('value')
        
        if 'foei:CertificateLifeSI' in i.values(): DIC['certificate_life_si'] = i.get('value')

        if 'foei:DesignationSI' in i.values(): DIC['designation_si'] = i.get('value')[0]

        if 'foei:YearSI' in i.values(): DIC['year_si'] = i.get('value')

        if 'foei:ManufacturerTotalSI' in i.values(): DIC['manufacturer_total_si'] = i.get('value')

        country_si = []
        if 'foei:SI2_assoc' in i.values():
            for f in i['value']:
                for g in f['fields']:
                    if 'foei:CountrySI' in g.values():
                        country_si.append(g.get('value'))
            DIC['country_si'] = ', '.join(country_si)

        settlement_si = []
        if 'foei:SI2_assoc' in i.values():
            for f in i['value']:
                for g in f['fields']:
                    if 'foei:SettlementSI' in g.values():
                        settlement_si.append(g.get('value'))
            DIC['settlement_si'] = ', '.join(settlement_si)

        manufacturer_si = []
        if 'foei:SI2_assoc' in i.values():
            for f in i['value']:
                for g in f['fields']:
                    if 'foei:ManufacturerSI' in g.values():
                        manufacturer_si.append(g.get('value'))
            DIC['manufacturer_si'] = ', '.join(manufacturer_si)

        if 'foei:DescriptionSI' in i.values(): DIC['description_si_name'] = i.get('value')

        if 'foei:DescriptionSI' in i.values(): DIC['description_si_link'] = i.get('link')

        if 'foei:MethodVerifSI' in i.values(): DIC['method_verif_si_name'] = i.get('value')

        if 'foei:MethodVerifSI' in i.values(): DIC['method_verif_si_link'] = i.get('link')

        if 'id' in i.values(): DIC['id_si'] = i.get('value')

    return DIC



# сохранение в базу данных
def save_base(dic):

    global COUNT
    COUNT += 1

    data = updated_data()
    for _ in dic:
        data.id = dic['id_si']
        data.NumberSI = dic['number_si']
        data.NameSI = dic['name_si']
        data.CertificateLifeSI = dic['certificate_life_si']
        data.CountrySI = dic['country_si']
        data.date = dic['date']
        data.DesignationSI = dic['designation_si']
        data.ManufacturerSI = dic['manufacturer_si']
        data.ManufacturerTotalSI = dic['manufacturer_total_si']
        data.MPISI = dic['mpisi']
        data.FactoryNumSI = dic['factory_num_si']
        data.DescriptionSI = dic['description_si_link']
        data.DescriptionSiName = dic['description_si_name']
        data.MethodVerifSI = dic['method_verif_si_link']
        data.MethodVerifSiName = dic['method_verif_si_name']
        data.YearSI = dic['year_si']
        data.SettlementSI = dic['settlement_si']

        data.Maker = slugify(dic['manufacturer_si'])
        data.Slug = f"{slugify(dic['name_si'])}-{COUNT}"

    db.session.add(data)
    db.session.commit()

    print(f"{COUNT}) | {dic['id_si']} | {dic['number_si']} | {dic['name_si']} | {slugify(dic['manufacturer_si'])} | {slugify(dic['name_si'])}-{COUNT} | {dic['factory_num_si']}")



def main():

    start = datetime.now()

    BASE_URL = 'https://fgis.gost.ru/fundmetrology/api/registry/4/data'
    TOTAL_LINK = f'{BASE_URL}?pageNumber=1&pageSize=1&orgID=CURRENT_ORG'

    global TOTAL
    TOTAL = get_url(TOTAL_LINK).json()['result']['totalCount']  # берем общее количество записей из json масива
    BASE_TOTAL = db.session.query(func.count(Data.ids)).scalar()

    print(TOTAL)
    print(BASE_TOTAL)

    if TOTAL-BASE_TOTAL >= 100:

        for i in range(1, TOTAL+1):
            LINK = f'{BASE_URL}?pageNumber={i}&pageSize=1000&orgID=CURRENT_ORG'

            JSON = ( x for x in get_url(LINK).json()['result']['items'] )

            for g in JSON:
                dic = get_data(g)
                save_base(dic)

            print(
                f"""
    Общее время работы скрипта: ( {datetime.now() - start} )
    Запесей сохранено ( COUNT ): {COUNT}
    Всего записей в базе ( TOTAL ): {TOTAL}
    """
            )

            if COUNT == TOTAL: break

    print('stop')


if __name__ == '__main__':
    main()
