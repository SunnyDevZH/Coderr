"""
URL configuration for mein_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include
from accounts.views import RegisterView, LoginView, BaseInfoView, UserViewSet, ReviewViewSet
from offers.views import OfferDetailViewSet  # Import für OfferDetailViewSet
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [

    # Admin #

    path('admin/', admin.site.urls),

    # Accounts #

    path('api/registration/', RegisterView.as_view(), name='registration'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/base-info/', BaseInfoView.as_view(), name='base-info'),
    path('api/reviews/', ReviewViewSet.as_view({'get': 'list', 'post': 'create'}), name='reviews'), 

    path('api/profile/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}), name='profile'),
    path('api/profiles/business/', UserViewSet.as_view({'get': 'list_business'}), name='profiles-business'),
    path('api/profiles/customer/', UserViewSet.as_view({'get': 'list_customer'}), name='profiles-customer'),

    # Orders / Offers #

    path('api/orders/', include('orders.urls')),
    path('api/offers/', include('offers.urls')),
    path('api/offerdetails/<int:pk>/', OfferDetailViewSet.as_view({'get': 'retrieve'}), name='offerdetails'),
]
