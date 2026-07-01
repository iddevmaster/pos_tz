from django.contrib import admin
from .models import register_main, register_payment, location_thai, pos_machine,user_group,user_detail,category_program,pay_item
from .models import commission_policy, commission_condition, commission_payee, commission_rule, commission_rule_allocation, commission_plan, commission_plan_line, commission_plan_allocation, commission_payout
# Register your models here.
admin.site.register(register_main)
admin.site.register(register_payment)
admin.site.register(location_thai)
admin.site.register(pos_machine)
admin.site.register(user_group)
admin.site.register(user_detail)
admin.site.register(category_program)
admin.site.register(pay_item)
admin.site.register(commission_policy)
admin.site.register(commission_condition)
admin.site.register(commission_payee)
admin.site.register(commission_rule)
admin.site.register(commission_rule_allocation)
admin.site.register(commission_plan)
admin.site.register(commission_plan_line)
admin.site.register(commission_plan_allocation)
admin.site.register(commission_payout)