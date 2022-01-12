from ..models import *
from django.db.models import Q

from datetime import datetime, date

from .sentence_text import create_sentence_text

def find_pers_with_current_deprivation():
    """
    Находит список преследований в которых на данных момент жертва лишена свободы
    :return: список преследований
    """
    pers = Depriving_Liberty.objects.filter(date__isnull=False, date_of_end__isnull=True)
    return pers


def get_persecution_inf(persecution):
    """
    собирает информацию о преследовании и вносит ее в преследование
    acts - список актов в преследловании
    guilty - список виновных в собраных актах
    sentence - если вынесен приговор, формирует текст приговора
    status - текущий статус в преследовании, если оно уголовное
    :return:
    """
    persecution.acts = persecution.act_set.all().order_by('date')
    person_in_act = PersonInAct.objects.filter(act__in=persecution.acts, status_in_act="Винний").values('person_id')
    persecution.guilty = Person.objects.filter(id__in=person_in_act)
    sent_act = get_sentence_of_persecution(persecution)
    if sent_act:
        persecution.sentence = sent_act
        persecution.sentence_text = create_sentence_text(sent_act)
    status = persecution.statusofvictiminpers_set.all().order_by('date').reverse()
    if status:
        persecution.status = status[0]


def get_persecutions_with_sentence(persecutions=None, date_from: date = None, date_to: date = None):
    """
    QuerySet преследований с имеющейся информацией о характере вынесенного приговора
    :param date_to: дата до которой должен быть вынесен приговор YYYY.MM.DD
    :param date_from: дата после которой должен быть вынесен приговор YYYY.MM.DD
    :param persecutions: заданный QuerySet преследований
    :return: list преследований c уже вынесенными приговорами
    """
    persecutions = persecutions if persecutions else Persecution.objects.all()
    if date_from and date_to:
        pers_with_sent = list(pers for pers in persecutions if get_sentence_of_persecution(pers)
                              and get_sentence_of_persecution(pers).date
                              and date_from <= get_sentence_of_persecution(pers).date <= date_to)
        return pers_with_sent
    if date_from:
        pers_with_sent = list(pers for pers in persecutions if get_sentence_of_persecution(pers)
                              and get_sentence_of_persecution(pers).date
                              and date_from <= get_sentence_of_persecution(pers).date)
        return pers_with_sent
    if date_to:
        pers_with_sent = list(pers for pers in persecutions if get_sentence_of_persecution(pers)
                              and get_sentence_of_persecution(pers).date
                              and get_sentence_of_persecution(pers).date <= date_to)
        return pers_with_sent
    pers_with_sent = list(pers for pers in persecutions if get_sentence_of_persecution(pers))
    return pers_with_sent


def get_sentence_of_persecution(persecution):
    """
    Получает последний акт преследования в котором есть приговор и как минимум его тип (штраф, лишение совбоды и т.п.
    :param persecution: проверяемое преследование
    :return: Получает акт приговора, или None
    """
    sentence = None
    sent_act = persecution.act_set.filter(sentence__isnull=False).order_by('date').reverse()
    if sent_act:
        sentence = sent_act[0]
    return sentence

def get_current_prisoners(org):
    """

    :param org: объект "организация"
    :return: QuerySet текущих лишений свободы в этой организации
    """
    if org.prison == False:
        return
    depr_persec = org.depriving_liberty_set.filter(date__isnull=False,
                                                   date_of_end__isnull=True).values('persecution_id')
    return  depr_persec


def take_request_keys(request):
    """
	Сбор всех ключей полученного запроса
	"""

    filtr_set = []
    if request.method == 'POST':
        r_m = request.POST
    else:
        r_m = request.GET
    for filtr in r_m.keys():
        if filtr in ('csrfmiddlewaretoken', 'page'):
            continue
        if r_m[filtr]:
            filtr_set.append(filtr)
    return filtr_set


def make_filter_persecution_forms(persecutions=None, with_status = True):
    """
    	Создаются списки для фильтров на основании переданного QeurySet преследований
    :param persecutions: QeurySet преследований
    :param form_list: список ключей которые должны повлятся в поле
    :return: словарь form фильров, с ключами - подписями для кнопок
    """

    if persecutions:
        case_of_p = persecutions.values('case_id')
        art_in_pers = ArticlesInPersecution.objects.filter(persecution__in=persecutions).values('article_id')
        stat_in_pers = set(StatusOfVictimInPers.objects.filter(persecution__in=persecutions).values_list('status',
                                                                                                         flat=True))
    else:
        case_of_p = Persecution.objects.all().values('case_id')
        art_in_pers = ArticlesInPersecution.objects.all().values('article_id')
        stat_in_pers = set(StatusOfVictimInPers.objects.all().values_list('status', flat=True))

    form = {}
    form["Дела"] = Case.objects.filter(id__in=case_of_p).values_list('id', 'name')
    form["Преследования"] = set(persecutions.values_list('type_of_pers', 'type_of_pers'))
    form["Cтатьи"] = Article.objects.filter(id__in=art_in_pers).values_list('id', 'parts')
    if with_status:
        form["Статус в деле"] = [(i,i) for i in stat_in_pers]

    return form


