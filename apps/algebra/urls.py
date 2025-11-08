from django.urls import path
from . import views

urlpatterns = [
    path("matmul/", views.matmul, name="algebra-matmul"),
    path("det/", views.det, name="algebra-det"),
]
