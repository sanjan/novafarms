from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new-order/', views.new_order, name='new_order'),
    path('new-batch/', views.new_batch, name='new_batch'),
    path('order-details/<int:order_id>/', views.order_details, name='order_details'),
    path('batch-details/<str:batch_number>/', views.batch_details, name='batch_details'),
]
 