from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import authentication, permissions

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# from .serializers import VictimSerializer
from .forms import UserRegistrationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
import datetime

from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from .models import *
from .serializers import *
from django.core.paginator import Paginator

from .synch.synchronization import synch
from .utilites.utils import find_pers_with_current_deprivation, make_filter_act_forms, filter_acts, \
    get_persecution_inf, make_filter_persecution_forms, filter_persecution, case_statistic, create_sentence_text

from .utilites.utils import permission_level, get_actors_in_permission_level, get_subjects_in_permission_level, \
    get_acts_in_permission_level, get_current_prisoners, get_persecutions_in_permission_level, \
    get_victims_in_permission_level

from .utilites.chart_inf import persecution_all_statistic, persecution_month_statistic, deprivation_statistic, \
    act_year_statistic

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

def get_attr(obj):
    # добавление только существующих атрибутов объекта
    obj_attr = []
    for attr in obj.__dict__.keys():
        if attr in ('_state', 'id', 'photo', 'name') or type((obj.__dict__[attr])) is 'int':
            continue
        if (obj.__dict__[attr]):
            obj_attr.append(obj.__dict__[attr])
    return obj_attr


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Token.objects.create(user=new_user)


            return render(request, 'sitedb/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'sitedb/register.html', {'user_form': user_form})


def index(request):
    # Number of visits to this view, as counted in the session variable.
    # num_visits = request.session.get('num_visits', 0)
    # request.session['num_visits'] = num_visits + 1
    #
    # # Render the HTML template index.html with the data in the context variable.
    current_user = request.user
    data = {'num_visits': 4}  # num_visits appended

    # for user in User.objects.all():
    #     Token.objects.get_or_create(user=user)

    if request.method == 'POST':
        # synch()
        pass
    data['persecution'] = get_persecutions_in_permission_level(request)
    data['victims'] = get_victims_in_permission_level(request)
    data['prisoners'] = Depriving_Liberty.objects.filter(date__isnull=False,
                                                         date_of_end__isnull=True,
                                                         persecution__in=data['persecution'])
    data['acts'] = get_acts_in_permission_level(request)
    Violations = {}
    for right in H_Rights.objects.all():
        Violations[right.rights] = right.violationinact_set.all().values('act')
    data['violations'] = Violations
    data['acts'] = get_acts_in_permission_level(request)

    if request.method == 'GET':
        if 'chart' in request.GET:
            dt_cr = persecution_all_statistic(data['persecution'], 'УК')
            dt_pers = {}
            chart_name = "Политически мотивированные уголовные преследования"
            dt_pers[chart_name] = [["Год", "Уголовные преследования", "Приговоры по уголовным делам"]]
            for year in dt_cr.keys():
                dt_pers[chart_name].append([year, dt_cr[year][0], dt_cr[year][1]])
            return JsonResponse(dt_pers, safe=False)

        if 'chartCriminal' in request.GET:
            depr = persecution_all_statistic(data['persecution'], 'УК')
            dt_pers = {}
            dt_pers["labels"] = [str(year) for year in depr]
            dt_pers["datasets"] = []
            data_set_1 = {}
            data_set_1['label'] = "Политически мотивированные уголовные преследования"
            data_set_1['data'] = [depr[year] for year in depr]
            data_set_1['borderColor'] = 'rgb(88, 77, 192)'
            dt_pers["datasets"].append(data_set_1)
            return JsonResponse(dt_pers, safe=False)

        if 'chart_adm' in request.GET:
            dt_ad = persecution_all_statistic(data['persecution'], 'КоАП')
            dt_pers = {}
            chart_name = "Политически мотивированные административные преследования"
            dt_pers[chart_name] = [["Год", "Административные преследования", "Постановления производствам"]]
            for year in dt_ad.keys():
                dt_pers[chart_name].append([year, dt_ad[year][0], dt_ad[year][1]])
            return JsonResponse(dt_pers, safe=False)

        if 'chart_depr' in request.GET:
            """
            запрос пр построении Google графика лишенных свободы
            """
            dt_depr = {}
            chart_name = "Лишения свободы в политически мотивированных уголовных преследованиях"
            dt_depr[chart_name] = [["Год", "Лишения свободы за год", "Количество лишенных свободы в конце года"]]
            crim_pers = data['persecution'].filter(type_of_pers='УК')
            depr = deprivation_statistic(crim_pers)
            for d in depr:
                dt_depr[chart_name].append([d, depr[d][0],  depr[d][1]])
            return JsonResponse(dt_depr, safe=False)


        if 'chartDepr' in request.GET:
            dt_depr = {}
            crim_pers = data['persecution'].filter(type_of_pers='УК')
            depr = deprivation_statistic(crim_pers)
            dt_depr["labels"] = [str(year) for year in depr]
            dt_depr["datasets"] = []
            data_set_1 = {}
            data_set_1['label'] = "Лишения свободы за год"
            data_set_1['data'] = [depr[year][0] for year in depr]
            data_set_1['borderColor'] = 'rgb(88, 77, 192)'
            dt_depr["datasets"].append(data_set_1)

            data_set_2 = {}
            data_set_2['label'] = "Количество лишенных свободы в конце года"
            data_set_2['data'] = [depr[year][1] for year in depr]
            data_set_2['borderColor'] = 'rgb(192, 77, 88)'
            dt_depr["datasets"].append(data_set_2)
            return JsonResponse(dt_depr, safe=False)


        if 'chartDetention' in request.GET:
            data = act_year_statistic(acts=data['acts'], ch_year=2021, type_of_act='Затримання')
            dt_pers = {}
            dt_pers["labels"] = [str(m) for m in range(1,13)]
            dt_pers["datasets"] = []
            data_set = {}
            data_set['label'] = "Количество задержаний в Крыму в %s году" % 2021
            data_set['data'] = [data[key] for key in data]
            data_set['borderColor'] = 'rgb(192, 77, 88)'
            dt_pers["datasets"].append(data_set)

            return JsonResponse(dt_pers, safe=False)
            pass

    return render(request, 'sitedb/index.html', context=data)


class PersonsView(generic.ListView):
    model = Person
    template_name = 'sitedb/persons.html'
    paginate_by = 24

    def get_queryset(self, **kwargs):
        person_rest = get_subjects_in_permission_level(self.request).order_by('name')
        request_list = self.request.GET.keys()
        if 'q' in request_list:
            search_request = self.request.GET['q']
            person_rest = person_rest.filter(name__contains=search_request)
        return person_rest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context ['rest'] = self.get_queryset()
        taken_request = None
        if self.request.GET.keys():
            taken_request = self.request.get_full_path()
            if 'page' in taken_request:
                taken_request = taken_request.split('&')
                taken_request = ('&').join(taken_request[:-1])
        context['taken_request'] = taken_request
        return context


class PersonsDetailView(generic.DetailView):
    model = Person
    template_name = 'sitedb/person_home.html'
    contex_object_name = 'one_person'

    def get_queryset(self):
        return get_subjects_in_permission_level(self.request)

    def get_context_data(self, **kwargs):
        obj = self.object
        context = super().get_context_data(**kwargs)
        obj.type = 'Person'
        # добавление только существующих атрибутов объекта
        obj_attr = get_attr(obj)
        # Call the base implementation first to get a context

        # расположение фильтров для выборки информации на странице персонажа
        p_level = permission_level(self.request)
        persecutions_of_person = obj.persecution_set.filter(permission_level__lt=(p_level + 1))  # преследования против персонажа
        if persecutions_of_person:
            for persecution in persecutions_of_person:
                get_persecution_inf(persecution)
            # лишения свободы в рамках преследований
            deprivings = Depriving_Liberty.objects.filter(persecution__in=persecutions_of_person).order_by('date')
            if deprivings:
                context['deprivings'] = deprivings
                for depr in deprivings:
                    if depr.date and not depr.date_of_end:
                        obj.depr = depr  # текущее лишение свободы

            context['p_of_p'] = persecutions_of_person
        p_acts = get_acts_in_permission_level(self.request)
        violation_of_person = obj.personinact_set.filter(status_in_act="Винний", act__in=p_acts)
        # преследования которые совершал персонаж и на просмотр которых есть допуск пользователя

        if violation_of_person:
            context['v_of_p'] = violation_of_person

        place_of_work = obj.placeofwork_set.all()
        if place_of_work:
            context['place_of_work'] = place_of_work

        return context


class VictimsView(PersonsView):
    template_name = 'sitedb/victims.html'

    def get_queryset(self, **kwargs):
        p_level = permission_level(self.request)  # уровень допуска пользователя
        self.person_rest = super().get_queryset(**kwargs)
        self.acts_rest = filter_acts(self.request)
        pers_with_acts = self.acts_rest.values('persecution_id')
        self.persecution_rest = Persecution.objects.all().filter(id__in=pers_with_acts,
                                                                 permission_level__lt=(p_level+1))
        victim_total_list = self.persecution_rest.values('victim_id')  # получает весь списоr Id жертв c актами
        person_total_rest = Person.objects.filter(id__in=victim_total_list)  # получает весь список  жертв c актами
        self.total = len(person_total_rest)
        #
        self.persecution_rest = filter_persecution(self.request, self.persecution_rest)
        #
        request_list = self.request.GET.keys()
        self.rest_form = False
        if 'allpers' in request_list:
            self.rest_form = True
        #
        victim_list = self.persecution_rest.values('victim_id')
        self.person_rest = self.person_rest.filter(id__in=victim_list)
        return self.person_rest.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.total  # все пострадавшие в преследованиях
        context['selected'] = len(self.person_rest)
        context['form'] = make_filter_persecution_forms(self.persecution_rest)
        context['act_form'] = make_filter_act_forms(self.acts_rest)
        context['rest_form'] = self.rest_form

        return context


class GuiltyView(LoginRequiredMixin, PersonsView):
    template_name = 'sitedb/guilty.html'

    def get_queryset(self, **kwargs):
        person_rest = super().get_queryset(**kwargs)
        acts_in_persc_total = get_acts_in_permission_level(self.request)
        guilty_total_list = PersonInAct.objects.filter(status_in_act="Винний",
                                                       act__in=acts_in_persc_total).values('person_id')
        person_total_rest = Person.objects.filter(id__in=guilty_total_list).order_by('name')
        self.total = len(person_total_rest)  # все субъекты - виновные в актах

        self.persecution_rest = filter_persecution(self.request)  # выборка преследований по фильтру в запросе
        acts_in_persc = Act.objects.filter(persecution__in=self.persecution_rest)
        self.acts_rest = filter_acts(self.request, acts_in_persc)

        request_list = self.request.GET.keys()

        guilty_list = guilty_total_list.filter(act__in=self.acts_rest).values('person_id')
        person_rest = person_rest.filter(id__in=guilty_list).order_by('name')

        if 'Гражданство' in request_list:
            data = self.request.GET.getlist('Гражданство')
            person_rest = person_rest.filter(citizenship__in=data)

        organisation_rest = Organisation.objects.all()
        pow = False  # Флаг применения фильтра по месту работы,
        # коряво хочется красивей, без него не показывет виновных без места работы (адвокаты, самообоорона и т.п.)
        if 'Структура' in request_list:
            pow = True
            data = self.request.GET.getlist('Структура')
            organisation_rest = organisation_rest.filter(srtucture__in=data)

        if 'Место работы' in request_list:
            pow = True
            data = self.request.GET.getlist('Место работы')
            organisation_rest = organisation_rest.filter(short_name__in=data)
        if pow:
            pers_in_org = PlaceOfWork.objects.filter(оrganisation__in=organisation_rest).values('person_id')
            person_rest = person_rest.filter(id__in=pers_in_org).order_by('name')

        return person_rest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person_rest = self.get_queryset()
        context['total'] = self.total  # все пострадавшие в преследованиях
        context['selected'] = len(person_rest)  # все субъекты - виновные в актах после фильтрации
        context['form'] = make_filter_persecution_forms(self.persecution_rest, with_status=False)
        context['act_form'] = make_filter_act_forms(self.acts_rest)

        organisation_id_rest = set(PlaceOfWork.objects.filter(person__in=person_rest).values_list('оrganisation',
                                                                                                  flat=True))
        organisation_rest = Organisation.objects.filter(id__in=organisation_id_rest)

        context['sec_form'] = {"Гражданство": set((glt.citizenship, glt.citizenship)
                                                  for glt in person_rest),
                               "Структура": set((org.srtucture.id, org.srtucture)
                                                for org in organisation_rest),
                               "Место работы": ((org.short_name, org.short_name)
                                                for org in organisation_rest)}

        return context


class CasesView(generic.ListView):
    model = Case
    template_name = 'sitedb/cases-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rest'] = self.get_queryset()
        context['head'] = 'Кейсы'
        return context

    def get_queryset(self, **kwargs):
        cases = Case.objects.all().order_by('name')
        if 'q' in self.request.GET.keys():
            cases = cases.filter(name__contains=self.request.GET['q'])
        return cases


