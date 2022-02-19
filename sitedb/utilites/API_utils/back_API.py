import itertools

import requests
import json

import os
import sqlite3

from utils.API_utils import get_token

from person_synch import persons_analys
from structure_synch import stucture_analys
from case_synch import case_analys
from organisation_synch import organis_analys
from pow_synch import pow_analys
from article_synch import article_analys
from persecution_synch import persecution_analys
from aip_synch import aip_analys
from right_synch import right_analys
from status_synch import status_analys
from act_synch import act_analys
from right_in_act_synch import via_analys
from pia_synch import pia_analys
from depriving_synch import depriving_analys



def api_synch(url, curs, session):
    """
    Синхронизирует информацию на сайте и в базе данных
    :param url: адрес сайта
    :param curs: путь к базе данных
    """



    test_url = url + 'persons_api/'

    cont = session.get(test_url).json()
    print(session.get(test_url))

    persons_analys(url, curs, session)
    stucture_analys(url, curs, session)
    case_analys(url, curs, session)
    organis_analys(url, curs, session)
    pow_analys(url, curs, session)
    article_analys(url, curs, session)
    persecution_analys(url, curs, session)
    aip_analys(url, curs, session)
    right_analys(url, curs, session)
    status_analys(url, curs, session)
    act_analys(url, curs, session)
    via_analys(url, curs, session)
    pia_analys(url, curs, session)
    depriving_analys(url, curs, session)

def main():
    # admin_token = '955fe159642f8ebfefaa81c18454e09c1a73a58d'  # админский
    # # admin_token = '6167d7881aa97dff17b880306bdafd07ba001382'    # пользовательский
    # # admin_token = '6167d7841aa97dff17b880306bdafd07ba001382'    # неверный

    file_path = "%s\%s" % (os.getcwd(), 'synch_API.sqlite3')
    conn = sqlite3.connect(file_path)
    curs = conn.cursor()
    name_of_tables = list(curs.execute('SELECT name from sqlite_master where type= "table"'))
    print('name_of_tables begin', name_of_tables)

    url = 'http://127.0.0.1:8000/'
    username = 'admin'
    password = '111111111'
    t_url = url+"api-token-auth/"
    auth = {"username": [username], "password": [password]}
    token = get_token(t_url, auth)
    # print (username, token)
    session = requests.Session()
    session.headers.update({'Authorization': 'token %s' % token})
    api_synch(url, curs, session)


    pass

if __name__ == '__main__':
    main()
