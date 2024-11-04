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