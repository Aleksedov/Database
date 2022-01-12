from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('persons/', views.PersonsView.as_view(), name='persons'),
    path('victims/', views.VictimsView.as_view(), name='victims'),
    path('guilty/', views.GuiltyView.as_view(), name='guilty'),
    path('cases/', views.CasesView.as_view(), name='cases'),
    path('persons/<int:pk>', views.PersonsDetailView.as_view(), name='one_person'),
    path('cases/<int:pk>', views.CaseDetailView.as_view(), name='one_case'),
    path('acts/', views.ActsListView.as_view(), name='acts'),
    path('acts/<int:pk>', views.ActDetailView.as_view(), name='one_act'),
    path('articles/', views.ArticleListView.as_view(), name='articles'),
    path('articles/<int:pk>', views.ArticleDetailView.as_view(), name='one_article'),
    path('organisations/', views.OrgListView.as_view(), name='organisations'),
    path('organisations/<int:pk>', views.OrgDetailView.as_view(), name='one_org'),
    path('persecutions/', views.PersecutionListView.as_view(), name='persecutions'),
    path('persons_api/', views.PersonsViewAPI.as_view()),
    path('persons_api/<int:pk>', views.SinglePersonsViewAPI.as_view()),
    path('structures_api/', views.StructuresViewAPI.as_view()),
    path('structures_api/<int:pk>', views.SingleStructureViewAPI.as_view()),
    path('cases_api/', views.CasesViewAPI.as_view()),
    path('cases_api/<int:pk>', views.SingleCaseViewAPI.as_view()),
    path('organisations/api/', views.OrganisationsViewAPI.as_view()),
    path('organisations/api/<int:pk>', views.SingleOrganisationViewAPI.as_view()),
    path('pow_api/', views.PlaceOfWorkViewAPI.as_view()),
    path('pow_api/<int:pk>', views.SinglePlaceOfWorkViewAPI.as_view()),
    path('articles/api/', views.ArticleViewAPI.as_view()),
    path('articles/api/<int:pk>', views.SingleArticleViewAPI.as_view()),
    path('persecution_api/', views.PersecutionViewAPI.as_view()),
    path('persecution_api/<int:pk>', views.SinglePersecutionViewAPI.as_view()),
    path('aip_api/', views.AiPViewAPI.as_view()),
    path('aip_api/<int:pk>', views.SingleAiPViewAPI.as_view()),
    path('rights_api/', views.RightsViewAPI.as_view()),
    path('rights_api/<int:pk>', views.SingleRightsViewAPI.as_view()),
    path('status_api/', views.StatusViewAPI.as_view()),
    path('status_api/<int:pk>', views.SingleStatusViewAPI.as_view()),
    path('acts_api/', views.ActViewAPI.as_view()),
    path('acts_api/<int:pk>', views.SingleActViewAPI.as_view()),
    path('via_api/', views.ViAAPI.as_view()),
    path('via_api/<int:pk>', views.SingleViAAPI.as_view()),
    path('pia_api/', views.PersonInActAPI.as_view()),
    path('pia_api/<int:pk>', views.SinglePersonInActAPI.as_view()),
    path('depriving_api/', views.DeprivingAPI.as_view()),
    path('depriving_api/<int:pk>', views.SingleDeprivingAPI.as_view()),

    # path('persons_api/', views.PersonsViewAPI.as_view()),
    # path('persons_api/<int:pk>', views.SinglePersonsViewAPI.as_view()),
]