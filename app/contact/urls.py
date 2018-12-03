from django.urls import path

from . import views

urlpatterns= [
    path('add_user/', views.add_user, name='add_user'),
    path('get_user_list/', views.get_user_list, name='get_user_list'),
    path('user_details/<user_id>/', views.user_details, name='user_details'),
    path('contact_list/', views.contact_list, name='contact_list'),
    path('search_contact/', views.search_contact, name='search_contact'),
]