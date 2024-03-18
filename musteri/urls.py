from django.urls import path
from . import views

app_name = 'musteri'


urlpatterns = [
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/new/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail_view, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit_view, name='customer_edit'),
    path('customers/upload_pdf/', views.upload_pdf_view, name='upload_pdf'),  # yeni eklenen url
    path('customers/query/', views.customer_query_view, name='customer_query'),  # yeni yol
    path('customers/<int:pk>/ptt-track/', views.PTTTrackingView.as_view(), name='ptt-track'),
    path('customers/home/', views.home, name='home'),
    path('captcha/', views.FormView().captcha, name='captcha'),
    path('customers/ikamet/', views.FormView().form_view, name='ikamet'),
    path('customer_expiry_list/', views.customer_expiry_list, name='customer_expiry_list'),
    # path('download-excel/', views.download_excel, name='download_excel'),
    path('expense/', views.calculate_expenses, name='expense'),
    path('yapilacak/', views.yapilacak_list_view, name='yapilacak'),
    path('add_yapilacak/', views.add_yapilacak, name='add_yapilacak'),
    path('complete_yapilacak/<int:id>/', views.complete_yapilacak, name='complete_yapilacak'),
    





    ]
