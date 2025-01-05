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
    path('customers/<int:pk>/add-note/', views.add_note_to_customer, name='add_note'),
    path('customers/<int:pk>/delete-note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('customers/upload/', views.upload_pdf_view, name='upload_pdf'),
    path('customers/query/', views.customer_query_view, name='customer_query'),
    path('customers/<int:customer_id>/last-check-update/', views.last_check_update, name='last_check_update'),
    path('customers/expiry/', views.customer_expiry_list, name='customer_expiry_list'),
    path('customers/status/', views.customer_status_list, name='customer_status_list'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.calendar_events_view, name='calendar_events'),
    path('calendar/event/create/', views.calendar_event_create_view, name='calendar_event_create'),
    path('calendar/event/<int:event_id>/', views.calendar_event_detail_view, name='calendar_event_detail'),
    path('calendar/event/<int:event_id>/update/', views.calendar_event_update_view, name='calendar_event_update'),
    path('calendar/event/<int:event_id>/delete/', views.calendar_event_delete_view, name='calendar_event_delete'),
    
    # Payment Management
    path('customers/<int:customer_id>/payments/add/', views.add_payment, name='add_payment'),
    
    # Task Management
    path('tasks/', views.yapilacak_list, name='yapilacak'),
    path('tasks/add/', views.add_yapilacak, name='add_yapilacak'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:id>/complete/', views.complete_yapilacak, name='complete_yapilacak'),
    
    # Expense Management
    path('expenses/', views.expense_list, name='expense'),
    path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense_create'),
    path('expenses/calculate/', views.calculate_expenses, name='calculate_expenses'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('expenses/<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    
    # User Profile & Settings
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Reports
    path('reports/', views.reports_view, name='reports'),
    path('reports/customers/', views.customer_reports_view, name='customer_reports'),
    path('reports/tasks/', views.task_reports_view, name='task_reports'),
    path('reports/expenses/', views.expense_reports_view, name='expense_reports'),
]
