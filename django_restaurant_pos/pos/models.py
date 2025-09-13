from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Category(models.Model):
    """Menu item categories like Appetizers, Main Course, Desserts"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """Restaurant menu items"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - ${self.price}"


class Table(models.Model):
    """Restaurant tables"""
    TABLE_STATUSES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
        ('cleaning', 'Cleaning'),
    ]
    
    number = models.PositiveIntegerField(unique=True)
    seats = models.PositiveIntegerField(default=4)
    status = models.CharField(max_length=20, choices=TABLE_STATUSES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Table {self.number} ({self.seats} seats)"


class Order(models.Model):
    """Customer orders"""
    ORDER_STATUSES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready'),
        ('served', 'Served'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=20, unique=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default='pending')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            from django.utils import timezone
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}"
        super().save(*args, **kwargs)
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total for this order"""
        from django.conf import settings
        
        subtotal = sum(item.get_total() for item in self.orderitem_set.all())
        tax_rate = Decimal(str(settings.POS_SETTINGS.get('TAX_RATE', 0.08)))
        tax_amount = subtotal * tax_rate
        total = subtotal + tax_amount
        
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.total = total
        self.save()
    
    def __str__(self):
        return f"Order {self.order_number} - ${self.total}"


class OrderItem(models.Model):
    """Individual items in an order"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total(self):
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.menu_item.price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"


class Payment(models.Model):
    """Payment records for orders"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('digital', 'Digital Payment'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True)
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.order.order_number} - ${self.amount}"