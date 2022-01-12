from django.contrib import admin
from .models import *


class PersonAdmin (admin.ModelAdmin):
    search_fields = ['name']


class OrganisationAdmin (admin.ModelAdmin):
    search_fields = ['short_name']


class PersecutionAdmin (admin.ModelAdmin):
    list_filter = ['case']


admin.site.register(Person, PersonAdmin)
admin.site.register(Organisation, OrganisationAdmin)
admin.site.register(Persecution, PersecutionAdmin)
admin.site.register(Structure)