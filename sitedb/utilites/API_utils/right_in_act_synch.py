import os
import sqlite3
import requests

from sitedb.utilites.API_utils.utils.tables_class import *
from sitedb.utilites.API_utils.utils.API_utils import trans_date, get_content, compare_object, create_request_for_post
from sitedb.utilites.API_utils.utils.API_utils import compare_date_object, create_request_date_for_post, get_token



def via_analys(url, curs, session):
    """
    Сравнивает информацю о записях структур на сайте и в базе данных
    :param url: адрес сайта
    :param curs: курсор соединения к базе
    :return:
    """
    type_url = url + 'via_api/'                          # сcылка на API - список объектов # отличие 1
    cont = get_content(type_url, session)                                # информация о структурах на сайте в формате JSON
    if not cont:
        return
    objs_json = JSON_Tables('obj_site', cont)
    objs_json.add_all_items()
    print(objs_json)
    db_objs = Tables("Акт", curs)                         # отличие 2
    print(db_objs)
    db_objs.add_all_items()
    print("обьектов на сайте = ", len(objs_json.items), "обьектов в базе  = ", len(db_objs.items))
    pers_in_aip_site = {}

    for i_site in objs_json.items:
        obj_request = type_url + str(i_site) + '?format=api'
        if objs_json.items[i_site].act not in db_objs.items:
            print('акт сайта отсутствует в базе и удалется', objs_json.items[i_site].act)
            session.delete(obj_request)
            continue
        aip_base = db_objs.items[objs_json.items[i_site].act].__dict__['Порушені права']
        aip_base = aip_base.split(';')
        if str(objs_json.items[i_site].rights) not in aip_base:
            print('право %s в акте %s отсутствует в базе и удаляется' % (objs_json.items[i_site].rights,
                  objs_json.items[i_site].act))
            session.delete(obj_request)
            continue
        act_site = objs_json.items[i_site].act
        if not act_site in pers_in_aip_site:
            pers_in_aip_site[act_site] = []
        pers_in_aip_site[act_site].append(objs_json.items[i_site].rights)  #добавляет в ghfdj к frne с сайта

    list_obj_request = type_url + '?format=api'
    for i_base in db_objs.items:
        aip_base = db_objs.items[i_base].__dict__['Порушені права']
        if not aip_base:
            continue
        aip_base = aip_base.split(';')
        if i_base not in pers_in_aip_site:
            print('преследование базы отсутствует в Aip сайта и все его АИп добавляются на сайт', i_base)

            for h_r in aip_base:
                pst = {
                    "act": i_base,
                    "rights": int(h_r)
                }
                rpst = session.post(list_obj_request, json=pst)
                print(rpst, list_obj_request, pst)

        else:
            for h_r in aip_base:
                if int(h_r) not in pers_in_aip_site[i_base]:
                    print('Aip базы отсутствует в Aip сайта и статья добавляется на сайт', i_base , h_r)
                    pst = {
                        "act": i_base,
                        "rights": h_r
                    }
                    session.post(list_obj_request, json=pst)


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
    via_analys(url, curs, session)

    pass

if __name__ == '__main__':
    main()