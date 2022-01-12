def create_sentence_text(act):
    """

    :param act: акт с приговором
    :return: текст приговра в читаемом формате
    """
    text_sen = kind_sent(act.sentence) + term_sent(act)
    return text_sen

def kind_sent(sent):
    if "Умовне" in sent:
        return "Условное лишение свободы"
    if "суворого" in sent:
        return "Лишение свободы в колонии строгого режима"
    if "загальне" in sent:
        return "Лишение свободы в колонии общего режима"
    if "поселення" in sent:
        return "Лишение свободы в колонии-поселении"
    if "поселення" in sent:
        return "Лишение свободы в колонии-поселении"
    if "праця" in sent:
        return "Принудительные работы "
    if "арешт" in sent:
        return "Админинистративный арест"
    if "відтерм" in sent:
        return "Лишение свободы с одстрочной"
    if "Попередження" in sent:
        return "Предупреждение"
    if "Виправдан" in sent:
        return "Оправдан"
    if "Виправдан" in sent:
        return "Оправдан"
    return ""

def term_sent(act):
    text_sen = ""
    if 'ПВ' in act.sentence or "арешт" in act.sentence:
        text_sen+= " сроком "
        if act.year_sentence:
            if 0 < int(act.year_sentence) < 2:
                text_sen += act.year_sentence + " год, "
            elif 1 < int(act.year_sentence) < 5:
                text_sen += str(act.year_sentence)+ " года, "
            elif 4 < int(act.year_sentence):
                text_sen += str(act.year_sentence)+ " лет, "
        if act.month_sentence:
            if 0 < int(act.month_sentence) < 2:
                text_sen += str(act.month_sentence)+ " месяц, "
            elif 1 < int(act.month_sentence) < 5:
                text_sen += str(act.month_sentence)+ " месяца, "
            elif 4 < int(act.month_sentence):
                text_sen += str(act.month_sentence)+ " месяцев, "
        if act.day_sentence:
            if 0 < int(act.day_sentence) < 2:
                text_sen += str(act.day_sentence)+ " день, "
            elif 1 < int(act.day_sentence) < 5:
                text_sen += str(act.day_sentence)+ " дня, "
            elif 4 < int(act.day_sentence):
                text_sen += str(act.day_sentence)+ " дней, "
    if act.work_sentence:
        if 0 < int(act.work_sentence[-1]):
            text_sen += str(act.work_sentence)+ " часов, "

    if act.penalty_sentence:
        if int(act.penalty_sentence.split('.')[0]) > 0:
            text_sen += "Штраф - " + str(act.penalty_sentence) + " рублей. "

    return text_sen