class CaseDetailView(generic.DetailView):
    model = Case

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        pers = self.context['persecutions']
        if 'chartCriminal' in self.request.GET.keys():
            depr = persecution_all_statistic(pers)
            dt_pers = {}
            dt_pers["labels"] = [str(year) for year in depr]
            dt_pers["datasets"] = []
            data_set_1 = {}
            data_set_1['label'] = "Количество возбужденных дел в рамках кейса"
            data_set_1['data'] = [depr[year] for year in depr]
            data_set_1['borderColor'] = 'rgb(88, 77, 192)'
            dt_pers["datasets"].append(data_set_1)
            return JsonResponse(dt_pers, safe=False)

        if 'chartMonth' in request.GET:
            dt_pers = {}
            dt_pers["labels"] = [str(m) for m in range(1,13)]
            dt_pers["datasets"] = []
            r = 250
            g = 120
            b = 0
            for y in range(2016, 2022):
                print(y)
                step = 10
                depr = persecution_month_statistic(persecutions=pers, year=y)
                data_set = {}
                data_set['label'] = "Количество возбужденных дел за уклонение \n от службы в ВС РФ в %s году" % y
                data_set['data'] = [depr[y] for y in depr]
                data_set['borderColor'] = 'rgb(%s, %s, %s)' %(r, g, b)
                print (data_set)
                dt_pers["datasets"].append(data_set)
                r -=step*3
                g -=step
                b +=step*3
            dt_pers
            return JsonResponse(dt_pers, safe=False)
        return response

    def get_context_data(self, **kwargs):
        p_level = permission_level(self.request)  # уровень допуска пользователя
        obj = self.object
        self.context = super().get_context_data(**kwargs)
        case_statistic(obj)
        self.context['head'] = obj.name
        persecution_in_case = obj.persecution_set.filter(permission_level__lt=(p_level+1))
        for persecution in persecution_in_case:
            get_persecution_inf(persecution)
        self.context['persecutions'] = persecution_in_case
        return self.context


