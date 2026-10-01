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

    def test_finance_can_access_only_finance_pages(self):
        self.set_role('finance')
        for name in ['dashboard', 'reports']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f'finance failed on {name}')

        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, reverse('reports'))
        for name in ['inventory', 'pos', 'hr', 'hr_attendance', 'hr_payroll', 'hr_applicants', 'hr_employees', 'applications', 'tasks']:
            self.assertNotContains(response, reverse(name))

        for name in ['inventory', 'pos', 'hr', 'hr_attendance', 'hr_payroll', 'hr_applicants', 'hr_employees', 'applications', 'tasks']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, f'finance unexpectedly accessed {name}')
            self.assertEqual(response.url, reverse('dashboard'))

    def test_owner_can_access_management_modules(self):
        self.set_role('owner')
        for name in ['dashboard', 'inventory', 'pos', 'hr', 'reports', 'applications', 'tasks']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f'owner failed on {name}')

    def test_dashboard_is_only_for_owner_and_finance(self):
        self.set_role('sales')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('pos'))

        self.set_role('finance')
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)

    def test_view_mode_switch_is_available_on_login_and_app_pages(self):
        login_response = self.client.get(reverse('login'))
        self.assertContains(login_response, 'data-view-mode-choice="mobile"')
        self.assertContains(login_response, 'data-view-mode-choice="desktop"')
        self.assertContains(login_response, 'farm_management/view-mode.js')

        self.set_role('owner')
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertNotContains(dashboard_response, 'data-view-mode-choice="mobile"')
        self.assertContains(dashboard_response, 'farm_management/view-mode.js')

    def test_credential_login_preview_is_linked_and_renders_fields(self):
        login_response = self.client.get(reverse('login'))
        self.assertContains(login_response, reverse('credential_login'))

        preview_response = self.client.get(reverse('credential_login'))
        self.assertEqual(preview_response.status_code, 200)
        self.assertContains(preview_response, 'name="username"')
        self.assertContains(preview_response, 'name="password"')
        self.assertContains(preview_response, 'Sign in')
        self.assertNotContains(preview_response, 'data-view-mode-choice')
        self.assertNotContains(preview_response, 'Back to role selection')
        self.assertContains(preview_response, f'window.location.assign("{reverse("login")}")')

    def test_owner_dashboard_shows_inventory_mix_but_finance_does_not(self):
        self.set_role('owner')
        owner_response = self.client.get(reverse('dashboard'))
        self.assertContains(owner_response, 'Inventory Mix')
        self.assertContains(owner_response, 'Vegetables')
        self.assertContains(owner_response, '50%')

        self.set_role('finance')
        finance_response = self.client.get(reverse('dashboard'))
        self.assertNotContains(finance_response, 'Inventory Mix')
