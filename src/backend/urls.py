"""
URL configuration for cfehome project.

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
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from .views import home_view, about_view
from auth import views as auth_views
from checkouts import views as checkout_views
from landing import views as landing_views
from subscriptions import views as subscription_views
from .views import (
    home_view, 
    about_view, 
    pw_protected_view,
    user_only_view,
    staff_only_view
)

urlpatterns = [
    # path("", landing_views.landing_page_view, name='home'), #index page -> root page
    path("", lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('account_login'), name='home'), # redirect to login or dashboard
    # checkout
    path("checkout/sub-price/<int:price_id>/", checkout_views.product_price_redirect_view, name='sub-price-checkout'),
    path("checkout/start/", checkout_views.checkout_redirect_view, name='stripe-checkout-start'),
    path("checkout/success/", checkout_views.checkout_finalize_view, name='stripe-checkout-end'),
    #pricing
    path("pricing/", subscription_views.subscription_price_view, name='pricing'),
    path("pricing/<str:interval>/", subscription_views.subscription_price_view, name='pricing_interval'),

    path("about/", about_view),
    path("hello-world/", home_view),
    path("hello-world.html", home_view),
    path("admin/", admin.site.urls),
    path('accounts/billing/', subscription_views.user_subscription_view, name='user_subscription'),
    path('accounts/billing/cancel/', subscription_views.user_subscription_cancel_view, name='user_subscription_cancel'),
    path('accounts/', include('allauth.urls')),
    path('protected/user-only/', user_only_view),
    path('protected/staff-only/', staff_only_view),
    path('profiles/', include('profiles.urls')),
    path('core/', include('core.urls')),
    path('protected/', pw_protected_view),
    
    # Next.js Headless API 
    path('api/v1/', include('core.api_urls')),
]