from django.shortcuts import redirect, render


ROLE_ACCESS = {
    'owner': {'dashboard', 'inventory', 'pos', 'hr', 'reports', 'applications', 'tasks'},
    'finance': {'dashboard', 'inventory', 'pos', 'hr', 'reports'},
    'inventory': {'inventory'},
    'sales': {'pos'},
    'hr': {'hr'},
    'staff': {'tasks'},
}

ROLE_DISPLAY_NAMES = {
    'owner': 'Randy Dagooc',
    'finance': 'Finance Staff',
    'inventory': 'Lito Salazar',
    'sales': 'Rica Jumao-as',
    'hr': 'Nico Reyes',
    'staff': 'Regular Staff',
}


def get_role_display_name(role):
    return ROLE_DISPLAY_NAMES.get(role, role.replace('_', ' ').title())


def role_required(page_name):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            role = request.session.get('role')
            if not role:
                return redirect('login')
            if page_name not in ROLE_ACCESS.get(role, set()):
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def redirect_to_login(request):
    if request.session.get('role'):
        return redirect('dashboard')
    return redirect('login')


def login_view(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'owner').lower()
        if role not in ROLE_ACCESS:
            role = 'owner'
        request.session['role'] = role
        return redirect('dashboard')
    return render(request, 'farm_management/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def dashboard(request):
    role = request.session.get('role', 'owner')
    if role not in ROLE_ACCESS:
        request.session.flush()
        return redirect('login')

    if role not in {'owner', 'finance'}:
        if role == 'inventory':
            return redirect('inventory')
        if role == 'sales':
            return redirect('pos')
        if role == 'hr':
            return redirect('hr')
        if role == 'staff':
            return redirect('tasks')
        return redirect('login')

    dashboard_data = {
        'owner': {
            'title': 'Owner Dashboard',
            'summary': 'Full operational view across all farm departments.',
            'cards': [
                {'label': 'Total Sales', 'value': '₱ 1,248,500', 'note': 'Current cycle'},
                {'label': 'Inventory Value', 'value': '₱ 486,000', 'note': 'Estimated stock'},
                {'label': 'Active Personnel', 'value': '48', 'note': 'Working staff'},
                {'label': 'Net Margin', 'value': '₱ 392,400', 'note': 'Projected gain'},
            ],
            'quick_actions': ['Add employee', 'Create sales transaction', 'Restock inventory', 'Review payroll'],
        },
        'finance': {
            'title': 'Finance Dashboard',
            'summary': 'Track all financial movement, payroll obligations, and operational summaries.',
            'cards': [
                {'label': 'Gross Revenue', 'value': '₱ 1,248,500', 'note': 'Current cycle'},
                {'label': 'Expenses', 'value': '₱ 856,100', 'note': 'Operational costs'},
                {'label': 'Net Cashflow', 'value': '₱ 392,400', 'note': 'Remaining gain'},
                {'label': 'Payroll Due', 'value': '₱ 268,900', 'note': 'This month'},
            ],
            'quick_actions': ['Generate report', 'Review due payroll', 'Check cashflow', 'Export summary'],
        },
    }
    context = {
        'role': get_role_display_name(role),
        'stats': dashboard_data.get(role, dashboard_data['owner']),
    }
    return render(request, 'farm_management/dashboard.html', context)


@role_required('inventory')
def inventory_view(request):
    items = [
        {'name': 'Baguio Beans', 'category': 'Vegetables', 'stock': '120 kg', 'status': 'Healthy'},
        {'name': 'Carabao Mango', 'category': 'Fruits', 'stock': '45 kg', 'status': 'Low stock'},
        {'name': 'Fresh Basil', 'category': 'Herbs', 'stock': '18 packs', 'status': 'Restocking'},
        {'name': 'Eggplant', 'category': 'Vegetables', 'stock': '86 kg', 'status': 'Healthy'},
    ]
    transaction_log = [
        {'item': 'Fresh Basil', 'type': 'Deduction', 'quantity': '7 packs', 'reason': 'Sales order'},
        {'item': 'Baguio Beans', 'type': 'Addition', 'quantity': '30 kg', 'reason': 'Supplier delivery'},
    ]
    return render(request, 'farm_management/inventory.html', {'items': items, 'transaction_log': transaction_log})


@role_required('pos')
def pos_view(request):
    transactions = [
        {'receipt': 'DF-101', 'method': 'Cash', 'amount': '₱ 1,250', 'buyer': 'Household Customer'},
        {'receipt': 'DF-102', 'method': 'GCash', 'amount': '₱ 2,340', 'buyer': 'Restaurant Buyer'},
        {'receipt': 'DF-103', 'method': 'Card', 'amount': '₱ 980', 'buyer': 'Walk-in Customer'},
    ]
    cart_preview = [
        {'item': 'Baguio Beans', 'qty': 2, 'amount': '₱ 150'},
        {'item': 'Carabao Mango', 'qty': 3, 'amount': '₱ 330'},
        {'item': 'Fresh Basil', 'qty': 1, 'amount': '₱ 35'},
    ]
    return render(request, 'farm_management/pos.html', {'transactions': transactions, 'cart_preview': cart_preview})


def _build_hr_context():
    employees = [
        {'name': 'Randy Dagooc', 'employee_type': 'Management', 'role': 'Owner / CEO', 'status': 'Active'},
        {'name': 'Lito Salazar', 'employee_type': 'Regular', 'role': 'Inventory Officer', 'status': 'Active'},
        {'name': 'Rica Jumao-as', 'employee_type': 'Regular', 'role': 'Sales Associate', 'status': 'Active'},
        {'name': 'Nico Reyes', 'employee_type': 'Contractual', 'role': 'HR Officer', 'status': 'On Leave'},
        {'name': 'Finance Staff', 'employee_type': 'Regular', 'role': 'Finance Staff', 'status': 'Active'},
    ]
    attendance = [
        {'name': 'Lito Salazar', 'date': 'Oct 02, 2026', 'status': 'Present'},
        {'name': 'Rica Jumao-as', 'date': 'Oct 02, 2026', 'status': 'Present'},
        {'name': 'Nico Reyes', 'date': 'Oct 02, 2026', 'status': 'Absent'},
        {'name': 'Finance Staff', 'date': 'Oct 02, 2026', 'status': 'Present'},
    ]
    payroll = [
        {'name': 'Randy Dagooc', 'type': 'Management', 'salary': '₱ 40,000', 'status': 'Approved'},
        {'name': 'Lito Salazar', 'type': 'Regular', 'salary': '₱ 22,000', 'status': 'Pending'},
        {'name': 'Rica Jumao-as', 'type': 'Regular', 'salary': '₱ 18,000', 'status': 'Approved'},
        {'name': 'Finance Staff', 'type': 'Regular', 'salary': '₱ 20,000', 'status': 'Tentative'},
    ]
    tentative_payroll = [
        {'name': 'Randy Dagooc', 'days_present': 20, 'rate': '₱ 2,000/day', 'tentative_pay': '₱ 40,000'},
        {'name': 'Lito Salazar', 'days_present': 18, 'rate': '₱ 1,200/day', 'tentative_pay': '₱ 21,600'},
        {'name': 'Rica Jumao-as', 'days_present': 19, 'rate': '₱ 950/day', 'tentative_pay': '₱ 18,050'},
        {'name': 'Finance Staff', 'days_present': 20, 'rate': '₱ 1,000/day', 'tentative_pay': '₱ 20,000'},
    ]
    applicants = [
        {'name': 'Alyssa Panganiban', 'role': 'Farm Worker', 'type': 'Contractual', 'status': 'Pending', 'experience': '2 years poultry care'},
        {'name': 'Jhon Dela Cruz', 'role': 'Inventory Assistant', 'type': 'Permanent', 'status': 'Awaiting interview', 'experience': 'Warehouse and stock handling'},
        {'name': 'Mariel Santos', 'role': 'Sales Associate', 'type': 'Contractual', 'status': 'For review', 'experience': 'Retail and customer service'},
    ]
    return {
        'employees': employees,
        'attendance': attendance,
        'payroll': payroll,
        'tentative_payroll': tentative_payroll,
        'applicants': applicants,
    }


@role_required('hr')
def hr_view(request):
    context = _build_hr_context()
    context['section'] = 'overview'
    return render(request, 'farm_management/hr.html', context)


@role_required('hr')
def hr_attendance_view(request):
    context = _build_hr_context()
    context['section'] = 'attendance'
    return render(request, 'farm_management/hr.html', context)


@role_required('hr')
def hr_payroll_view(request):
    context = _build_hr_context()
    context['section'] = 'payroll'
    return render(request, 'farm_management/hr.html', context)


@role_required('hr')
def hr_applicants_view(request):
    context = _build_hr_context()
    context['section'] = 'applicants'
    return render(request, 'farm_management/hr.html', context)


@role_required('hr')
def hr_employees_view(request):
    context = _build_hr_context()
    context['section'] = 'employees'
    return render(request, 'farm_management/hr.html', context)


@role_required('reports')
def reports_view(request):
    report_cards = [
        {'module': 'Sales', 'headline': '₱ 1.25M', 'detail': 'Sales this cycle'},
        {'module': 'Inventory', 'headline': '98.4%', 'detail': 'Stock accuracy'},
        {'module': 'HR', 'headline': '92%', 'detail': 'Attendance rate'},
        {'module': 'Operations', 'headline': '89%', 'detail': 'Production output'},
    ]
    summary_sections = [
        {'title': 'Sales Summary', 'items': ['Total sales: ₱ 1,248,500', 'Orders delivered: 1,182', 'Top product: Baguio Beans']},
        {'title': 'Inventory Summary', 'items': ['Current stock value: ₱ 486,000', 'Low stock alerts: 4 items', 'Reorders pending: 2 shipments']},
        {'title': 'HR Summary', 'items': ['Active employees: 48', 'Payroll due: ₱ 268,900', 'Attendance: 92% this month']},
        {'title': 'Operations Summary', 'items': ['Field productivity: 89%', 'Daily tasks completed: 46', 'Pending issues: 7 items']},
    ]
    return render(request, 'farm_management/reports.html', {'report_cards': report_cards, 'summary_sections': summary_sections})


# Backward compatibility alias kept for older bookmarked routes.
def analytics_view(request):
    return reports_view(request)


@role_required('applications')
def applications_view(request):
    applicants = [
        {'name': 'Alyssa Panganiban', 'role': 'Farm Worker', 'type': 'Contractual', 'status': 'Pending', 'experience': '2 years poultry care'},
        {'name': 'Jhon Dela Cruz', 'role': 'Inventory Assistant', 'type': 'Permanent', 'status': 'Awaiting interview', 'experience': 'Warehouse and stock handling'},
        {'name': 'Mariel Santos', 'role': 'Sales Associate', 'type': 'Contractual', 'status': 'For review', 'experience': 'Retail and customer service'},
    ]
    return render(request, 'farm_management/applications.html', {'applicants': applicants})


@role_required('tasks')
def tasks_view(request):
    tasks = [
        {'title': 'Harvest and sort vegetables', 'due': 'Today, 8:00 AM', 'status': 'In progress'},
        {'title': 'Prepare inventory count sheet', 'due': 'Today, 10:30 AM', 'status': 'Pending'},
        {'title': 'Record daily sales summary', 'due': 'Today, 2:00 PM', 'status': 'Scheduled'},
        {'title': 'Check poultry feeding logs', 'due': 'Tomorrow, 7:30 AM', 'status': 'Planned'},
    ]
    return render(request, 'farm_management/tasks.html', {'tasks': tasks})
