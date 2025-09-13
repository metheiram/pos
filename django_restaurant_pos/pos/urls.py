from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomLoginForm

app_name = 'pos'

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='pos/login.html',
        authentication_form=CustomLoginForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Menu Management
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),
    path('menu/edit/<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('menu/toggle/<int:item_id>/', views.toggle_menu_item, name='toggle_menu_item'),
    
    # Category Management
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/add/', views.add_category, name='add_category'),
    
    # Order Taking
    path('orders/', views.order_list, name='order_list'),
    path('orders/new/', views.new_order, name='new_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/edit/', views.edit_order, name='edit_order'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    
    # Table Management
    path('tables/', views.table_management, name='table_management'),
    path('tables/<int:table_id>/status/', views.update_table_status, name='update_table_status'),
    
    # Billing and Payment
    path('billing/<int:order_id>/', views.billing, name='billing'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('receipt/<int:order_id>/', views.print_receipt, name='print_receipt'),
    
    # AJAX endpoints
    path('api/menu-items/', views.get_menu_items, name='api_menu_items'),
    path('api/add-to-order/', views.add_item_to_order, name='api_add_to_order'),
    path('api/order-totals/<int:order_id>/', views.get_order_totals, name='api_order_totals'),
]