class ActsListView(LoginRequiredMixin, generic.ListView):
    model = Act
    paginate_by = 24

    def get_queryset(self, **kwargs):
        total = get_acts_in_permission_level(self.request)
        self.total = (len(total))
        self.persecution_rest = filter_persecution(self.request)
        self.acts_rest = total.filter(persecution__in=self.persecution_rest)
        self.acts_rest = filter_acts(self.request, self.acts_rest)
        return self.acts_rest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.total                   # все акты
        context['selected'] = len(self.acts_rest)
        context['form'] = make_filter_persecution_forms(self.persecution_rest)
        context['act_form'] = make_filter_act_forms(self.acts_rest)
        taken_request = None
        if self.request.GET.keys():
            taken_request = self.request.get_full_path()
            if 'page' in taken_request:
                taken_request = taken_request.split('&')
                taken_request = ('&').join(taken_request[:-1])
        context['taken_request'] = taken_request
        return context


class ActDetailView(generic.DetailView):
    model = Act

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object.sentence:
            context['sentence_text'] = create_sentence_text(self.object)
        return context


class ArticleListView(generic.ListView):
    model = Article
    paginate_by = 24


class ArticleDetailView(generic.DetailView):
    model = Article

    def get_context_data(self, **kwargs):
        obj = self.object
        context = super().get_context_data(**kwargs)
        context['head'] = obj.parts
        persecutions = get_persecutions_in_permission_level(self.request)
        persecution_with_article = [per.persecution for per in obj.articlesinpersecution_set.filter(persecution__in=persecutions)]
        for per in persecution_with_article:
            get_persecution_inf(per)
        context['persecutions'] = persecution_with_article

        return context


