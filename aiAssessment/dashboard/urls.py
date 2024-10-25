from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('report/<str:userId>', views.report_view, name='report'),

]
