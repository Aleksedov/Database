from django.db import models

"""
admin
1111111
"""


class Person(models.Model):
    name = models.CharField('ФИО', max_length=250)
    date_of_birth = models.DateField('Дата рождения', blank=True, null=True)
    biography = models.TextField('биография', blank=True, null=True)
    photo = models.ImageField(upload_to='sitedb/images/person', default='images/Noface.JPG', null=True)
    citizenship = models.CharField('гражданство', max_length=250, blank=True, null=True)

    def __str__(self):
        return self.name


class Structure(models.Model):
    name = models.CharField('короткое название', max_length=50)
    overwrite = models.TextField('описание', blank=True, null=True)
    logo = models.ImageField(upload_to='sitedb/images/structure', default='images/Nologo.JPG', null=True)
    def __str__(self):
        return self.name


class Organisation(models.Model):
    short_name = models.CharField('короткое название', max_length=250)
    full_name = models.CharField('полное название', max_length=250, blank=True, null=True)
    address = models.CharField('адрес', max_length=250, blank=True, null=True)
    phonenumber = models.CharField('телефон', max_length=20, blank=True, null=True)
    site_org = models.URLField('сайт', max_length=250, blank=True, null=True)
    Email = models.URLField('E-mail', max_length=250, blank=True, null=True)
    srtucture = models.ForeignKey(Structure, on_delete=models.CASCADE, blank=True, null=True)
    prison = models.BooleanField('место лишения свободы', default=False, blank=True, null=True)
    state = models.CharField('страна расположения', max_length=250, blank=True, null=True)
    main_org = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.short_name


class PlaceOfWork(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    оrganisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, blank=True, null=True)
    position = models.CharField('должность', max_length=250, blank=True, null=True)
    rank = models.CharField('звание', max_length=250, blank=True, null=True)
    date = models.DateField('начало работы', blank=True, null=True)
    date_of_end = models.DateField('прекращение работы', blank=True, null=True)
    notes = models.TextField('пометки', blank=True, null=True)


class Article(models.Model):
    """
    статья обвинения
    для оптимизации на этом этапе parts выглядит "222 ч.3",
    логичнее parts указать как числовое значение, но тогда нужен адаптер
    """

    codes_choices = [
        ('УК', 'Уголовный кодекс'),
        ('КоАП', 'Кодекс об административных правонарушениях')
    ]
    number = models.CharField('статья', max_length=10)
    parts = models.CharField('часть', max_length=20, blank=True, null=True)
    code = models.CharField('кодекс', max_length=10, choices=codes_choices, default='УК')
    title = models.TextField('название', blank=True, null=True)
    text = models.TextField('текст', blank=True, null=True)

    def __str__(self):
        return "ст.%s %s" % (self.parts, self.code)


class Case(models.Model):
    name = models.CharField('Дело', max_length=250)
    overview = models.TextField('описание', blank=True, null=True)
    photo = models.ImageField(upload_to='static/images/cases', default='images/Noface.JPG', blank=True, null=True)

    def __str__(self):
        return self.name


class Persecution(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, blank=True, null=True)
    victim = models.ForeignKey(Person, on_delete=models.CASCADE)
    type_of_pers = models.CharField('Тип преследования', max_length=20, blank=True, null=True)
    date = models.DateField('Дата преследования', max_length=10, blank=True, null=True)
    overview = models.TextField('описание', blank=True, null=True)
    permission_level = models.IntegerField('допуск', default=0)

    def __str__(self):
        return "%s_%s_%s" % (self.case,self.victim,self.type_of_pers)


class ArticlesInPersecution(models.Model):
    persecution = models.ForeignKey(Persecution, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


class H_Rights(models.Model):
    rights = models.CharField('Права свободы', max_length=150, unique=True)
    echr_article = models.CharField('статья', max_length=15, blank=True, null=True)
    content = models.TextField('описание', blank=True, null=True)

    def __str__(self):
        return self.rights


class StatusOfVictimInPers(models.Model):
    persecution = models.ForeignKey(Persecution, on_delete=models.CASCADE)
    status = models.CharField('статус', max_length=100, default='Підозрюваний')
    date = models.DateField('Дата начала статуса',max_length=10, blank=True, null=True)
    date_of_end = models.DateField('Окончание статуса',max_length=10, blank=True, null=True)

class Act(models.Model):
    """
    Акт преследования
    """
    date = models.DateField('Начало',max_length=10, blank=True, null=True)
    date_of_end = models.DateField('Окончание',max_length=10, blank=True, null=True)
    persecution = models.ForeignKey(Persecution, on_delete=models.CASCADE)
    type_of_act = models.CharField('тип акта преследования', max_length=150, blank=True, null=True)
    # Типы преследований в акте преследования (содержание под стражей, обыск и т.п.

    appeal = models.ForeignKey('self', null=True, on_delete=models.CASCADE)
    сase_num = models.CharField('номер дела в суде', max_length=100, blank=True, null=True)
    сase_decision = models.CharField('тип судебного решения', max_length=50, blank=True, null=True)
    sentence = models.CharField('тип приговора', max_length=50, blank=True, null=True)
    year_sentence = models.CharField('лет', max_length=2, blank=True, null=True)
    month_sentence = models.CharField('месяцев', max_length=2, blank=True, null=True)
    day_sentence = models.CharField('дней', max_length=4, blank=True, null=True)
    penalty_sentence = models.CharField('штраф', max_length=15, blank=True, null=True)
    work_sentence = models.CharField('принудительные работы', max_length=4, blank=True, null=True)
    text_sentence = models.TextField('текст приговора', blank=True, null=True)
    overview = models.TextField('описание', blank=True, null=True)

    def __str__(self):
        return "%s_%s_%s" % (self.date, self.persecution, self.type_of_act)


class ViolationInAct(models.Model):
    """
    Права нарушенные в акте преследования
    """
    act = models.ForeignKey(Act, on_delete=models.CASCADE)
    rights = models.ForeignKey(H_Rights, on_delete=models.CASCADE)


class PersonInAct(models.Model):
    """
    Участники в акте преследования
    """
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    act = models.ForeignKey(Act, on_delete=models.CASCADE)
    status_in_act = models.CharField('статус в акте', max_length=250, default="Винний")
    role = models.CharField('роль в акте', max_length=250, blank=True, null=True)

class OrganisationInAct(models.Model):
    """
    Участники в акте преследования
    """
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    act = models.ForeignKey(Act, on_delete=models.CASCADE)

class Depriving_Liberty(models.Model):
    """
    Лишения свободы в преследовании
    """
    persecution = models.ForeignKey(Persecution, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    date = models.DateField('Начало', max_length=10)
    date_of_end = models.DateField('Окончание', max_length=10, blank=True, null=True)
    condition = models.CharField('Умови', max_length=250, blank=True, null=True)  # ШИЗО, ПКТ, камера, палата
    status = models.CharField('Статус', max_length=250, blank=True, null=True)  # колония, содержание под стражей, арест, медчасть
    overview = models.TextField('описание', blank=True, null=True)

# Синхронизировано
# Не создано ссылки на акт, на работу, на лишение свободы, на статус в деле, на дело, на человека. соцсети и контанкты,
