import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse, HttpResponseNotAllowed, Http404
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from ..models import CertificateLayout, student, course_event, user_detail, category_program_permission
from ..certificate_layout import certificate_elements, render_elements, validate_layout


@login_required(login_url='/login/')
def certificate_settings(request, language='th'):
    if language not in ('th', 'eng'):
        raise Http404
    if not request.user.is_active or not request.user.is_staff:
        raise PermissionDenied
    obj = CertificateLayout.objects.filter(language=language).first()
    permission = 'app.change_certificatelayout' if obj else 'app.add_certificatelayout'
    if not request.user.has_perm(permission):
        raise PermissionDenied
    context = {'designer_base': 'base.html', 'main_site': True}
    if request.method == 'GET':
        profile = user_detail.objects.filter(user_id=request.user.pk).first()
        permissions = category_program_permission.objects.filter(cm_id=profile.cm_id if profile else 0)
        groups = permissions.values('group_value', 'group_label').annotate(dcount=Count('group_value')).order_by('group_label')
        context['listMenuPermission'] = [
            {**group, 'children': permissions.filter(group_value=group['group_value']).order_by('page_label')}
            for group in groups
        ]
    return designer_response(request, language, obj, context)


def designer_response(request, language, obj, extra_context):
    if request.method == 'POST':
        try:
            if len(request.body) > 100000:
                raise ValidationError('ข้อมูลมีขนาดใหญ่เกินไป')
            layout = validate_layout(json.loads(request.body), language)
        except (ValueError, ValidationError) as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        CertificateLayout.objects.update_or_create(language=language, defaults={'layout': layout})
        return JsonResponse({'ok': True})
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET', 'POST'])
    person = event = None
    if request.GET.get('student'):
        person = get_object_or_404(student.objects.select_related('register'), pk=request.GET['student'])
        event = get_object_or_404(course_event.objects.select_related('course'), ev_id=person.register.ev_id)
    context = {
        **extra_context,
        'title': 'ออกแบบใบประกาศ — ' + ('ไทย' if language == 'th' else 'English'),
        'elements': render_elements(language, obj.layout if obj else {}, person, event),
        'defaults': certificate_elements(language, person, event),
        'language': language,
    }
    return render(request, 'admin/certificate_designer.html', context)
