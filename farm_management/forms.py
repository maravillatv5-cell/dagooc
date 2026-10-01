from django import forms

from .models import Employee, InventoryItem, SaleTransaction


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = [
            'name',
            'category',
            'unit',
            'cost_price',
            'selling_price',
            'stock_quantity',
            'reorder_level',
            'supplier',
            'is_active',
        ]


class PosSaleForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(is_active=True),
        label='Item',
    )
    quantity = forms.IntegerField(min_value=1, initial=1)
    payment_method = forms.ChoiceField(
        choices=SaleTransaction.PAYMENT_METHOD_CHOICES,
        initial='Cash',
    )


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'first_name',
            'last_name',
            'department',
            'role',
            'email',
            'phone',
            'monthly_salary',
            'status',
            'hire_date',
        ]
