from django.urls import path
from api import views

urlpatterns = [
    # Auth endpoints
    path('auth/register', views.register_view, name='register'),
    path('auth/login', views.login_view, name='login'),
    path('auth/logout', views.logout_view, name='logout'),
    path('auth/me', views.me_view, name='me'),
    
    # Clients endpoints
    path('clients', views.clients_list_create, name='clients_list_create'),
    path('clients/<str:client_id>', views.client_detail, name='client_detail'),
    
    # Settings endpoints
    path('settings', views.settings_view, name='settings'),
    
    # Logs endpoints
    path('logs', views.logs_list_clear, name='logs_list_clear'),
    
    # Emails endpoints
    path('emails', views.emails_list_create, name='emails_list_create'),
    
    # Invoices endpoints
    path('invoices', views.invoices_list_create, name='invoices_list_create'),
    path('invoices/<str:invoice_id>', views.invoice_detail, name='invoice_detail'),
    path('invoices/<str:invoice_id>/payments', views.invoice_payments, name='invoice_payments'),
    path('invoices/<str:invoice_id>/payments/<str:payment_id>', views.invoice_payment_detail, name='invoice_payment_detail'),
    
    # Quotations endpoints
    path('quotes', views.quotes_list_create, name='quotes_list_create'),
    path('quotes/<str:quote_id>', views.quote_detail, name='quote_detail'),
]
