from django.urls import path

from . import views

app_name = 'mysite'
urlpatterns = [
    path('users/', views.index, name='index'),
    path('user/<int:userId>/', views.detail, name='detail'),
    path('user/edit/<int:userId>/', views.edit, name='edit'),
    path('user/add/', views.add, name='add'),
    path('user/save/', views.save, name='save'),
    path('departments/', views.departments, name='departments'),
    # path('remove-department/', views.removeDepartment, name='removeDepartment'),
]