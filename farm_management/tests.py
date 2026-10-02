from django.test import TestCase
from django.urls import reverse


class RoleBasedAccessTests(TestCase):
    def set_role(self, role):
        session = self.client.session
        session['role'] = role
        session.save()

    def test_sales_staff_has_separate_sales_and_reporting_pages(self):
        self.set_role('sales')
        for name in ['sales_entry', 'sales_reports']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f'sales failed on {name}')

        response = self.client.get(reverse('hr'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_inventory_staff_has_separate_record_and_information_pages(self):
        self.set_role('inventory')
        for name in ['inventory_entry', 'inventory_info']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f'inventory failed on {name}')

        response = self.client.get(reverse('pos'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_inventory_mock_exposes_required_categories_and_movements(self):
        self.set_role('inventory')
        response = self.client.get(reverse('inventory_entry'))
        for category in ['Poultry', 'Hydroponics', 'Bees', 'Soda', 'Services']:
            self.assertContains(response, category)
        for movement in ['Inbound', 'Harvest', 'Sale', 'Spoilage']:
            self.assertContains(response, movement)
        self.assertContains(response, 'Recorded by demo account:')
        self.assertContains(response, 'id="supplier-field" hidden')

    def test_sales_mock_starts_without_items_and_requires_one_to_complete(self):
        self.set_role('sales')
        response = self.client.get(reverse('sales_entry'))
        for category in ['Poultry', 'Hydroponics', 'Bees', 'Soda', 'Services']:
            self.assertContains(response, category)
        self.assertContains(response, 'Required: add at least one')
        self.assertContains(response, 'id="complete-sale" type="submit" class="primary-btn" disabled')
        self.assertContains(response, 'Processed by demo account:')

    def test_staff_can_access_daily_tasks_only(self):
        self.set_role('staff')
        response = self.client.get(reverse('tasks'))
        self.assertEqual(response.status_code, 200)
        blocked = self.client.get(reverse('pos'))
        self.assertEqual(blocked.status_code, 302)
        self.assertEqual(blocked.url, reverse('dashboard'))

    def test_finance_can_access_only_finance_pages(self):
        self.set_role('finance')
        for name in ['dashboard', 'reports', 'finance']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f'finance failed on {name}')

        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, reverse('reports'))
        self.assertContains(response, reverse('finance'))
        for name in ['inventory', 'pos', 'hr', 'hr_attendance', 'hr_payroll', 'hr_applicants', 'hr_employees', 'applications', 'tasks', 'people']:
            self.assertNotContains(response, reverse(name))

        for name in ['inventory', 'pos', 'hr', 'hr_attendance', 'hr_payroll', 'hr_applicants', 'hr_employees', 'applications', 'tasks', 'people']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, f'finance unexpectedly accessed {name}')
            self.assertEqual(response.url, reverse('dashboard'))

    def test_owner_can_access_dashboard_reports_people_and_operations(self):
        self.set_role('owner')
        for name in ['dashboard', 'reports', 'people', 'operations']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, f'owner failed on {name}')

        for name in ['inventory', 'pos', 'hr', 'hr_attendance', 'hr_payroll', 'hr_applicants', 'hr_employees', 'applications', 'tasks']:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, f'owner unexpectedly accessed {name}')
            self.assertEqual(response.url, reverse('dashboard'))

    def test_sales_dashboard_redirects_to_sales_entry(self):
        self.set_role('sales')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('sales_entry'))

        self.set_role('finance')
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)

    def test_view_mode_switch_is_available_on_login_and_app_pages(self):
        login_response = self.client.get(reverse('login'))
        self.assertContains(login_response, 'data-view-mode-choice="mobile"')
        self.assertContains(login_response, 'data-view-mode-choice="desktop"')
        self.assertContains(login_response, 'farm_management/view-mode.')

        self.set_role('owner')
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertNotContains(dashboard_response, 'data-view-mode-choice="mobile"')
        self.assertContains(dashboard_response, 'farm_management/view-mode.')

    def test_credential_login_preview_is_linked_and_renders_fields(self):
        login_response = self.client.get(reverse('login'))
        self.assertContains(login_response, 'name="username"')
        self.assertContains(login_response, 'name="password"')

        preview_response = self.client.get(reverse('credential_login'))
        self.assertRedirects(preview_response, reverse('login'))

    def test_demo_credentials_sign_in_to_the_matching_role(self):
        destinations = {
            'owner': 'dashboard',
            'finance': 'dashboard',
            'sales': 'sales_entry',
            'inventory': 'inventory_entry',
            'hr': 'hr',
            'staff': 'tasks',
        }
        for role, destination in destinations.items():
            response = self.client.post(reverse('login'), {
                'username': role,
                'password': role,
            }, follow=True)
            self.assertEqual(self.client.session['role'], role)
            self.assertEqual(response.redirect_chain[-1][0], reverse(destination))

    def test_invalid_demo_credentials_do_not_sign_in(self):
        response = self.client.post(reverse('login'), {
            'username': 'owner',
            'password': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password.')
        self.assertNotIn('role', self.client.session)

    def test_owner_dashboard_shows_inventory_mix_but_finance_does_not(self):
        self.set_role('owner')
        owner_response = self.client.get(reverse('dashboard'))
        self.assertContains(owner_response, 'Inventory Mix')
        self.assertContains(owner_response, 'Vegetables')
        self.assertContains(owner_response, '50%')

        self.set_role('finance')
        finance_response = self.client.get(reverse('dashboard'))
        self.assertNotContains(finance_response, 'Inventory Mix')
