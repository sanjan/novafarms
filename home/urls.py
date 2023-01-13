from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new-order/', views.new_order, name='new_order'),
    path('order-details/<int:order_id>/', views.order_view, name='order_view'),
]
 