def filter_persecution(request, short_list=None):
    """
	Фильтрация преследований на основании фильтров переданных в запросе "request"
	фильтруются все запросы если не передан короткий список short_list

    :param request: запрос
    :param short_list: сокращенный QuerySet преследований
    :return: QuerySet преследований после применения всех фильтров
    """
    p_level = permission_level(request)  # уровень допуска пользователя
    if request.method == 'POST':
        r_m = request.POST
    else:
        r_m = request.GET
    pers_list = short_list if short_list else Persecution.objects.filter(permission_level__lt=(p_level+1))
    filtr_set = take_request_keys(request)

    if 'q_pers' in filtr_set:
        search_request = r_m['q_pers']
        victims = Person.objects.filter(name__contains=search_request)
        pers_list = pers_list.filter(victim__in=victims)

    if 'allpers' in filtr_set:  # лишенные в данный момент свободы
        depr_persec = Depriving_Liberty.objects.filter(date__isnull=False, date_of_end__isnull=True,
                                                       persecution__in=pers_list).values('persecution_id')
        pers_list = pers_list.filter(id__in=depr_persec)


    if 'p_d_b' in filtr_set and r_m['p_d_b']:
        d = r_m['p_d_b'].split('-')
        d = list(int(i) for i in d)
        pers_list = pers_list.filter(date__gte=date(d[0], d[1], d[2]))

    if 'p_d_e' in filtr_set and r_m['p_d_e']:
        d = r_m['p_d_e'].split('-')
        d = list(int(i) for i in d)
        pers_list = pers_list.filter(date__lte=date(d[0], d[1], d[2]))
    #
    if 'Дела' in filtr_set:     # преследования по выбранным делам
        data = (int(i) for i in r_m.getlist('Дела'))
        pers_list = pers_list.filter(case__in=data)
    #
    if 'Преследования' in filtr_set: # сбор преследований по типу
        pers_list = pers_list.filter(type_of_pers__in=r_m.getlist('Преследования'))

    if 'Cтатьи' in filtr_set:   # сбор преследований в которых применялась статья
        data = (int(i) for i in r_m.getlist('Cтатьи'))
        pers_with_art = ArticlesInPersecution.objects.filter(article_id__in=data).values('persecution_id')
        pers_list = pers_list.filter(id__in=pers_with_art)

    if 'Статус в деле' in filtr_set:   # сбор преследований в которых применялась статья
        pers_with_stat = StatusOfVictimInPers.objects.filter(status__in=r_m.getlist('Статус в деле')).values('persecution_id')
        pers_list = pers_list.filter(id__in=pers_with_stat)

    return pers_list.order_by("date")


def make_filter_act_forms(acts=None):
    """
    Создает списки для фильтров на основании переданного QeurySet актов
    :param short_list: QeurySet актов
    :return: словарь form фильров, с ключами - подписями для кнопок
    """

    if acts:
        viol_in_acts = ViolationInAct.objects.filter(act__in=acts).values('rights_id')
    else:
        viol_in_acts = ViolationInAct.objects.all().values('rights_id')

    form = {}
    form["Нарушенные права"] = H_Rights.objects.filter(id__in=viol_in_acts).values_list('id', 'rights')

    return form


def filter_acts(request, short_list=None):
    """
    Отфильтровывает полученный QuerySet актов на основаниии фильтров переденных в запросе
    :param request: запрос
    :param short_list: сокращенный QuerySet актов
    :return: QuerySet актов после применения всех фильтров
    """
    if request.method == 'POST':
        r_m = request.POST
    else:
        r_m = request.GET
    acts_list = short_list if short_list else Act.objects.all()
    filtr_set = take_request_keys(request)

    if 'a_d_b' in filtr_set and r_m['a_d_b']:
        d = r_m['a_d_b'].split('-')
        d = list(int(i) for i in d)
        acts_list = acts_list.filter(date__gte=date(d[0], d[1], d[2]))

    if 'a_d_e' in filtr_set and r_m['a_d_e']:
        d = r_m['a_d_e'].split('-')
        d = list(int(i) for i in d)
        acts_list = acts_list.filter(date__lte=date(d[0], d[1], d[2]))

    if 'Нарушенные права' in filtr_set:   # сбор актов в которых нарушались заданные права
        data = (int(i) for i in r_m.getlist('Нарушенные права'))
        acts_with_viol = ViolationInAct.objects.filter(rights_id__in=data).values('act_id')
        acts_list = acts_list.filter(id__in=acts_with_viol)

    return acts_list.order_by("date")


