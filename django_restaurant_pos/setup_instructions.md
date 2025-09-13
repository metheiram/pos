# Django Restaurant POS System Setup Instructions

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

## Installation Steps

1. **Create Project Directory and Virtual Environment**
   ```bash
   mkdir restaurant_pos_project
   cd restaurant_pos_project
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Copy Project Files**
   - Copy all the Django project files to your `restaurant_pos_project` directory
   - The structure should look like:
     ```
     restaurant_pos_project/
     ├── venv/
     └── django_restaurant_pos/
         ├── manage.py
         ├── requirements.txt
         ├── restaurant_pos/
         └── pos/
     ```

3. **Navigate to Django Project and Install Dependencies**
   ```bash
   cd django_restaurant_pos
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   # Create and apply migrations
   python manage.py makemigrations pos
   python manage.py migrate
   ```

5. **Create Superuser Account**
   ```bash
   python manage.py createsuperuser
   # Follow prompts to create admin account
   ```

6. **Create Sample Data (Optional)**
   ```bash
   python manage.py shell
   ```
   
   Then run these Python commands:
   ```python
   from pos.models import Category, MenuItem, Table
   from django.contrib.auth.models import User
   
   # Create categories
   appetizers = Category.objects.create(name="Appetizers", description="Starter dishes")
   mains = Category.objects.create(name="Main Course", description="Main dishes")
   desserts = Category.objects.create(name="Desserts", description="Sweet endings")
   beverages = Category.objects.create(name="Beverages", description="Drinks")
   
   # Create sample menu items
   MenuItem.objects.create(name="Caesar Salad", description="Fresh romaine lettuce with caesar dressing", price=12.99, category=appetizers)
   MenuItem.objects.create(name="Buffalo Wings", description="Spicy chicken wings with ranch dip", price=14.99, category=appetizers)
   MenuItem.objects.create(name="Grilled Salmon", description="Fresh Atlantic salmon with lemon butter", price=24.99, category=mains)
   MenuItem.objects.create(name="Ribeye Steak", description="12oz prime ribeye with garlic mashed potatoes", price=32.99, category=mains)
   MenuItem.objects.create(name="Chocolate Cake", description="Rich chocolate layer cake", price=8.99, category=desserts)
   MenuItem.objects.create(name="Soft Drinks", description="Coca-Cola products", price=3.99, category=beverages)
   
   # Create tables
   for i in range(1, 11):
       Table.objects.create(number=i, seats=4)
   
   # Create staff user
   User.objects.create_user(username='staff', email='staff@restaurant.com', password='staff123', is_staff=False)
   
   exit()
   ```

7. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the Application**
   - Open your web browser and go to: `http://127.0.0.1:8000/`
   - Login with:
     - Admin account you created earlier (full access)
     - Staff account: username `staff`, password `staff123` (limited access)

## Features Overview

### User Roles
- **Admin/Staff**: Full access to all features including menu management
- **Regular Users**: Access to order taking, billing, and dashboard

### Main Features
1. **Dashboard**: Overview of daily sales, orders, and table status
2. **Order Management**: Create new orders, add items, track status
3. **Menu Management**: Add/edit/delete menu items and categories (admin only)
4. **Table Management**: Monitor and update table status
5. **Billing & Payment**: Process payments and generate receipts
6. **Real-time Updates**: Live status updates for orders and tables

### Default Login Credentials
- **Admin**: Use the superuser account you created
- **Staff**: username: `staff`, password: `staff123`

## Customization

### Restaurant Settings
Edit `restaurant_pos/settings.py` and modify the `POS_SETTINGS` dictionary:
```python
POS_SETTINGS = {
    'TAX_RATE': 0.08,  # Change tax rate (8% = 0.08)
    'CURRENCY': '$',   # Change currency symbol
    'RESTAURANT_NAME': 'Your Restaurant Name',  # Restaurant name
}
```

### Adding More Tables
Use Django admin or shell:
```bash
python manage.py shell
```
```python
from pos.models import Table
# Add tables 11-20
for i in range(11, 21):
    Table.objects.create(number=i, seats=4)
```

## Production Deployment

For production deployment:

1. **Security Settings**
   - Change `SECRET_KEY` in settings.py
   - Set `DEBUG = False`
   - Update `ALLOWED_HOSTS`

2. **Database**
   - Consider using PostgreSQL for production
   - Set up proper database backups

3. **Static Files**
   - Configure static file serving
   - Run `python manage.py collectstatic`

4. **Server**
   - Use a production WSGI server like Gunicorn
   - Set up reverse proxy with Nginx

## Troubleshooting

### Common Issues

1. **Module Not Found Error**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirements.txt`

2. **Database Errors**
   - Delete `db.sqlite3` and run migrations again
   - Check migration status: `python manage.py showmigrations`

3. **Static Files Not Loading**
   - Run: `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATICFILES_DIRS` in settings

4. **Permission Errors**
   - Ensure proper file permissions
   - Check if virtual environment is activated

## Support

The system includes:
- Responsive design for desktop and mobile
- Real-time updates
- Print-ready receipts
- Secure authentication
- Data validation
- Error handling

For additional customization or issues, refer to the Django documentation or modify the code according to your specific needs.