class PersecutionListView(LoginRequiredMixin, generic.ListView):
    model = Persecution
    paginate_by = 20

    def get_queryset(self, **kwargs):
        self.persecution_rest = get_persecutions_in_permission_level(self.request)
        self.total = len(self.persecution_rest)
        self.persecution_rest = filter_persecution(self.request, self.persecution_rest)
        return self.persecution_rest

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if 'prs' in self.request.GET.keys():
            pers = self.persecution_rest.get(id=int(self.request.GET['prs']))
            get_persecution_inf(pers)
            actors = pers.guilty
            data = dict((p.id, p.name) for p in actors)
            return JsonResponse(data, safe=False)
        else:
            return response

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['total'] = self.total
        context['selected'] = len(self.persecution_rest)
        context['form'] = make_filter_persecution_forms(self.persecution_rest)
        context['rest'] = self.get_queryset()
        taken_request = None
        if self.request.GET.keys():
            taken_request = self.request.get_full_path()
            if 'page' in taken_request:
                taken_request = taken_request.split('&')
                taken_request = ('&').join(taken_request[:-1])
        context['taken_request'] = taken_request

        return context


class OrgListView(generic.ListView):
    model = Organisation
    template_name = 'sitedb/org_list.html'
    paginate_by = 24

    def get_queryset(self, **kwargs):
        org_rest = Organisation.objects.all()
        request_list = self.request.GET.keys()
        print(request_list)
        depr_facilities = Depriving_Liberty.objects.filter(date__isnull=False,
                                                           date_of_end__isnull=True).values('organisation_id')
        prisons = org_rest.filter(id__in=depr_facilities)

        self.rest_form = False
        self.prison_form = False
        if 'allpers' in request_list:
            self.rest_form = True
            org_rest = org_rest.filter(prison=True)
            if 'allprison' in request_list:

                org_rest = prisons
                self.prison_form = True
        if 'q' in request_list:
            search_request = self.request.GET['q']
            org_rest = org_rest.filter(short_name__contains=search_request)

        if 'Структура' in request_list:
            search_request = self.request.GET['Структура']
            org_rest = org_rest.filter(srtucture__in=search_request)

        for org in org_rest:
            if org in prisons:
                org.deprivings = len(get_current_prisoners(org))
        return org_rest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rest'] = self.get_queryset()
        context['rest_form'] = self.rest_form
        context['prison_form'] = self.prison_form
        taken_request = None
        context['sec_form'] = {"Структура": set((org.srtucture.id, org.srtucture)
                                                for org in context['rest'])}
        if self.request.GET.keys():
            taken_request = self.request.get_full_path()
            if 'page' in taken_request:
                taken_request = taken_request.split('&')
                taken_request = ('&').join(taken_request[:-1])
        context['taken_request'] = taken_request
        return context

