from django.conf import settings
from django.db import models
from django.utils import timezone


class ProductCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=120)
    contact_person = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name


class InventoryItem(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('pack', 'Pack'),
        ('crate', 'Crate'),
        ('piece', 'Piece'),
        ('box', 'Box'),
    ]

    name = models.CharField(max_length=150)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, related_name='items')
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def low_stock(self):
        return self.stock_quantity <= self.reorder_level


class StockMovement(models.Model):
    MOVEMENT_CHOICES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJUSTMENT', 'Adjustment'),
    ]

    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_CHOICES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=120, blank=True)
    reason = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.item.name} - {self.movement_type}'


class Employee(models.Model):
    ROLE_CHOICES = [
        ('Owner', 'Owner'),
        ('Admin', 'Admin'),
        ('Inventory', 'Inventory'),
        ('Sales', 'Sales'),
        ('HR', 'HR'),
    ]
    DEPARTMENT_CHOICES = [
        ('Farm Operations', 'Farm Operations'),
        ('Production', 'Production'),
        ('Inventory', 'Inventory'),
        ('Sales', 'Sales'),
        ('HR', 'HR'),
        ('Admin', 'Admin'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('On Leave', 'On Leave'),
        ('Terminated', 'Terminated'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee', null=True, blank=True)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='Farm Operations')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='Sales')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    monthly_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    hire_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    class Meta:
        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name


class AttendanceRecord(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Present')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f'{self.employee.full_name} - {self.date}'


class PayrollEntry(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_entries')
    period_start = models.DateField()
    period_end = models.DateField()
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.employee.full_name} - {self.period_start}'


class SaleTransaction(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('GCash', 'GCash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Credit Card', 'Credit Card'),
    ]

    receipt_number = models.CharField(max_length=50, unique=True)
    cashier = models.CharField(max_length=100, default='Owner')
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES, default='Cash')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.receipt_number


class SaleItem(models.Model):
    transaction = models.ForeignKey(SaleTransaction, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, related_name='sales')
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.item.name} x {self.quantity}'