def case_statistic(case):
    """
    Сорирает статистику по делу на текущую дату для отображения на странице дела
    :param case: объект Case
    """
    case.now = date.today()
    case.persecutions = case.persecution_set.all()
    case.sentence_text = []                                 #  все последние судебные решения с известным приговором
    case.last_acts = []                                     #  все последние судебные решения
    case.decisions = {}                                     #  все последние судебные решения по типу
    case.all_acts = []                                      #  все акты в деле
    case.pendings = []                                      #  все судебные решения еще на рассмотрении
    case.deprived = []                                      # Лишенные свободы в кейсе на данный момент
    case.deprived_total = []                                # Лишенные свободы в кейсе за весь период
    case.victims = []                                       # Фигуранты дела
    for persecution in case.persecutions:
        if not persecution.victim in case.victims:
            case.victims.append(persecution.victim)
        all_acts_in_pers = persecution.act_set.all()         #  все акты в преследовании
        for act in all_acts_in_pers:
            case.all_acts.append(act)
        last_decision = all_acts_in_pers.filter(сase_decision__isnull=False).order_by('date').reverse()
        if last_decision:                                    #  последнее вынесенное судебное решение в преследовании
            last_decision = last_decision[0]
            if not last_decision.сase_decision in case.decisions:
                case.decisions[last_decision.сase_decision] = []
            case.decisions[last_decision.сase_decision].append(persecution)
            case.last_acts.append(persecution)

        #  акты типа "судебное решение" без вынесенного еще решения
        pending = all_acts_in_pers.filter(type_of_act="Судове рішення", сase_decision__isnull=True)
        if pending:                                             #  судебное решение на рассмотрении в преследовании
            case.pendings.append(persecution)
        sent_act = all_acts_in_pers.filter(sentence__isnull=False).order_by('date').reverse()
        if sent_act:                                            #  судебное решение с приговором в преследовании
            case.sentence_text.append(persecution)
        deprivation = Depriving_Liberty.objects.filter(date__isnull=False,
                                         persecution=persecution)
        if deprivation:
            pers = deprivation[0].persecution
            case.deprived_total.append(pers)
            current_depr = deprivation.filter(date_of_end__isnull=True)
            if current_depr:
                case.deprived.append(pers)

        # deprivation = Depriving_Liberty.objects.filter(date__isnull=False, date_of_end__isnull=True,
        #                                  persecution=persecution)
def permission_level(request):
    """
    получает значение допуска на основании запроса
    :param request:
    :return: int - уровень допуска
    """
    current_user = request.user
    if not current_user.is_authenticated:
        return 0
    if current_user.is_staff:
        return 2
    return 1
    # print('is_authenticated', current_user.is_authenticated)
    # if current_user.is_authenticated:
    #     print('password', current_user.password)
    #     print('groups', current_user.groups.get().name)
    # print('is_staff', current_user.is_staff)
    # print('is_superuser', current_user.is_superuser)
    # print(current_user)


def get_persecutions_in_permission_level(request):
    """
    :return:  QuerySet преследований отображаемых в уровне допуска Пользователя
    """
    p_level = permission_level(request)
    return Persecution.objects.filter(permission_level__lt=(p_level + 1))


def get_victims_in_permission_level(request):
    """
    :return:  QuerySet "жертв в преследованиях" отображаемых в уровне допуска Пользователя
    """
    persecutions = get_persecutions_in_permission_level(request)
    victims = persecutions.values('victim')
    return Person.objects.filter(id__in=victims)


def get_acts_in_permission_level(request):
    """
    :return:  QuerySet act в преследованиях отображаемых в уровне допуска Пользователя
    """
    persecutions = get_persecutions_in_permission_level(request)
    return Act.objects.filter(persecution__in=persecutions)


def get_actors_in_permission_level(request):
    """
    Отбирает, только участников для соотвествующего уровня пользователя
        "Не зарегистритованный"  -только виновных в допустимых актых
        "Обычный"  - Всех в допустимых актах
        "Staff"  - Всех
    :return:  QuerySet "участники акта" отображаемых в уровне допуска Пользователя
    """
    p_level = permission_level(request)
    if p_level == 2:
        return PersonInAct.objects.all().values('person_id')
    act = get_acts_in_permission_level(request)
    if p_level == 0:
        return PersonInAct.objects.filter(status_in_act="Винний", act__in=act).values('person_id')
    return PersonInAct.objects.filter(act__in=act).values('person_id')


def get_subjects_in_permission_level(request):
    victims = get_victims_in_permission_level(request)
    actors = get_actors_in_permission_level(request)
    persons = Person.objects.filter(Q(id__in=victims) | Q(id__in=actors))
    return persons

def main():
    pass

    pass

if __name__ == '__main__':
    main()