class OrgDetailView(generic.DetailView):
    model = Organisation
    template_name = 'sitedb/org_detail.html'

    def get_context_data(self, **kwargs):
        obj = self.object
        context = super().get_context_data(**kwargs)
        context['head'] = obj.short_name
        actors = get_actors_in_permission_level(self.request)
        context['staff'] = obj.placeofwork_set.filter(person__in=actors)
        context['prisoner'] = obj.depriving_liberty_set.filter(date__isnull=False, date_of_end__isnull=True)
        return context





class ApiMixinListAuth(ListCreateAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]


class SingleApiMixinListAuth(RetrieveUpdateDestroyAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]


class PersonsViewAPI(ApiMixinListAuth):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    # def perform_create(self, serializer):
    #     serializer.save(data=self.request.data)
    #
    def perform_update(self, serializer):
        serializer.save(data=self.request.data)


class SinglePersonsViewAPI(SingleApiMixinListAuth):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class StructuresViewAPI(ApiMixinListAuth):
    queryset = Structure.objects.all()
    serializer_class = SrtuctureSerializer


class SingleStructureViewAPI(SingleApiMixinListAuth):
    queryset = Structure.objects.all()
    serializer_class = SrtuctureSerializer


class CasesViewAPI(ApiMixinListAuth):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class SingleCaseViewAPI(SingleApiMixinListAuth):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


