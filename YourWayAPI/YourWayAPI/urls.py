"""
URL configuration for YourWayAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from ProfOrientationModule.views import PostGroupView, PostProgramView, PostSuplyByProgramView, PostAuthorizeVK, GetHelloView
from .yasg import urlpatterns as doc_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path(r"edu/group/", PostGroupView.as_view()),
    path(r"edu/program/", PostProgramView.as_view()),
    path(r"edu/suply-by-program/", PostSuplyByProgramView.as_view()),
    path(r"auth/vk/", PostAuthorizeVK.as_view()),
    path(r"edu/test-method/", GetHelloView.as_view()),
]

urlpatterns += doc_urls