import os
import sqlite3
from ..models import *


class Tables():
    """класс таблица данных"""

    def __init__(self, table_name, curs):
        self.table_name = table_name  # название таблицы
        self.curs = curs
        self.items = {}  # словарь записей таблицы с ключем ID
        self.curs.execute("SELECT * FROM '%s'" % self.table_name).fetchall()
        self.title = list(i[0] for i in curs.description)

    def add_item(self, item):
        """ добавление записи в словарь с ключем  item.id """
        self.items[item[0]] = Table_items(item)
        for attr, val in zip(self.title, item):
            self.items[item[0]].__dict__[attr] = val

    def add_all_items(self):
        for item in self.curs.execute("SELECT * FROM '%s'" % self.table_name).fetchall():
            self.add_item(item)

    def __str__(self):
        return self.table_name + " Список полей = " + str(self.title)


class Table_items(Tables):
    def __init__(self, *args):
        pass


def connect_to_base():
    file_path = "%s\sitedb\synch\%s" % (os.getcwd(), 'source_db.db')
    conn = sqlite3.connect(file_path)
    curs = conn.cursor()
    return curs


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


def add_new_person(person):
    titles = ['Код_люд', 'ПІБ', 'Дата народження', 'Громадянство', 'Фото', 'Біографія', 'Прикмети']
    ids = person.Код_люд
    name = person.ПІБ
    date_of_birth = trans_date(person.__dict__['Дата народження'])
    citizenship = person.Громадянство
    biography = person.Біографія
    if person.Фото:
        photo = 'sitedb/images/person/' + person.Фото
    else:
        photo = 'images/Noface.JPG'
    new = Person.objects.create(id=ids, name=name, date_of_birth=date_of_birth, biography=biography, photo=photo,
                                citizenship=citizenship)
    new.save()


def sync_persons(curs):
    existed = Person.objects.all().values_list('id', flat=True)
    proposed = Tables('Людина', curs)
    proposed.add_all_items()
    proposed_ids = proposed.items
    new_items = [ids for ids in proposed_ids if ids not in existed]
    for id_p in new_items:
        add_new_person(proposed.items[id_p])


def add_new_case(case):
    # ['Код_кейс', 'Назва кейсу', 'Опис кейсу']
    ids = case.Код_кейс
    name = case.__dict__['Назва кейсу']
    overview = case.__dict__['Опис кейсу']
    new = Case.objects.create(id=ids, name=name, overview=overview)
    new.save()


