# chatbot/urls.py
from django.urls import path
from .views import ChatView, chat_page

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
    path("", chat_page, name="chat_page"),
]