"""
URL configuration for shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin

from django.urls import path, include
from rest_framework import routers

from shop import settings
from store.views import *

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('book/<int:pk>/', book_detail, name='book'),
    path('comments/<int:pk>/', add_comment),
    path('search/', search_book),
    path('search/results/', search_book),
    path('add/book/form/', add_book),
    path('book/new/', BookCreateViewSet.as_view()),
    path('cart/add/<int:book_id>/', cart_add),
    path('cart/detail/', cart_detail),
    path('api/home/', include(router.urls)),
    path('cart/remove/<int:pk>/', cart_remove),
    path('signin/', sign_in_view),
    path('signin/new/', user_register_view),
    path('login/', login_view),
    path('login/new/', user_login_view),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
