from django.test import TestCase
from django.urls import reverse


class RoleBasedAccessTests(TestCase):
    def set_role(self, role):
        session = self.client.session
        session['role'] = role
        session.save()

    def test_sales_staff_cannot_access_hr_page(self):
        self.set_role('sales')
        response = self.client.get(reverse('hr'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_inventory_staff_cannot_access_sales_page(self):
        self.set_role('inventory')
        response = self.client.get(reverse('pos'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_staff_can_access_daily_tasks_only(self):
        self.set_role('staff')
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        blocked = self.client.get(reverse('pos'))
        self.assertEqual(blocked.status_code, 302)
        self.assertEqual(blocked.url, reverse('dashboard'))

    def test_owner_and_finance_can_access_reports_and_management_modules(self):
        allowed = {
            'owner': ['dashboard', 'inventory', 'pos', 'hr', 'reports', 'applications', 'tasks'],
            'finance': ['dashboard', 'inventory', 'pos', 'hr', 'reports'],
        }
        for role, names in allowed.items():
            self.set_role(role)
            for name in names:
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200, f'{role} failed on {name}')

    def test_dashboard_is_only_for_owner_and_finance(self):
        self.set_role('sales')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pos'))

        self.set_role('finance')
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
