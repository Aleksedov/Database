import os
import sqlite3
import requests

from sitedb.utilites.API_utils.utils.tables_class import *
from sitedb.utilites.API_utils.utils.API_utils import trans_date, get_content, compare_object, create_request_for_post
from sitedb.utilites.API_utils.utils.API_utils import compare_date_object, create_request_date_for_post, get_token

def stucture_analys(url, curs, session):
    """
    Сравнивает информацю о записях структур на сайте и в базе данных
    :param url: адрес сайта
    :param curs: курсор соединения к базе
    :return:
    """
    type_url = url + 'structures_api/'                          # сcылка на API - список объектов # отличие 1
    cont = get_content(type_url, session)                                # информация о структурах на сайте в формате JSON
    if not cont:
        return
    objs_json = JSON_Tables('obj_site', cont)
    objs_json.add_all_items()
    print(objs_json)
    db_objs = Tables("Структури", curs)                         # отличие 2
    print(db_objs)
    db_objs.add_all_items()
    print("обьектов на сайте = ", len(objs_json.items), "обьектов в базе  = ", len(db_objs.items))

    for i_site in objs_json.items:
        obj_request = type_url + str(i_site) + '?format=api'
        if i_site not in db_objs.items:
            print('элемент сайта отсутствует в базе и его необходимо удалить', i_site)
            session.delete(obj_request)
        else:
            discr = compare_object(objs_json.items[i_site], db_objs.items[i_site]) # отличие 4 данные в функции
            if discr:
                site_p = objs_json.items[i_site]
                pt = {
                    "id": "%s" % site_p.id,
                    "name": "%s" % site_p.name}                   # отличие 5    обязательная строка
                for key, value in discr.items():
                    pt[key] = value
                rpt = session.put(obj_request, json=pt)

    for i_base in db_objs.items:
        if i_base not in objs_json.items:
            print('новый элемент из базы для внесения на сайт', i_base)
            add_new_obj(type_url, db_objs.items[i_base], session)            # отличие 4 данные в функции


def compare_object(site_obj, db_obj):
    """
    Сравнивает имеющуюся информацию о судьекте на сайте и в базе данных
    :param site_p:  информация об объекте на сайте
    :param db_p:    информация об объекте в базе данных
    :return: {} если информация совпадает, в противном случае словарь ключи со значенями разницы

    """
    discr = {}
    if site_obj.name != db_obj.Назва:
        print("несовпадение имени ", site_obj.name, db_obj.Назва )
        discr["name"] = "%s" %db_obj.Назва
    if site_obj.overwrite != db_obj.Опис:
        print("несовпадение описания ", site_obj.overwrite, db_obj.Опис )
        discr["overwrite"] = "%s" %db_obj.Опис
    return discr

def add_new_obj(type_url,db_p, session):
    """
    Вносит информацию о новом объекте на сайт
    :param person_request:
    :param new_per: информация о новом субьекте в формате JSON
    """
    obj_request = type_url + '?format=api'
    pst = {
        "id": "%s" %db_p.Код_струк,
        "name": "%s" %db_p.Назва,
    }
    if db_p.__dict__['Опис']:
        pst["overwrite"] = db_p.__dict__['Опис']
    rpost = session.post(obj_request, json=pst)
    print(rpost)


def main():

    url = 'http://127.0.0.1:8000/'
    file_path = "%s\%s" % (os.getcwd(), 'synch_API.sqlite3')
    conn = sqlite3.connect(file_path)
    curs = conn.cursor()
    # curs.execute("DROP TABLE 'Структури'")
    username = 'admin'
    password = '111111111'
    t_url = url+"api-token-auth/"
    auth = {"username": [username], "password": [password]}
    token = get_token(t_url, auth)
    session = requests.Session()
    session.headers.update({'Authorization': 'token %s' % token })
    stucture_analys(url, curs, session)

    pass

if __name__ == '__main__':
    main()