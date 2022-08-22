from django.contrib import admin
from .models import PcrTest

# admin for the PcrTest model
class PcrTestAdmin(admin.ModelAdmin):
    list_display = ('__all__')

admin.site.register(PcrTest)