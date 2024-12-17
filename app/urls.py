
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import course, finance, register, master_data, general, api, teacher, user, report_and_print

urlpatterns = [
    # Register
    path('', register.register_home),
    path('register/', register.register_home),
    path('register/create/', register.register_create, name="CreateRegister"),
    path('register/reset', register.register_reset),
    path('register/customer/create/',
         register.customer_create, name="CreateCustomer"),
    path('register/customer/read_idcard/', register.customer_read_idcard),
    path('register/payment/<str:register_id>', register.payment),
    path('register/payment/update/<str:register_id>',
         register.payment_form_update),
    path('register/payment/create/', register.payment_create, name="CreatePayment"),
    path('register/payment/history/<str:register_id>', register.payment_history),
    path('register/management', register.register_management),
    path('register/update/close_the_sale',
         register.update_close_the_sale, name="UpdateCloseTheSale"),
    path('register/detail/<str:register_id>', register.register_detail),
    path('register/cancle', register.register_cancle, name="CancleRegister"),
    path('register/studentlist/<str:register_id>', register.student_list),
    path('student/ref/create',
         register.student_ref_create, name="StudentRefCreate"),
    path('student/form/create/<str:register_id>', register.student_form_create),
    path('student/form/update/<str:student_id>', register.student_form_update),
    path('student/delete',
         register.student_delete, name="StudentDelete"),
    path('student/create/idcard',
         register.student_create_idcard),
    path('student/update/status',
         register.student_update_status, name="StudentUpdateStatus"),
    path('student/update/status/all',
         register.student_update_status_all, name="StudentUpdateAllStatus"),
    path('register/certificate/<str:student_id>',
         register.student_form_certificate),
    path('register/approve/create',
         register.register_approve_create, name="RegisterApproveCreate"),

    # Approve
    path('approve/update/payment', register.approve_list),
    path('approve/update/set', register.approve_update_status,
         name="ApproveSetStatus"),
    # Course
    path('course/', course.course_list),
    path('create_course/', course.course_create, name="CreateCourse"),
    path('create_update/', course.course_update, name="UpdateCourse"),
    path('course_delete/', course.course_delete, name="DeleteCourse"),
    path('course/event', course.course_event_list),
    path('course/event/create', course.course_event_create,
         name="CreateCourseEvent"),
    path('course/event/update', course.course_event_update,
         name="UpdateCourseEvent"),
    path('course/event/delete/', course.course_event_delete,
         name="DeleteCourseEvent"),
    path('course/event/teachers/list/<slug:ev_id>', course.course_teacher_event_list),
    path('calendar_event/', course.calendar_event),
    path('calendar_event_api/', course.calendar_event_api),

    #     teacher
    path('teachers/', teacher.teacher_list),
    path('teacher/form/create', teacher.teacher_form_create,
         name="teacher_form_create"),
    path('teacher/form/update/<slug:teacher_id>',
         teacher.teacher_form_update, name="teacher_form_update"),
    path('teacher/form/delete', teacher.teacher_form_delete,
         name="teacher_form_delete"),

    # Master Data
    path('locationthai/', master_data.get_locationThai),

    # General
    path('login/', general.login),
    path('logout/', general.logout),
    path('authen_check/', general.login_check, name="LoginCheck"),

    # print / export / report
    path('report/register/export/seller',
         report_and_print.register_selller_report),
    path('report/register/export/quotation',
         report_and_print.register_report_quotation),
    path('report/register/export/bill', report_and_print.register_report_bill),
    path('report/register/export/learning_status',
         report_and_print.register_report_learn_status),
    path('report/register/export/approve_list',
         report_and_print.register_report_approve),
    path('register/print/<slug:rp_id>', report_and_print.register_print),
    path('register/excel/seller', report_and_print.register_excel_seller),
    path('register/excel/quotation', report_and_print.register_excel_quotation),
    path('register/excel/bill', report_and_print.register_excel_bill),
    path('register/excel/learning_status',
         report_and_print.register_excel_learn_status),
    path('certificate/print/<slug:student_id>',
         report_and_print.student_print_certificate),
    path('manual/idcard', general.manual_idcard),

    #     user
    path('user/category/list', user.category_program_form_create,
         name="category_program_form_create"),
    path('user/category/delete', user.category_program_form_delete,
         name="category_program_form_delete"),
    path('user/category/clusterting/<slug:pk>',
         user.category_program_form_permission, name="category_program_form_delete"),
    #     finance
    path('finance/billing/result', finance.billing_cycle_result),
    path('finance/billing/setting', finance.course_event_list),
    path('billing/setting/form/create', finance.billing_cycle_setting_form_create,
         name="billing_cycle_setting_form_create"),
    path('billing/setting/form/delete', finance.billing_cycle_setting_form_delete,
         name="billing_cycle_setting_form_delete"),
    path('course/event/teachers/form/create/<slug:ev_id>',
         finance.course_teacher_event_set_income_form_create),
    path('course/event/teacher/form/delete', finance.course_teacher_event_set_income_form_delete,
         name="course_teacher_event_set_income_form_delete"),
    #     public
    path('public/form/certificate', report_and_print.public_form_print),
    path('api/get/compensation', finance.course_teacher_event_get_income_form_compo),

    #     API
    path('api/student/<str:date>', api.studentReport.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
