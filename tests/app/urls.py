from django.urls import path

from . import views

urlpatterns = [
    path("n-plus-one/", views.n_plus_one),
    path("select-related/", views.select_related),
]