class OrganisationsViewAPI(ApiMixinListAuth):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer


class SingleOrganisationViewAPI(SingleApiMixinListAuth):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer


class PlaceOfWorkViewAPI(ApiMixinListAuth):
    queryset = PlaceOfWork.objects.all()
    serializer_class = PlaceOfWorkSerializer


class SinglePlaceOfWorkViewAPI(SingleApiMixinListAuth):
    queryset = PlaceOfWork.objects.all()
    serializer_class = PlaceOfWorkSerializer


class ArticleViewAPI(ApiMixinListAuth):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class SingleArticleViewAPI(SingleApiMixinListAuth):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


class PersecutionViewAPI(ApiMixinListAuth):
    queryset = Persecution.objects.all()
    serializer_class = PersecutionSerializer


class SinglePersecutionViewAPI(SingleApiMixinListAuth):
    queryset = Persecution.objects.all()
    serializer_class = PersecutionSerializer


class AiPViewAPI(ApiMixinListAuth):
    queryset = ArticlesInPersecution.objects.all()
    serializer_class = AiPSerializer


class SingleAiPViewAPI(SingleApiMixinListAuth):
    queryset = ArticlesInPersecution.objects.all()
    serializer_class = AiPSerializer


class RightsViewAPI(ApiMixinListAuth):
    queryset = H_Rights.objects.all()
    serializer_class = RightsSerializer


class SingleRightsViewAPI(SingleApiMixinListAuth):
    queryset = H_Rights.objects.all()
    serializer_class = RightsSerializer


class StatusViewAPI(ApiMixinListAuth):
    queryset = StatusOfVictimInPers.objects.all()
    serializer_class = StatusSerializer


class SingleStatusViewAPI(SingleApiMixinListAuth):
    queryset = StatusOfVictimInPers.objects.all()
    serializer_class = StatusSerializer


class ActViewAPI(ApiMixinListAuth):
    queryset = Act.objects.all()
    serializer_class = ActsSerializer


class SingleActViewAPI(SingleApiMixinListAuth):
    queryset = Act.objects.all()
    serializer_class = ActsSerializer


class ViAAPI(ApiMixinListAuth):
    queryset = ViolationInAct.objects.all()
    serializer_class = ViASerializer


class SingleViAAPI(SingleApiMixinListAuth):
    queryset = ViolationInAct.objects.all()
    serializer_class = ViASerializer


class PersonInActAPI(ApiMixinListAuth):
    queryset = PersonInAct.objects.all()
    serializer_class = PersonInActSerializer


class SinglePersonInActAPI(SingleApiMixinListAuth):
    queryset = PersonInAct.objects.all()
    serializer_class = PersonInActSerializer


class DeprivingAPI(ApiMixinListAuth):
    queryset = Depriving_Liberty.objects.all()
    serializer_class = DerpivingSerializer


class SingleDeprivingAPI(SingleApiMixinListAuth):
    queryset = Depriving_Liberty.objects.all()
    serializer_class = DerpivingSerializer