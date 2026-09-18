import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import PermissionDenied, ValidationError
from django.test import SimpleTestCase, RequestFactory, TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import render_to_string

from .admin import CertificateLayoutAdmin
from .certificate_layout import certificate_elements, render_elements, validate_layout
from .models import CertificateLayout


class CertificateLayoutTests(SimpleTestCase):
    def test_default_elements_fit_on_page(self):
        fields = ('x', 'y', 'w', 'h', 'size', 'bold', 'color', 'align', 'opacity', 'z', 'visible', 'locked')
        for language in ('th', 'eng'):
            elements = certificate_elements(language)
            self.assertEqual(len(elements), 24)
            layout = {e['id']: {p: e[p] for p in fields} for e in elements}
            self.assertEqual(validate_layout(layout, language), layout)

    def test_rejects_invalid_or_unsafe_properties(self):
        for layout in [[], {'unknown': {}}, {'title': {'x': float('nan')}},
                       {'title': {'x': True}}, {'title': {'color': 'red;display:none'}},
                       {'title': {'w': 297}}, {'title': {'visible': 'false'}},
                       {'student_name': {'text': 'Forged name'}},
                       {'signature': {'value': 'javascript:alert(1)'}}]:
            with self.subTest(layout=layout), self.assertRaises(ValidationError):
                validate_layout(layout, 'th')

    def test_real_data_is_preserved_when_moving_elements(self):
        student = SimpleNamespace(student_prefix_th='นาย', student_firstname_th='ทดสอบ', student_lastname_th='ระบบ', student_code='A&B')
        result = {e['id']: e for e in render_elements('th', {'student_name': {'x': 10}}, student)}
        self.assertEqual(result['student_name']['value'], 'นาย ทดสอบ ระบบ')
        self.assertEqual(result['student_name']['x'], 10)
        self.assertIn('A%26B', result['qr']['value'])

    def test_template_escapes_script_in_text(self):
        html = render_to_string('print/student_print_certificate_layout.html', {
            'elements': render_elements('th', {'title': {'text': '</script><script>alert(1)</script>'}}),
            'print': 'false',
        })
        self.assertNotIn('</script><script>alert(1)', html)
        self.assertNotIn('window.print()', html)

    def test_custom_text_and_visibility_render(self):
        items = {e['id']: e for e in render_elements('eng', {'title': {'text': 'Custom', 'visible': False}})}
        self.assertEqual(items['title']['value'], 'Custom')
        self.assertFalse(items['title']['visible'])

    def test_admin_permission_and_save_validation(self):
        admin = CertificateLayoutAdmin(CertificateLayout, AdminSite())
        request = RequestFactory().post('/admin/design/th/', data=json.dumps({'title': {'x': 2}}), content_type='application/json')
        request.user = MagicMock()
        request.user.has_perm.return_value = False
        with patch.object(CertificateLayout.objects, 'filter') as query:
            query.return_value.first.return_value = CertificateLayout(language='th')
            with self.assertRaises(PermissionDenied):
                admin.designer(request, 'th')
            request.user.has_perm.return_value = True
            with patch.object(CertificateLayout.objects, 'update_or_create') as save:
                response = admin.designer(request, 'th')
                self.assertEqual(response.status_code, 200)
                save.assert_called_once_with(language='th', defaults={'layout': {'title': {'x': 2}}})
                request = RequestFactory().post('/admin/design/th/', data='{"title":{"x":999}}', content_type='application/json')
                request.user = MagicMock()
                self.assertEqual(admin.designer(request, 'th').status_code, 400)
                self.assertEqual(save.call_count, 1)


class CertificateLayoutIntegrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='designer_test', password='test-only')
        self.client.force_login(self.user)
        self.url = reverse('admin:certificate_designer', args=['th'])

    def test_save_reload_and_language_isolation(self):
        self.assertContains(self.client.get(self.url), 'certificate-page')
        layout = {'title': {'text': 'Saved title', 'x': 15}}
        response = self.client.post(self.url, json.dumps(layout), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CertificateLayout.objects.get(language='th').layout, layout)
        self.assertContains(self.client.get(self.url), 'Saved title')
        self.assertNotContains(self.client.get(reverse('admin:certificate_designer', args=['eng'])), 'Saved title')

    def test_csrf_and_staff_permissions_are_required(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        self.assertEqual(csrf_client.post(self.url, '{}', content_type='application/json').status_code, 403)
        self.user.is_superuser = False
        self.user.save()
        self.assertEqual(self.client.get(self.url).status_code, 403)

    def test_main_site_sidebar_and_language_links(self):
        response = self.client.get(reverse('certificate_settings'))
        self.assertContains(response, 'ตั้งค่าใบเซอร์')
        self.assertContains(response, 'id="sidebar"')
        self.assertContains(response, reverse('certificate_settings_language', args=['eng']))
        self.assertContains(response, 'certificate_layout.css')
        self.assertNotContains(response, 'กลับรายการแม่แบบ')

    def test_main_site_save_uses_same_layout_and_protects_access(self):
        url = reverse('certificate_settings_language', args=['eng'])
        response = self.client.post(url, json.dumps({'title': {'text': 'Main site'}}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CertificateLayout.objects.get(language='eng').layout['title']['text'], 'Main site')
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)
        self.assertEqual(csrf_client.post(url, '{}', content_type='application/json').status_code, 403)
        self.user.is_superuser = False
        self.user.save()
        self.assertEqual(self.client.get(url).status_code, 403)
        self.assertEqual(self.client.post(url, '{}', content_type='application/json').status_code, 403)
        self.client.logout()
        self.assertRedirects(self.client.get(url), '/login/?next=' + url, fetch_redirect_response=False)

    def test_saved_layout_is_used_by_print_view(self):
        from .views.report_and_print import student_print_certificate
        person = SimpleNamespace(student_prefix_th='นาย', student_firstname_th='ทดสอบ', student_lastname_th='ระบบ', student_code='TEST', register=SimpleNamespace(ev_id=1))
        event = SimpleNamespace(ev_logo=None, course=SimpleNamespace(course_name='หลักสูตร', course_name_eng='Course'), ev_date_end=None, ev_date_start=None, ev_expired_cer_date=None)
        CertificateLayout.objects.create(language='th', layout={'title': {'text': 'Saved title'}})
        with patch('app.views.report_and_print.student.objects.select_related') as students, patch('app.views.report_and_print.course_event.objects.select_related') as events:
            students.return_value.get.return_value = person
            events.return_value.get.return_value = event
            response = student_print_certificate(RequestFactory().get('/certificate/print/test', {'lang': 'th', 'print': 'false'}), 'test')
            self.assertContains(response, 'Saved title')
            self.assertContains(response, 'certificate-elements')
