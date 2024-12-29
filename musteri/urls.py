from django.urls import path
from . import views

app_name = 'musteri'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Customer Management
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/create/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/', views.customer_detail_view, name='customer_detail'),
    path('customers/<int:pk>/edit/', views.customer_edit_view, name='customer_edit'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),
    path('customers/upload/', views.upload_pdf_view, name='upload_pdf'),
    path('customers/query/', views.customer_query_view, name='customer_query'),
    path('customers/<int:customer_id>/last-check-update/', views.last_check_update, name='last_check_update'),
    
    # Payment Management
    path('customers/<int:customer_id>/payments/add/', views.add_payment, name='add_payment'),
    
    # Task Management
    path('tasks/', views.yapilacak_list, name='yapilacak'),
    path('tasks/add/', views.add_yapilacak, name='add_yapilacak'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:id>/complete/', views.complete_yapilacak, name='complete_yapilacak'),
    
    # Calendar & Events
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.calendar_events_view, name='calendar_events'),
    path('calendar/events/create/', views.calendar_event_create_view, name='calendar_event_create'),
    
    # Reports & Analytics
    path('reports/', views.reports_view, name='reports'),
    path('reports/customers/', views.customer_reports_view, name='customer_reports'),
    path('reports/tasks/', views.task_reports_view, name='task_reports'),
    path('reports/expenses/', views.expense_reports_view, name='expense_reports'),
    
    # Expense Management
    path('expenses/', views.calculate_expenses, name='expense'),
    path('expenses/create/', views.expense_create_view, name='expense_create'),
    path('expenses/<int:pk>/edit/', views.expense_edit_view, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete_view, name='expense_delete'),
    
    # Customer Status & Documents
    path('customers/status/', views.customer_status_list, name='customer_status_list'),
    path('customers/expiring/', views.customer_expiry_list, name='customer_expiry_list'),
    path('customers/documents/', views.customer_documents_view, name='customer_documents'),
    
    # User Profile & Settings
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/notifications/', views.notification_settings_view, name='notification_settings'),
    
    # API Endpoints
    path('api/customers/search/', views.customer_search_api, name='customer_search_api'),
    path('api/tasks/search/', views.task_search_api, name='task_search_api'),

    # Notes
    path('customers/<int:pk>/add_note/', views.add_note_to_customer, name='add_note'),
    path('customers/<int:pk>/delete_note/<int:note_id>/', views.delete_note, name='delete_note'),
]
