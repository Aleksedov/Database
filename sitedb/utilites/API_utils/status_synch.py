import os
import sqlite3
import requests

from utils.tables_class import *
from utils.API_utils import trans_date, get_content, compare_object, create_request_for_post
from utils.API_utils import compare_date_object, create_request_date_for_post, get_token

def status_analys(url, curs, session):
    """
    Сравнивает информацю о записях структур на сайте и в базе данных
    :param url: адрес сайта
    :param curs: курсор соединения к базе
    :return:
    """
    type_url = url + 'status_api/'                          # сcылка на API - список объектов # отличие 1
    cont = get_content(type_url, session)                                # информация о структурах на сайте в формате JSON
    if cont:
        objs_json = JSON_Tables('obj_site', cont)
        objs_json.add_all_items()
        print("обьектов на сайте = ", len(objs_json.items))
    else:
        print("обьекті на сайте отсутсвуют")
        objs_json = {}
    print(objs_json)
    db_objs = Tables("Статус в переслідуванні", curs)                         # отличие 2
    print(db_objs)
    db_objs.add_all_items()
    print("обьектов в базе  = ", len(db_objs.items))

    if objs_json:
        for i_site in objs_json.items:
            obj_request = type_url + str(i_site) + '?format=api'
            if i_site not in db_objs.items:
                print('элемент сайта отсутствует в базе и его необходимо удалить', i_site)
                session.delete(obj_request)
            else:
                # отличие 4 данные в функции
                pare_keys = {
                    "status": "Статус"
                }
                discr = compare_object(objs_json.items[i_site], db_objs.items[i_site], pare_keys)
                pare_date_keys = {
                    "date": "Початок",
                    "date_of_end": "Завершення"
                }
                discr = compare_date_object(objs_json.items[i_site], db_objs.items[i_site], pare_date_keys, discr)
                if discr:
                    print("Несовпадение в элементе -", objs_json.items[i_site])
                    site_p = objs_json.items[i_site]\
                    # отличие 5    обязательная строка
                    pt = {
                        "id": site_p.id,
                        "status": site_p.status}
                    for key, value in discr.items():
                        pt[key] = value
                    rpt = session.put(obj_request, json=pt)

    for i_base in db_objs.items:
        if not objs_json or i_base not in objs_json.items:
            print('новый элемент из базы для внесения на сайт', i_base)
            add_new_obj(type_url, db_objs.items[i_base], session)


def add_new_obj(type_url, db_obj, session):
    """
    Вносит информацию о новом объекте на сайт
    """
    obj_request = type_url + '?format=api'
    pst = {
        "id": db_obj.Код_стат,                                            # 4.1 разница
        "persecution": db_obj.__dict__['Переслідування'],                             # 4.2 разница
    }
    # 4.3 разница список ключей
    pare_keys = {
        "status": "Статус",
    }
    pst = create_request_for_post(db_obj, pst, pare_keys)
    pare_date_keys = {
        "date": "Початок",
        "date_of_end": "Завершення"
    }
    pst = create_request_date_for_post(db_obj, pst, pare_date_keys)
    try:
        session.post(obj_request, json=pst)
    except:
        print("onnectionError(err, request=request)",pst, obj_request)


def main():
    url = 'http://127.0.0.1:8000/'
    file_path = "%s\%s" % (os.getcwd(), 'synch_API.sqlite3')
    conn = sqlite3.connect(file_path)
    curs = conn.cursor()

    username = 'admin'
    password = '111111111'
    t_url = url+"api-token-auth/"
    auth = {"username": [username], "password": [password]}
    token = get_token(t_url, auth)
    session = requests.Session()
    session.headers.update({'Authorization': 'token %s' % token })
    status_analys(url, curs, session)

    pass

if __name__ == '__main__':
    main()