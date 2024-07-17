from django.urls import path
from . import views

app_name = 'coupons'  # Specify the app_name

urlpatterns = [
    path('apply/', views.coupon_apply, name='coupon_apply'),
    path('delete', views.coupon_remove, name='coupon_delete'),

]
