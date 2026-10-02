from django.shortcuts import redirect, render


ROLE_ACCESS = {
    'owner': {'dashboard', 'reports', 'people', 'operations'},
    'finance': {'dashboard', 'reports', 'finance'},
    'inventory': {'dashboard', 'inventory_entry', 'inventory_info', 'inventory'},
    'sales': {'dashboard', 'sales_entry', 'sales_reports'},
    'hr': {'hr'},
    'staff': {'tasks'},
}

ROLE_DISPLAY_NAMES = {
    'owner': 'Randy Dagooc',
    'finance': 'Finance Staff',
    'inventory': 'Inventory Staff',
    'sales': 'Sales Staff',
    'hr': 'HR Staff',
    'staff': 'Regular Staff',
}

DEMO_CREDENTIALS = {role: role for role in ROLE_ACCESS}

MOCK_PRODUCTS = [
    {'id': 'eggs', 'name': 'Free-range Eggs', 'category': 'Poultry', 'unit': 'dozen', 'price': 180, 'stock': 42, 'reorder_level': 12, 'inventory_tracked': True},
    {'id': 'lettuce', 'name': 'Hydroponic Lettuce', 'category': 'Hydroponics', 'unit': 'kg', 'price': 75, 'stock': 120, 'reorder_level': 25, 'inventory_tracked': True},
    {'id': 'eggplant', 'name': 'Hydroponic Eggplant', 'category': 'Hydroponics', 'unit': 'kg', 'price': 60, 'stock': 86, 'reorder_level': 20, 'inventory_tracked': True},
    {'id': 'honey', 'name': 'Raw Honey', 'category': 'Bees', 'unit': 'jar', 'price': 250, 'stock': 24, 'reorder_level': 6, 'inventory_tracked': True},
    {'id': 'farm-soda', 'name': 'Farm Soda', 'category': 'Soda', 'unit': 'bottle', 'price': 45, 'stock': 50, 'reorder_level': 10, 'inventory_tracked': True},
    {'id': 'delivery-service', 'name': 'Local Delivery Service', 'category': 'Services', 'unit': 'service', 'price': 80, 'stock': None, 'reorder_level': None, 'inventory_tracked': False},
]


def get_role_display_name(role):
    return ROLE_DISPLAY_NAMES.get(role, role.replace('_', ' ').title())


def get_mock_inventory_items():
    return [
        {
            **product,
            'stock_display': f"{product['stock']} {product['unit']}",
            'status': 'Low stock' if product['stock'] <= product['reorder_level'] else 'Healthy',
        }
        for product in MOCK_PRODUCTS
        if product['inventory_tracked']
    ]


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
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().lower()
        password = request.POST.get('password', '')
        role = DEMO_CREDENTIALS.get(username)
        if role and password == DEMO_CREDENTIALS[role]:
            request.session['role'] = role
            return redirect('dashboard')
        error = 'Invalid username or password.'
    return render(request, 'farm_management/login.html', {'error': error})


def credential_login_view(request):
    return redirect('login')


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
            return redirect('inventory_entry')
        if role == 'sales':
            return redirect('sales_entry')
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
        'inventory_mix': [
            {'category': 'Vegetables', 'item_count': 2, 'share': 50, 'color': '#2f7d5c'},
            {'category': 'Fruits', 'item_count': 2, 'share': 50, 'color': '#e6ad3b'},
        ] if role == 'owner' else [],
        'inventory_mix_gradient': 'conic-gradient(#2f7d5c 0 50%, #e6ad3b 50% 100%)',
    }
    return render(request, 'farm_management/dashboard.html', context)


@role_required('inventory_entry')
def inventory_entry_view(request):
    return render(request, 'farm_management/inventory_entry.html', {
        'items': get_mock_inventory_items(),
        'products': MOCK_PRODUCTS,
        'actor': request.session.get('role', 'inventory'),
    })