def sync_cases(curs):
    existed = Case.objects.all().values_list('id', flat=True)
    proposed = Tables('Кейс', curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_new_case(proposed.items[id_p])


def add_new_structure(structure):
    # ['Код_струк', 'Назва', 'Опис']
    ids = structure.Код_струк
    name = structure.Назва
    overwrite = structure.Опис
    new = Structure.objects.create(id=ids, name=name, overwrite=overwrite)
    new.save()


def sync_structure(curs):
    existed = Structure.objects.all().values_list('id', flat=True)
    proposed = Tables('Структури', curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_new_structure(proposed.items[id_p])


def add_new_organisation(organisation):
    # ['Код_орг', 'Назва організації', 'Повна назва', 'Юр адреса', 'Телефон', 'Cайт', 'E-mail',
    # 'Структура', 'Місто позбавлення волі', 'Країна', 'Головна організація']
    ids = organisation.Код_орг
    short_name = organisation.__dict__['Назва організації']
    full_name = organisation.__dict__['Повна назва']
    address = organisation.__dict__['Юр адреса']
    phonenumber = organisation.__dict__['Телефон']
    site_org = organisation.__dict__['Cайт']
    Email = organisation.__dict__['E-mail']
    srtucture_id = organisation.__dict__['Структура']

    srtucture = Structure.objects.get(pk=srtucture_id) if srtucture_id else None
    prison = organisation.__dict__['Місто позбавлення волі']
    state = organisation.__dict__['Країна']
    main_org_id = organisation.__dict__['Головна організація']
    main_org = None
    if main_org_id:
        main_org = Organisation.objects.get(pk=main_org_id)
        if not main_org:
            return True
            # защита на случай если при внесени организации оказалось что ее
            # головной офис еще внесен. Внесется при следующей синхронизации

    new = Organisation.objects.create(id=ids, short_name=short_name, full_name=full_name, address=address,
                                      phonenumber=phonenumber, site_org=site_org, Email=Email, srtucture=srtucture,
                                      prison=prison, state=state, main_org=main_org)
    new.save()
    return False


def sync_organisation(curs):
    again = False
    existed = Organisation.objects.all().values_list('id', flat=True)
    proposed = Tables('Організаціія', curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        new_org = add_new_organisation(proposed.items[id_p])  # True если при внесени организации оказалось что ее
        # головной офис еще внесен.
        if new_org:
            again = True
    return again


def add_new_place_of_work(obj):
    # ['Код_мр', 'Особа', 'Організація', 'Посада', 'Звання', 'Початок', 'Закінчення', 'Примітки']
    ids = obj.Код_мр
    person_id = obj.Особа
    person = Person.objects.get(pk=person_id) if person_id else None
    оrganisation_id = obj.Організація
    оrganisation = Organisation.objects.get(pk=оrganisation_id) if оrganisation_id else None
    position = obj.Посада
    rank = obj.Звання
    date = trans_date(obj.Початок)
    date_of_end = trans_date(obj.Закінчення)
    notes = obj.Примітки
    new = PlaceOfWork.objects.create(id=ids, person=person, оrganisation=оrganisation, position=position,
                                     rank=rank, date=date, date_of_end=date_of_end, notes=notes)
    new.save()


def sync_place_of_work(curs):
    existed = PlaceOfWork.objects.all().values_list('id', flat=True)
    proposed = Tables("Місце роботи", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_new_place_of_work(proposed.items[id_p])


def add_new_article(obj):
    # ['Код_ст', 'Стаття', 'Стаття звінувачення', 'Кодекс', 'Зміст']
    ids = obj.Код_ст
    number = obj.Стаття
    parts = obj.__dict__['Стаття звінувачення']
    code = obj.Кодекс
    title = obj.Зміст
    new = Article.objects.create(id=ids, number=number, parts=parts, code=code,
                                 title=title)
    new.save()


def sync_article(curs):
    existed = Article.objects.all().values_list('id', flat=True)
    proposed = Tables("Статті", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_new_article(proposed.items[id_p])


def add_article_in_persecution(pers, article):
    """
    проверка и добавление статей обвинения в преследования
    :param pers: преследование, класс Model
    :param article:  статья, класс Model
    """
    curr_art_in_pers = pers.articlesinpersecution_set.all().values('article')
    if article in curr_art_in_pers:
        return
    new = ArticlesInPersecution.objects.create(persecution=pers, article=article)
    new.save()


def add_new_persecution(obj):
    #  ['Код_пер', 'Тип переслідування', 'Кейс', 'Постраждалий', 'Вирок',
    #  'Статті', 'Подробиці', 'Початок переслідування']
    ids = obj.Код_пер
    type_of_pers = obj.__dict__['Тип переслідування']
    case_id = obj.Кейс
    case = Case.objects.get(pk=case_id) if case_id else None
    victim_id = obj.Постраждалий
    victim = Person.objects.get(pk=victim_id) if victim_id else None
    date = trans_date(obj.__dict__['Початок переслідування'])
    overview = obj.Подробиці

    new = Persecution.objects.create(id=ids, case=case, victim=victim, type_of_pers=type_of_pers,
                                     date=date, overview=overview)
    new.save()
    raw_articles = obj.Статті
    if raw_articles:
        raw_articles = raw_articles.split(';')
        for art_id in raw_articles:
            article = Article.objects.get(pk=art_id)
            new_aip = ArticlesInPersecution.objects.create(persecution=new, article=article)
            new_aip.save()


def sync_persecution(curs):
    existed = Persecution.objects.all().values_list('id', flat=True)
    proposed = Tables("Переслідування", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_new_persecution(proposed.items[id_p])


def add_h_rights(obj):
    # ['Код_пл', 'Право', 'Стаття ЕКПЧ', 'Опис']
    ids = obj.Код_пл
    rights = obj.Право
    echr_article = obj.__dict__['Стаття ЕКПЧ']
    content = obj.Опис
    new = H_Rights.objects.create(id=ids, rights=rights, echr_article=echr_article, content=content)
    new.save()


def sync_h_rights(curs):
    existed = H_Rights.objects.all().values_list('id', flat=True)
    proposed = Tables("Права людини", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_h_rights(proposed.items[id_p])


def add__status(obj):
    # ['Код_стат', 'Переслідування', 'Статус', 'Початок', 'Завершення']
    ids = obj.Код_стат
    persecution_id = obj.Переслідування
    persecution = Persecution.objects.get(pk=persecution_id) if persecution_id else None
    status = obj.Статус
    date = trans_date(obj.Початок)
    date_of_end = trans_date(obj.Завершення)
    new = StatusOfVictimInPers.objects.create(id=ids, persecution=persecution, status=status, date=date,
                                              date_of_end=date_of_end)
    new.save()


def sync_status(curs):
    existed = StatusOfVictimInPers.objects.all().values_list('id', flat=True)
    proposed = Tables("Статус в переслідуванні", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add__status(proposed.items[id_p])


def add_new_act(obj):
    # # ['Код_акт', 'Тіп порушення', 'Причетна організация', 'Початок', 'Закінчення',
    # 'Обставини', 'Місце', 'Переслідування', 'Стаття Римського статуту', 'Порушені права',
    # 'Апелляція', '№ справи в суді', 'Судове рішення',
    # 'Тип вироку', 'Років', 'Місяців', 'Діб', 'Штраф', 'Примусови роботи', 'Примітки']
    ids = obj.Код_акт
    persecution_id = obj.Переслідування
    persecution = Persecution.objects.get(pk=persecution_id) if persecution_id else None
    date = trans_date(obj.Початок)
    date_of_end = trans_date(obj.Закінчення)
    type_of_act = obj.__dict__['Тіп порушення']
    appeal_id = obj.Апелляція
    appeal = None
    if appeal_id:
        try:
            appeal = Act.objects.get(pk=appeal_id)
        except:
            # проверка на ошибку внесения, при которой апелляция вносится до информции о рассмотрении в первой инстанции
            return True
    case_num = obj.__dict__['№ справи в суді']
    if case_num and '#' in case_num:
        case_num = case_num.split('#')[0]
    case_decision = obj.__dict__['Судове рішення']
    sentence = obj.__dict__['Тип вироку']
    year_sentence = obj.__dict__['Років']
    month_sentence = obj.__dict__['Місяців']
    day_sentence = obj.__dict__['Діб']
    penalty_sentence = obj.__dict__['Штраф']
    work_sentence = obj.__dict__['Примусови роботи']
    overview = obj.__dict__['Примітки']

    new = Act.objects.create(id=ids, date=date, date_of_end=date_of_end, persecution=persecution,
                             type_of_act=type_of_act, appeal=appeal, сase_num=case_num, сase_decision=case_decision,
                             sentence=sentence, year_sentence=year_sentence, month_sentence=month_sentence,
                             day_sentence=day_sentence, penalty_sentence=penalty_sentence, work_sentence=work_sentence,
                             overview=overview)
    new.save()

    organisation_id = obj.__dict__['Причетна організация']
    organisation = Organisation.objects.get(pk=organisation_id) if organisation_id else None
    if organisation:
        new_oia = OrganisationInAct.objects.create(organisation=organisation,act=new)
        new_oia.save()

    raw_rights = obj.__dict__['Порушені права']
    if raw_rights:
        raw_rights = raw_rights.split(';')
        for rght_id in raw_rights:
            print(ids)
            right = H_Rights.objects.get(pk=rght_id)
            new_via = ViolationInAct.objects.create(act=new, rights=right)
            new_via.save()


def sync_act(curs):
    again = False
    existed = Act.objects.all().values_list('id', flat=True)
    proposed = Tables("Акт", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        new_org = add_new_act(proposed.items[id_p])
        if new_org:
            again = True
    return again


def add_new_person_in_act(obj):
    # ['Код', 'Людина', 'Акт', 'Статус', 'Роль', 'Опис']
    ids = obj.Код
    person_id = obj.Людина
    person = Person.objects.get(pk=person_id)
    act_id = obj.Акт
    act = Act.objects.get(pk=act_id)
    status_in_act = obj.Статус
    role = obj.Роль
    new = PersonInAct.objects.create(id=ids, person=person, act=act, status_in_act=status_in_act,
                                              role=role)
    new.save()
    pass

def sync_person_in_act(curs):
    existed = PersonInAct.objects.all().values_list('id', flat=True)
    proposed = Tables("Актори акту", curs)
    proposed.add_all_items()
    new_items = (ids for ids in proposed.items if ids not in existed)
    for id_p in new_items:
        try:
            add_new_person_in_act(proposed.items[id_p])
        except:
            continue
            # print(id_p)


def add_new_depr_liberty(obj):
    # ['Код_мпв', 'Переслідування', 'Місце позбавлення волі', 'початок', 'закінчення', 'місце перебування',
    # 'Статус перебування', 'примітки']
    ids = obj.Код_мпв
    persecution_id = obj.Переслідування
    persecution = Persecution.objects.get(pk=persecution_id) if persecution_id else None
    organisation_id = obj.__dict__['Місце позбавлення волі']
    organisation = Organisation.objects.get(pk=organisation_id) if organisation_id else None
    date = trans_date(obj.початок)
    date_of_end = trans_date(obj.закінчення)
    condition = obj.__dict__['місце перебування']
    status = obj.__dict__['Статус перебування']
    overview = obj.примітки
    new = Depriving_Liberty.objects.create(id=ids, persecution=persecution, organisation=organisation,
                                           date=date, date_of_end=date_of_end, condition=condition, status=status,
                                           overview=overview)
    new.save()


def sync_depr_liberty(curs):
    existed = Depriving_Liberty.objects.all().values_list('id', flat=True)

    for depr_id in existed:             # Удаление всех старых записей, чтобы не проводить сверку каждой на изменения
        current = Depriving_Liberty.objects.get(pk=depr_id)
        current.delete()

    proposed = Tables("Місце позбавлення волі", curs)
    proposed.add_all_items()
    new_items = [ids for ids in proposed.items if ids not in existed]
    for id_p in new_items:
        add_new_depr_liberty(proposed.items[id_p])


def synch():
    curs = connect_to_base()
    # name_of_tables = list(curs.execute('SELECT name from sqlite_master where type= "table"'))
    # print('name_of_tables begin', name_of_tables)
    sync_persons(curs)
    sync_cases(curs)
    sync_structure(curs)
    sync_h_rights(curs)
    again = True
    stop = 0
    while again:
        stop += 1
        again = sync_organisation(curs)
        if stop == 10:
            break
    sync_place_of_work(curs)
    sync_article(curs)
    sync_persecution(curs)
    # check_article_in_persecution(curs) # нужно создать, но пока отложил, нужно проверять каждое преследование
    sync_status(curs)
    again_act = True
    stop = 0
    while again_act:
        stop += 1
        again_act = sync_act(curs)
        if stop == 10:
            break
    sync_person_in_act(curs)
    sync_depr_liberty(curs)

if __name__ == '__main__':
    synch()
