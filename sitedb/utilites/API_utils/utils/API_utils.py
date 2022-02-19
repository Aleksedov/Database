import requests
from requests.auth import HTTPBasicAuth

def trans_date(old_date):
    if not old_date:
        return old_date
    if len(old_date) == 10:
        old_date = old_date.split('.')
        new_date = '%s-%s-%s' % (old_date[2], old_date[1], old_date[0])
        return new_date
    if len(old_date) > 10:
        old_date = old_date.split(' ')
        new_date = old_date[0]
        return new_date
    print('ERROR', old_date)
    return old_date


def get_token(url, auth):
    """
    получает токен по заданной ссылке
    :param url: адрес
    :param auth: кортеж (логин, пароль)
    :return: token
    """
    token = requests.post(url, data=auth)
    return token.json()['token']


def get_content(type_url, session):
    """
    Получает информацию внесенных на сайт объектов
    :param type_url: сcылка на API - список объектов
    :param session: сессия подлючения пользователя
    :return: response - JSON словарь объектов на сайте
    """
    print(type_url, session)
    try:
        response_get = session.get(type_url)

    except:
        print("Ошибка соединения")
        return False
    try:
        response_get.json()
    except:
        print("Ошибка получения json", type_url, response_get)
        return
    return response_get.json()


def compare_object(site_obj, db_obj, pare_keys):
    """
    :param site_p:  информация об объекте на сайте
    :param db_p:    информация об объекте в базе данных
    :param pare_keys: pare_keys - словарь ключей где key - ключ значения на сайте value - в базе
    :return: discr - разница в объектах
    """
    discr = {}
    for key, value in pare_keys.items():
        if str(site_obj.__dict__[key]) != str(db_obj.__dict__[value]) and db_obj.__dict__[value]:
            print ("Несовпдение в %s: сайт - %s, база - %s" % (key,site_obj.__dict__[key],db_obj.__dict__[value]))
            discr[key] = db_obj.__dict__[value]
    return discr

def compare_date_object(site_obj, db_obj, pare_date_keys=None, discr={}):
    """
    :param site_p:  информация об объекте на сайте
    :param db_p:    информация об объекте в базе данных
    :param pare_keys: pare_keys - словарь ключей где key - ключ значения на сайте value - в базе
    :return: discr - разница в объектах
    """
    if pare_date_keys:              # если не внесена пара ключей дат, то возвращает уже имеющуся разницу
        for key, value in pare_date_keys.items():
            if str(site_obj.__dict__[key]) != str(trans_date(db_obj.__dict__[value])) and db_obj.__dict__[value]:
                print("Несовпадение в %s: сайт - %s, база - %s" % (key, site_obj.__dict__[key],
                                                                 trans_date(db_obj.__dict__[value])))
                discr[key] = trans_date(db_obj.__dict__[value])
    return discr

def create_request_for_post(db_obj, pst, pare_keys):
    """
    :param db_p:    информация об объекте в базе данных
    :param pst:     базовый запрос с обязателными значениями
    :param pare_keys: pare_keys - словарь ключей где key - ключ значения на сайте value - в базе
    :return: pst - новые необязательные значения значения
    """

    for key, value in pare_keys.items():
        if db_obj.__dict__[value]:
            pst[key] = db_obj.__dict__[value]
    return pst

def create_request_date_for_post(db_obj, pst, pare_keys):
    """
    :param db_p:    информация об объекте в базе данных
    :param pst:     базовый запрос с обязателными значениями
    :param pare_keys: pare_keys - словарь ключей где key - ключ значения на сайте value - в базе
    :return: pst - новые необязательные значения значения
    """

    for key, value in pare_keys.items():
        if db_obj.__dict__[value]:
            pst[key] = trans_date(db_obj.__dict__[value])
    return pst