from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Count
from decimal import Decimal
import json

from .models import MenuItem, Category, Order, OrderItem, Table, Payment
from .forms import MenuItemForm, CategoryForm, OrderForm


@login_required
def dashboard(request):
    """Dashboard with overview of today's activity"""
    today = timezone.now().date()
    
    # Today's statistics
    todays_orders = Order.objects.filter(created_at__date=today)
    total_orders = todays_orders.count()
    total_sales = todays_orders.aggregate(Sum('total'))['total__sum'] or 0
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Top selling items today
    top_items = OrderItem.objects.filter(
        order__created_at__date=today
    ).values(
        'menu_item__name'
    ).annotate(
        total_quantity=Sum('quantity')
    ).order_by('-total_quantity')[:5]
    
    # Table status
    tables = Table.objects.all().order_by('number')
    
    context = {
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'top_items': top_items,
        'tables': tables,
    }
    
    return render(request, 'pos/dashboard.html', context)


@staff_member_required
def menu_management(request):
    """Menu management page"""
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.select_related('category').all()
    
    context = {
        'categories': categories,
        'menu_items': menu_items,
    }
    
    return render(request, 'pos/menu_management.html', context)


@staff_member_required
def add_menu_item(request):
    """Add new menu item"""
    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item added successfully!')
            return redirect('pos:menu_management')
    else:
        form = MenuItemForm()
    
    return render(request, 'pos/menu_form.html', {'form': form, 'title': 'Add Menu Item'})


@staff_member_required
def edit_menu_item(request, item_id):
    """Edit existing menu item"""
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Menu item updated successfully!')
            return redirect('pos:menu_management')
    else:
        form = MenuItemForm(instance=item)
    
    return render(request, 'pos/menu_form.html', {
        'form': form, 
        'title': f'Edit {item.name}',
        'item': item
    })


@staff_member_required
def delete_menu_item(request, item_id):
    """Delete menu item"""
    item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, f'{item.name} deleted successfully!')
        return redirect('pos:menu_management')
    
    return render(request, 'pos/confirm_delete.html', {
        'object': item,
        'type': 'menu item'
    })


@staff_member_required
def toggle_menu_item(request, item_id):
    """Toggle menu item availability"""
    item = get_object_or_404(MenuItem, id=item_id)
    item.is_available = not item.is_available
    item.save()
    
    status = "available" if item.is_available else "unavailable"
    messages.success(request, f'{item.name} marked as {status}!')
    
    return redirect('pos:menu_management')


@staff_member_required
def manage_categories(request):
    """Manage categories"""
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('pos:manage_categories')
    else:
        form = CategoryForm()
    
    context = {
        'categories': categories,
        'form': form,
    }
    
    return render(request, 'pos/categories.html', context)


@staff_member_required
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('pos:manage_categories')
    else:
        form = CategoryForm()
    
    return render(request, 'pos/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def order_list(request):
    """List all orders"""
    orders = Order.objects.select_related('table', 'created_by').order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'pos/order_list.html', context)


@login_required
def new_order(request):
    """Create new order"""
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            
            # Update table status if table is selected
            if order.table:
                order.table.status = 'occupied'
                order.table.save()
            
            messages.success(request, f'Order {order.order_number} created successfully!')
            return redirect('pos:order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    # Get available tables
    available_tables = Table.objects.filter(status='available')
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    context = {
        'form': form,
        'available_tables': available_tables,
        'categories': categories,
        'menu_items': menu_items,
    }
    
    return render(request, 'pos/new_order.html', context)


@login_required
def order_detail(request, order_id):
    """Order detail and editing"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.select_related('menu_item').all()
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.filter(is_available=True).select_related('category')
    
    context = {
        'order': order,
        'order_items': order_items,
        'categories': categories,
        'menu_items': menu_items,
    }
    
    return render(request, 'pos/order_detail.html', context)


@login_required
def edit_order(request, order_id):
    """Edit order details"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order updated successfully!')
            return redirect('pos:order_detail', order_id=order.id)
    else:
        form = OrderForm(instance=order)
    
    return render(request, 'pos/order_form.html', {
        'form': form,
        'order': order,
        'title': f'Edit Order {order.order_number}'
    })


@login_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.ORDER_STATUSES):
            order.status = new_status
            order.save()
            
            # Free table if order is completed or cancelled
            if new_status in ['paid', 'cancelled'] and order.table:
                order.table.status = 'available'
                order.table.save()
            
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False})