@role_required('inventory_info')
def inventory_info_view(request):
    return render(request, 'farm_management/inventory_info.html', {
        'items': get_mock_inventory_items(),
        'products': MOCK_PRODUCTS,
        'transaction_log': [],
    })


@role_required('inventory')
def inventory_view(request):
    return inventory_info_view(request)


@role_required('pos')
def pos_view(request):
    transactions = [
        {'receipt': 'DF-101', 'method': 'Cash', 'amount': '₱ 1,250', 'buyer': 'Household Customer'},
        {'receipt': 'DF-102', 'method': 'GCash', 'amount': '₱ 2,340', 'buyer': 'Restaurant Buyer'},
        {'receipt': 'DF-103', 'method': 'Card', 'amount': '₱ 980', 'buyer': 'Walk-in Customer'},
    ]
    cart_preview = [
        {'item': 'Lettuce', 'qty': 2, 'amount': '₱ 150'},
        {'item': 'Carabao Mango', 'qty': 3, 'amount': '₱ 330'},
        {'item': 'Dragon Fruit', 'qty': 1, 'amount': '₱ 35'},
    ]
    return render(request, 'farm_management/pos.html', {'transactions': transactions, 'cart_preview': cart_preview})


def _build_hr_context():
    employees = [
        {'name': 'Randy Dagooc', 'employee_type': 'Management', 'role': 'Owner / CEO', 'status': 'Active'},
        {'name': 'Inventory Staff', 'employee_type': 'Regular', 'role': 'Inventory Officer', 'status': 'Active'},
        {'name': 'Sales Staff', 'employee_type': 'Regular', 'role': 'Sales Associate', 'status': 'Active'},
        {'name': 'HR Staff', 'employee_type': 'Contractual', 'role': 'HR Officer', 'status': 'On Leave'},
        {'name': 'Finance Staff', 'employee_type': 'Regular', 'role': 'Finance Staff', 'status': 'Active'},
    ]
    attendance = [
        {'name': 'Inventory Staff', 'date': 'Oct 02, 2026', 'status': 'Present'},
        {'name': 'Sales Staff', 'date': 'Oct 02, 2026', 'status': 'Present'},
        {'name': 'HR Staff', 'date': 'Oct 02, 2026', 'status': 'Absent'},
        {'name': 'Finance Staff', 'date': 'Oct 02, 2026', 'status': 'Present'},
    ]
    payroll = [
        {'name': 'Randy Dagooc', 'type': 'Management', 'salary': '₱ 40,000', 'status': 'Approved'},
        {'name': 'Inventory Staff', 'type': 'Regular', 'salary': '₱ 22,000', 'status': 'Pending'},
        {'name': 'Sales Staff', 'type': 'Regular', 'salary': '₱ 18,000', 'status': 'Approved'},
        {'name': 'Finance Staff', 'type': 'Regular', 'salary': '₱ 20,000', 'status': 'Tentative'},
    ]
    tentative_payroll = [
        {'name': 'Randy Dagooc', 'days_present': 20, 'rate': '₱ 2,000/day', 'tentative_pay': '₱ 40,000'},
        {'name': 'Inventory Staff', 'days_present': 18, 'rate': '₱ 1,200/day', 'tentative_pay': '₱ 21,600'},
        {'name': 'Sales Staff', 'days_present': 19, 'rate': '₱ 950/day', 'tentative_pay': '₱ 18,050'},
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


@role_required('people')
def people_view(request):
    context = _build_hr_context()
    return render(request, 'farm_management/people.html', context)


@role_required('operations')
def operations_view(request):
    active_contracts = [
        {'name': 'PhilGEPS Supply Contract', 'partner': 'GreenHarvest Co.', 'value': '₱ 240,000', 'status': 'Active', 'end_date': 'Dec 31, 2026'},
        {'name': 'Department of Agriculture Purchase', 'partner': 'DA-Regional Office', 'value': '₱ 180,500', 'status': 'Active', 'end_date': 'Nov 15, 2026'},
        {'name': 'Hotel Supply Agreement', 'partner': 'Sunrise Hotel', 'value': '₱ 96,000', 'status': 'Renewal pending', 'end_date': 'Nov 30, 2026'},
    ]
    current_operations = [
        {'title': 'Crop Production', 'team': 'Field Crew', 'status': 'On track', 'detail': 'Lettuce and eggplant harvest cycle ahead of target.'},
        {'title': 'Inventory Replenishment', 'team': 'Warehouse Team', 'status': 'Monitoring', 'detail': 'Monitor delivery windows for mango and dragon fruit stock.'},
        {'title': 'Sales Pipeline', 'team': 'Sales Desk', 'status': 'Active', 'detail': 'Hotel and retail orders are being fulfilled this week.'},
        {'title': 'Workforce Deployment', 'team': 'HR & Operations', 'status': 'Stable', 'detail': 'Staffing levels remain within required coverage for field work.'},
    ]
    return render(request, 'farm_management/operations.html', {
        'active_contracts': active_contracts,
        'current_operations': current_operations,
    })


@role_required('finance')
def finance_view(request):
    submissions = [
        {'label': 'Operating Expenses', 'value': '₱ 856,100', 'status': 'Ready for review'},
        {'label': 'Payroll Due', 'value': '₱ 268,900', 'status': 'Submitted'},
        {'label': 'Cashflow', 'value': '₱ 392,400', 'status': 'Updated today'},
        {'label': 'Pending Approvals', 'value': '4 items', 'status': 'Needs owner sign-off'},
    ]
    pending_requests = [
        {'name': 'Feed & agronomy supplies', 'amount': '₱ 42,800', 'reason': 'Monthly restock'},
        {'name': 'Equipment maintenance', 'amount': '₱ 18,500', 'reason': 'Repair and servicing'},
        {'name': 'Harvest logistics', 'amount': '₱ 26,400', 'reason': 'Transport and cold storage'},
    ]
    return render(request, 'farm_management/finance.html', {'submissions': submissions, 'pending_requests': pending_requests})


@role_required('sales_entry')
def sales_entry_view(request):
    return render(request, 'farm_management/sales_entry.html', {
        'products': MOCK_PRODUCTS,
        'actor': request.session.get('role', 'sales'),
    })


@role_required('sales_reports')
def sales_reports_view(request):
    transactions = [
        {'receipt': 'DF-101', 'method': 'Cash', 'amount': '₱ 1,250', 'buyer': 'Household Customer'},
        {'receipt': 'DF-102', 'method': 'GCash', 'amount': '₱ 2,340', 'buyer': 'Restaurant Buyer'},
        {'receipt': 'DF-103', 'method': 'Card', 'amount': '₱ 980', 'buyer': 'Walk-in Customer'},
    ]
    summary_cards = [
        {'label': 'Today Sales', 'value': '₱ 15,600', 'note': 'Across 18 transactions'},
        {'label': 'Best Seller', 'value': 'Lettuce', 'note': '42 units sold'},
        {'label': 'Pending Summary', 'value': '2', 'note': 'Reports to submit'},
    ]
    return render(request, 'farm_management/sales_reports.html', {'transactions': transactions, 'summary_cards': summary_cards})


@role_required('reports')
def reports_view(request):
    report_cards = [
        {'module': 'Sales', 'headline': '₱ 1.25M', 'detail': 'Sales this cycle'},
        {'module': 'Inventory', 'headline': '98.4%', 'detail': 'Stock accuracy'},
        {'module': 'HR', 'headline': '92%', 'detail': 'Attendance rate'},
        {'module': 'Operations', 'headline': '89%', 'detail': 'Production output'},
    ]
    summary_sections = [
        {'title': 'Sales Summary', 'items': ['Total sales: ₱ 1,248,500', 'Orders delivered: 1,182', 'Top product: Lettuce']},
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
