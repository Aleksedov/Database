from datetime import date
from sitedb.models import *

from .utils import get_persecutions_with_sentence

def persecution_all_statistic(persecutions=None, type_pers=None):
    """
    Статистка количества преследований
    :param persecutions: QuerySet преследований
    :param type_pers: Тип преследования "УК", "КоАП"
    :return: словарь (год : количество преследований, количество приговоров)
    """
    persecutions = persecutions if persecutions else Persecution.objects.all()
    if type_pers:
        persecutions = persecutions.filter(type_of_pers=type_pers)
    check_year = 2014
    today = date.today()
    data = {}
    while check_year <= 2021: # while check_year <= today.year: для включения в график текущего года
        date_to = date(check_year, 12, 31)
        date_from = date(check_year, 1, 1)
        pers_in_period = persecution_in_period(persecutions, type_pers, date_from, date_to)
        data[check_year] = 0
        if pers_in_period:
            data[check_year] = len(pers_in_period)
        check_year += 1
    return data


def persecution_in_period(persecutions=None, type_pers=None, date_from=None, date_to=None):
    """
    Преследования в периоде
    :param persecutions:    Изначальный список преследлований
    :param type_pers:       Тип преследваний
    :param date_from:       Начальная дата
    :param date_to:         Конечная дата
    :return:                Отфильтрованный список преследлований
    """
    persecutions = persecutions if persecutions else Persecution.objects.all()
    if type_pers:
        persecutions = persecutions.filter(type_of_pers=type_pers)
    if date_to:
        persecutions = persecutions.filter(date__lte=date_to)
    if date_from:
        persecutions = persecutions.filter(date__gte=date_from)
    return persecutions

def persecution_month_statistic(persecutions=None, type_pers:str=None, ch_year:int=None):
    """
    Статистка количества преследований
    :param persecutions: QuerySet преследований
    :param type_pers: Тип преследования "УК", "КоАП"
    :param year: год за который необходимо построить график
    :return: словарь (год : (месяц, количество преследований, количество приговоров))
    """
    persecutions = persecutions if persecutions else Persecution.objects.all()
    if type_pers:
        persecutions = persecutions.filter(type_of_pers=type_pers)
    if not ch_year:
        today = date.today()
        ch_year = today.year
    data = {}
    for m in range(1, 13):
        date_from = date(ch_year, m, 1)
        date_to = date(ch_year, m+1, 1) if m != 12 else date(ch_year+1, 1, 1)
        pers_in_period = persecution_in_period(persecutions, type_pers, date_from, date_to)
        key_m = '%s-%s' % (ch_year, m)
        data[key_m] = 0
        if pers_in_period:
            data[key_m] = len(pers_in_period)
    return data



def deprivation_statistic(persecutions=None):
    """
    Статистка  лишений свободы
    :param persecutions: QuerySet преследований
    :return: словарь (год; (лишений свободы за год, полит ЗК в конце года(или на сегодня))

    """
    persecutions = persecutions if persecutions else Persecution.objects.all()
    check_year = 2014
    today = date.today()
    data = {}

    while check_year <= 2021: # while check_year <= today.year: для включения в график текущего года
        # print(check_year)
        depr_in_year = 0
        total_depr = 0
        persecution_at_end_of_year = persecutions.filter(date__lte=date(check_year, 12, 31))
        # преследования начатые до конца года
        for pers in persecution_at_end_of_year:
            pers_deprs = pers.depriving_liberty_set.filter(date__isnull=False).order_by('date')
            if pers_deprs:
                pers_deprs = [depr for depr in pers_deprs]
                first_depr = pers_deprs[0].date.year
                if first_depr == check_year:
                    depr_in_year +=1
                    # print('Был задержан', pers.victim.name)
                if first_depr > check_year:
                    continue
                if not pers_deprs[-1].date_of_end:
                    # print('Остается лишенным свободы ',pers.victim.name)
                    total_depr += 1
                    continue
                last_depr = pers_deprs[-1].date_of_end.year
                if last_depr > check_year:
                    total_depr += 1
                    # print('Оставался лишенным свободыв конце года',pers.victim.name)
        data[check_year] = (depr_in_year, total_depr)
        check_year += 1
    return data


def acts_in_period(acts=None, type_of_act=None, date_from=None, date_to=None):
    """
    Преследования в периоде
    :param persecutions:    Изначальный список преследлований
    :param type_pers:       Тип преследваний
    :param date_from:       Начальная дата
    :param date_to:         Конечная дата
    :return:                Отфильтрованный список преследлований
    """
    acts = acts if acts else Act.objects.all()
    if type_of_act:
        acts = acts.filter(type_of_act=type_of_act)
    if date_to:
        acts = acts.filter(date__lte=date_to)
    if date_from:
        acts = acts.filter(date__gte=date_from)
    return acts


def act_year_statistic(acts=None, ch_year=None, type_of_act=None):
    acts = acts if acts else Act.objects.all()
    if type_of_act:
        acts = acts.filter(type_of_act=type_of_act)
    ch_year = ch_year if ch_year else date.today().year
    data = {}
    for m in range(1, 13):
        date_from = date(ch_year, m, 1)
        date_to = date(ch_year, m+1, 1) if m != 12 else date(ch_year+1, 1, 1)
        acts_in_p = acts_in_period(acts, type_of_act, date_from, date_to)
        key_m = '%s-%s' % (ch_year, m)
        data[key_m] = 0
        if acts_in_p:
            data[key_m] = len(acts_in_p)
    return data

def main():
    persecution_all_statistic()

if __name__ == '__main__':
    main()

