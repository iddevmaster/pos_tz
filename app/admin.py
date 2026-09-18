from django.contrib import admin
from .models import register_main, register_payment, location_thai, pos_machine,user_group,user_detail,category_program,pay_item
# Register your models here.
admin.site.register(register_main)
admin.site.register(register_payment)
admin.site.register(location_thai)
admin.site.register(pos_machine)
admin.site.register(user_group)
admin.site.register(user_detail)
admin.site.register(category_program)
admin.site.register(pay_item)

from django.core.exceptions import PermissionDenied
from django.urls import path, reverse
from django.utils.html import format_html
from .models import CertificateLayout


@admin.register(CertificateLayout)
class CertificateLayoutAdmin(admin.ModelAdmin):
    list_display = ('language', 'updated_at', 'designer_link')
    fields = ('language', 'designer_link', 'updated_at')
    readonly_fields = ('designer_link', 'updated_at')
    change_list_template = 'admin/certificate_layout_list.html'

    @admin.display(description='ออกแบบ')
    def designer_link(self, obj):
        if not obj or not obj.pk:
            return 'บันทึกก่อนเพื่อเปิดหน้าออกแบบ'
        return format_html('<a href="{}">ลากวางใบประกาศ</a>', reverse('admin:certificate_designer', args=[obj.language]))

    def get_urls(self):
        return [path('design/<str:language>/', self.admin_site.admin_view(self.designer), name='certificate_designer')] + super().get_urls()

    def designer(self, request, language):
        if language not in ('th', 'eng'):
            from django.http import Http404
            raise Http404
        obj = CertificateLayout.objects.filter(language=language).first()
        if not (self.has_change_permission(request, obj) if obj else self.has_add_permission(request)):
            raise PermissionDenied
        from .views.certificate_settings import designer_response
        return designer_response(request, language, obj, self.admin_site.each_context(request))
