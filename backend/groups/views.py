from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class ChatTestView(TemplateView):
    template_name = 'chat_test.html'