@login_required
def table_management(request):
    """Table management interface"""
    tables = Table.objects.all().order_by('number')
    
    context = {
        'tables': tables,
    }
    
    return render(request, 'pos/table_management.html', context)


@login_required
def update_table_status(request, table_id):
    """Update table status"""
    if request.method == 'POST':
        table = get_object_or_404(Table, id=table_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Table.TABLE_STATUSES):
            table.status = new_status
            table.save()
            
            return JsonResponse({'success': True, 'status': new_status})
    
    return JsonResponse({'success': False})


@login_required
def billing(request, order_id):
    """Billing interface for an order"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.select_related('menu_item').all()
    
    # Calculate totals
    order.calculate_totals()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'pos/billing.html', context)


@login_required
def process_payment(request, order_id):
    """Process payment for an order"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        amount = Decimal(request.POST.get('amount', '0'))
        reference_number = request.POST.get('reference_number', '')
        
        if amount >= order.total:
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                method=payment_method,
                reference_number=reference_number,
                processed_by=request.user
            )
            
            # Update order status
            order.status = 'paid'
            order.save()
            
            # Free table
            if order.table:
                order.table.status = 'available'
                order.table.save()
            
            messages.success(request, f'Payment processed successfully for order {order.order_number}!')
            return redirect('pos:print_receipt', order_id=order.id)
        else:
            messages.error(request, 'Payment amount is insufficient!')
    
    return redirect('pos:billing', order_id=order_id)


@login_required
def print_receipt(request, order_id):
    """Generate receipt for printing"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.select_related('menu_item').all()
    payment = getattr(order, 'payment', None)
    
    context = {
        'order': order,
        'order_items': order_items,
        'payment': payment,
    }
    
    return render(request, 'pos/receipt.html', context)


# AJAX API endpoints
@login_required
def get_menu_items(request):
    """Get menu items by category (AJAX)"""
    category_id = request.GET.get('category_id')
    
    if category_id:
        menu_items = MenuItem.objects.filter(
            category_id=category_id,
            is_available=True
        ).values('id', 'name', 'price', 'description')
    else:
        menu_items = MenuItem.objects.filter(
            is_available=True
        ).values('id', 'name', 'price', 'description', 'category__name')
    
    return JsonResponse({'menu_items': list(menu_items)})


@csrf_exempt
@login_required
def add_item_to_order(request):
    """Add item to order (AJAX)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            menu_item_id = data.get('menu_item_id')
            quantity = int(data.get('quantity', 1))
            special_instructions = data.get('special_instructions', '')
            
            order = get_object_or_404(Order, id=order_id)
            menu_item = get_object_or_404(MenuItem, id=menu_item_id)
            
            # Check if item already exists in order
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                menu_item=menu_item,
                defaults={
                    'quantity': quantity,
                    'unit_price': menu_item.price,
                    'special_instructions': special_instructions
                }
            )
            
            if not created:
                # Update existing item
                order_item.quantity += quantity
                if special_instructions:
                    order_item.special_instructions = special_instructions
                order_item.save()
            
            # Recalculate order totals
            order.calculate_totals()
            
            return JsonResponse({
                'success': True,
                'item_total': float(order_item.get_total()),
                'order_subtotal': float(order.subtotal),
                'order_tax': float(order.tax_amount),
                'order_total': float(order.total)
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False})


@login_required
def get_order_totals(request, order_id):
    """Get order totals (AJAX)"""
    order = get_object_or_404(Order, id=order_id)
    order.calculate_totals()
    
    return JsonResponse({
        'subtotal': float(order.subtotal),
        'tax': float(order.tax_amount),
        'total': float(order.total)
    })