from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room, name='room'),
    path('delete/<int:message_id>/', views.delete_message, name='delete_message'),
    path('signup/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_account/', views.delete_account_view, name='delete_account'),
    path('fetch_messages/', views.fetch_messages, name='fetch_messages'),
]
