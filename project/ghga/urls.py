from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='ghga-index'),
    path('sample/<str:parm>', views.sample, name='ghga-get-sample'),
    path('sample', views.sample, name='ghga-sample'),
    path('<path:path>', views.index, name='ghga-pathed'),
]