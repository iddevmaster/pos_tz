
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import course, finance, register, master_data, general, api, teacher, user, report_and_print,project,desbill

urlpatterns = [
    # Register
    path('', register.register_home),
    path('salesnotevent', register.register_homenotevent),
    path('salesnotevent/create/', register.register_createnoevent, name="CreateRegisterNo"),
    path('salesnotevent/reset', register.register_resetnoevent),
    path('salesnotevent/customer/create/',
         register.customer_createno, name="CreateCustomerNo"),
    path('salesnotevent/payment/<str:register_id>', register.paymentnoevent),
    path('salesnotevent/payment/create/', register.payment_createno, name="CreatePaymentno"),
    path('salesnotevent/payment/history/<str:register_id>', register.payment_historyno),
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
    path('approve/update/processevent', register.approve_lis_event_end),
    path('approve/update/processeventend',
         register.update_close_the_eventend, name="UpdateCloseEndTheEvent"),
    path('approve/update/event', register.approve_lis_event),
    path('approvebill/update/bill', register.approve_list_payment),
    path('approvebill/update/bill2', register.approve_list_payment_update, name="UpdateCloseEndTheEventAll"
    ),
    path('approvebill/accept/<slug:pk>',
         register.approve_list_payment_accept  ,name='acceptbill'),
    path('approve/update/eventdate', course.approve_listevent),
 
    path('register/update/event',
         register.update_close_the_event, name="UpdateCloseTheEvent"),
    path('register/update/delete',
         register.delete_close_the_event, name="DeleteCloseTheEvent"),    
    path('approve/documents/internal', register.approve_internal),
    path('approve/documents/internal/view/<slug:doc_id>', register.approve_internal_doc),
    path('approve/documents/internal/print/view/<slug:doc_id>', register.approve_internal_doc_print),

    path('approv/internal/manage', register.approve_manage),
    path('approv/internal/gm', register.approve_gm),
    path('approv/save/gm', register.approve_gm_save),
    path('approv/save/mange', register.approve_mange_save),
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
    path('calendar_event_staff/', course.calendar_event_staff),
    path('calendar_event_all/', course.calendar_event_all),
    path('calendar_event_api/', course.calendar_event_api),
    
    path('calendar_event_apieve/', course.calendar_event_apizs),
    path('calendar_event_apiall/', course.calendar_event_apiall),
    path('calendar_event_apiall_com/', course.calendar_event_apiallcom),
    path('calendar_event_apiteacher/', course.calendar_event_apiteacher),

    path('calendar_event_api_totalbill/', course.calendar_event_api_totalbill),

    path('condition/management/', course.conditionlist),
    path('condition/management/<slug:conhead_id>', course.conditioncreate),
    path('condition/form/delete', course.condition_form_delete,
         name="conditionr_form_delete"),
    path('condition/form/save', course.condition_form_save,
         name="CreateConditioneEvent"),     
    path('condition/form/update', course.condition_form_update,
         name="UpdateConditioneEvent"),

    path('api/updateeventcondition', course.condition_form_update_event),
    path('api/savetax', desbill.savetax),
    path('api/savesettingbill', desbill.savesettingbill),
    path('api/findevid', desbill.findbillevid),
    

    #     teacher
    path('teachers/', teacher.teacher_list),
    path('teachersoutsource/', teacher.teacher_list),
    path('teacher/form/create', teacher.teacher_form_create,
         name="teacher_form_create"),
    path('teacher/form/update/<slug:teacher_id>',
         teacher.teacher_form_update, name="teacher_form_update"),
    path('teacher/form/delete', teacher.teacher_form_delete,
         name="teacher_form_delete"),
    path('calendarteachers', teacher.teacher_list_cale),
    path('licenteachers', teacher.teacher_list_licen),
    path('licenteachers/form/create', teacher.teacher_formlicen_create,
         name="teacher_formlicen_create"),
    path('licenteachers/update/', teacher.teacher_formlicen_update,
         name="UpdateLic"),          
    path('approvlicen', teacher.teacher_list_appv),
    path('approvlicen/form/delete', teacher.teacher_appv_delete,
         name="approvlicen_form_delete"),
    path('approvlicen/form/de', teacher.teacher_appv_de,
         name="approvlicen_form_de"),

    path('register/event/all', register.report_register_re),
    path('register/event/teacher', register.report_register_teacher),
    path('register/report/event/all', register.report_register),
    path('register/event/all/report/list/<slug:evs_id>', register.report_register_list),
    path('register/event/teacher/list/<slug:evs_id>', register.report_register_listteacher),


    path('register/report/event/all/report/list/<slug:evs_id>', register.report_register_listall),

    path('register/student/form/create/<str:ev_id>', register.register_form_create),
    path('register/student/form/store/<str:ev_id>', register.register_form_store ,name="StoreStudent"),
    path('register/student/form/show/<str:ev_id>/<str:training_id>', register.register_form_show ,name="ShowStudent"),
    path('register/student/form/update/<str:ev_id>/<str:training_id>', register.register_form_update),
    path('register/student/delete',
         register.register_delete, name="RegisterFormDelete"),

    path('register/all/student/form/create/<str:ev_id>', register.register_form_createall),
    path('register/all/student/form/store/<str:ev_id>', register.register_form_storeall ,name="StoreStudentAll"),
    path('register/all/student/form/show/<str:ev_id>/<str:training_id>', register.register_form_showall ,name="ShowStudentAll"),
    path('register/all/student/form/update/<str:ev_id>/<str:training_id>', register.register_form_updateall),
    path('register/all/student/delete',
         register.register_deleteall, name="RegisterFormDeleteAll"),     


    path('projectlist/', project.project_list),
    path('projectlist/event/delete/', project.project_event_delete,
         name="DeleteProjectEvent"),
    path('projectlist/create/', project.project_event_create,
         name="CreateProjectCodeEvent"),
    path('projectlist/update/', project.project_event_update,
         name="UpdateProjectCodeEvent"),
     
    # Master Data
    path('locationthai/', master_data.get_locationThai),
    path('api/customer', register.get_customer_data),

    # General
    path('login/', general.login),
    path('logout/', general.logout),
    path('authen_check/', general.login_check, name="LoginCheck"),

    # print / export / report
    path('report/register/export/seller',
         report_and_print.register_selller_report),
    path('report/register/export/seller/event',
         report_and_print.register_selller_report_event),     
    path('report/register/export/quotation',
         report_and_print.register_report_quotation),
    path('report/register/export/bill', report_and_print.register_report_bill),
    path('report/register/export/bill/today', report_and_print.register_report_billtoday),
    path('report/summarize/export/bill/today', report_and_print.register_report_billtoday_summarize),
    path('report/teacher/export', report_and_print.register_report_compensation),
    path('report/teacher/export/withdraw', report_and_print.register_report_compensation_withdraw),
    path('teacher/print/witdraw/<str:teacher_id>/<str:start>/<str:end>', report_and_print.register_print_witdraw),
    path('report/teacher/export/onemore', report_and_print.register_report_compensation_withdraw_onemore),
    path('report/teacher/export/withdraw/onemore', report_and_print.register_report_compensation_withdraw_onemorefitter),
    

    path('report/withdraw/all/summary', report_and_print.register_report_summary),
    path('report/withdraw/all/summary/withdraw', report_and_print.register_report_summary_withdraw),
    path('teacher/print/all/summary/<str:start>/<str:end>', report_and_print.register_report_summary_print),
    path('teacher/print/all/overdue/<str:year>/<str:m>', report_and_print.register_report_summary_print_overdue),
    path('teacher/print/overdue/<str:teacher_id>/<str:year>/<str:m>', report_and_print.register_report_summary_print_overdue_one),



    path('report/withdraw/all/summary/teacher', report_and_print.register_report_summary_teacher),
    path('report/withdraw/all/withdraw', report_and_print.register_report_summary_teacher_withdraw),
    path('report/withdraw/all/summary/teacher/<str:teacher_id>/<str:year>/<str:m>', report_and_print.register_report_summary_teacher_all),
    path('report/withdraw/all/summary/teacher/<str:year>/<str:m>', report_and_print.register_report_summary_teacher_all_month),


    path('report/withdraw/all/withdraw/comm', report_and_print.register_report_summary_user_withdraw_com),
    path('report/withdraw/all/summary/overdue', report_and_print.register_report_summary_user_withdraw_com_overdue),


    path('report/overdue/all/com', report_and_print.register_report_summary_com),  #ค้างจ่ายค่าคอม
    path('report/withdraw/all/com', report_and_print.register_report_summary_sale_com), #ตั้งเบิกค่าคอม

    path('report/register/export/learning_status',
         report_and_print.register_report_learn_status),
    path('report/register/export/approve_list',
         report_and_print.register_report_approve),
    path('register/print/<slug:rp_id>', report_and_print.register_print),
    

    path('salesnotevent/print/<slug:rp_id>', report_and_print.register_printnoev),
    path('register/excel/seller', report_and_print.register_excel_seller),
    path('register/excel/seller/accpept/<slug:ev_id>', report_and_print.register_excel_seller_accept),
    path('register/excel/quotation', report_and_print.register_excel_quotation),
    path('register/excel/bill', report_and_print.register_excel_bill),
    path('register/excel/bill/today', report_and_print.register_excel_billtoday),
    path('summarize/excel/bill/today', report_and_print.register_excel_billtoday_summarize),
    path('register/excel/learning_status',
         report_and_print.register_excel_learn_status),
    path('certificate/print/<slug:student_id>',
         report_and_print.student_print_certificate),
    path('manual/idcard', general.manual_idcard),
    path('register/excel/seller/view/<slug:doc_id>', report_and_print.register_excel_seller_view),

    #     user
    path('user/category/list', user.category_program_form_create,
         name="category_program_form_create"),
    path('user/category/delete', user.category_program_form_delete,
         name="category_program_form_delete"),
    path('user/category/clusterting/<slug:pk>',
         user.category_program_form_permission, name="category_program_form_delete"),
    #     finance
#     path('finance/billing/result', finance.billing_cycle_result),
    path('finance/billing/setting', finance.course_event_list),
    path('billing/setting/form/create', finance.billing_cycle_setting_form_create,
         name="billing_cycle_setting_form_create"),
    path('billing/setting/form/delete', finance.billing_cycle_setting_form_delete,
         name="billing_cycle_setting_form_delete"),
    path('course/event/teachers/form/create/<slug:ev_id>',
         finance.course_teacher_event_set_income_form_create),
    path('course/event/teacher/form/delete', finance.course_teacher_event_set_income_form_delete,
         name="course_teacher_event_set_income_form_delete"),

#     path('finance/teacher', finance.withdraw_list), 
    path('finance/teacher', finance.withdraw_list_one),
    path('finance/sale/commission', finance.withdraw_list_commission),
    path('finance/sale/com', finance.withdraw_list_one_com),

    path('finance/overduepayment', finance.withdraw_list_overduepayment),
    path('finance/overduepayment/<slug:register_id>', finance.withdraw_list_overduepayment_details),
   

    path('description/setting/form/create', desbill.setting_form_create,
         name="description_setting_form_create"),
    path('description/setting/form/delete', desbill.setting_form_delete,
         name="description_setting_form_delete"),
    path('description/setting/form/update', desbill.setting_form_update,
         name="description_setting_form_update"), 
    path('tax/setting/form/create', desbill.setting_form_tax,
         name="tax_setting_form_create"),
    path('setting/form/bill/create', desbill.setting_form_bill,
         name="bill_setting_form_create"),     
    path('commissionstages/setting/form/create', desbill.setting_form_commissionstages,
         name="com_setting_form_create"),
    path('commissionstage/setting/form/create', desbill.setting_form_commissionstages_create,
         name="com_setting_form_create"),  
     path('commissionstage/setting/form/update', desbill.setting_form_commissionstages_update,
         name="com_setting_form_update"),    
     path('commissionstage/setting/form/delete', desbill.setting_form_commissionstages_delete,
         name="com_setting_form_delete"),

    path('consent/print/<slug:training_id>',report_and_print.print_consent),


        
         
    path('api/sequence/up', desbill.up),
    path('api/sequence/down', desbill.down),     
    #     public
    path('public/form/certificate', report_and_print.public_form_print),
    path('api/get/compensation', finance.course_teacher_event_get_income_form_compo),
    path('api/calendar_event_api2/<slug:id>/', course.calendar_event_api2),

    path('api/checkhours', finance.checkhours),
    path('api/updateeve', course.updateeve),
    path('api/updatstatusev', course.updatstatusev),
    path('api/getgen', course.getgen),
    path('api/updatestatusproject', project.updatestatus),
    path('api/saveevenet', finance.saveeventadmin),
    path('api/evenetdel', finance.evenetdel),
    path('api/upload/uploadfilestu', register.upload_excel),
    path('api/upload/uploadfileev', register.upload_excel_ev),
    path('api/studentlist', register.listdata),
    path('api/tests', register.tests),
    path('api/data', register.testsdata),

    path('api/courseupdateeve', course.update_course_even),
    path('api/updateteachincome', finance.updateteachincom),
    path('api/saveaddon', register.addon_create),
    path('api/deleteaddon', register.addon_delete),

    path('api/condition/conditionhead', course.conditionhead),
    path('api/condition/createcondition', course.conditionheadcreate),
    path('api/condition/savecondition', course.conditionheadsave),
    path('api/condition/deletecondition', course.conditionheaddel),

    
    path('api/card/register', register.insertcard),
    path('api/sendwithdraw', finance.sendwithdraw),
    path('api/sendwithdrawcom', finance.sendwithdrawcom),

    path('api/calendar_event_api_data', desbill.data_event),
    path('api/calendar_event_api_bill', desbill.data_bill),
    path('api/calendar_event_api_billevent', desbill.data_bill_event),
    path('api/calendar_event_api_com', desbill.data_com),
    path('api/calendar_event_api_user', desbill.user_com),
    path('api/calendar_event_api_update_com', desbill.update_com),

     path('calendar_event_apiall_overdue/', course.calendar_event_apialloverdue),
     path('api/bill_overdue', desbill.data_bill_overdue),

    #     API
    path('api/student/<str:date>', api.studentReport.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.MEDIA_ROOT)
