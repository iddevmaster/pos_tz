defaultTitle = "Trainingzenter"
webUrl = "http://127.0.0.1:8000"
api_id_card = "https://localhost:8182/thaiid/read.jsonp?callback=callback&section1=true&section2a=true&section2c=true"
key_module = ('tz', 'idss')
prefixThai = (
    ('', 'ไม่ระบุ'),
    ('คุณ', 'คุณ'),
    ('นาย', 'นาย'),
    ('นาง', 'นาง'),
    ('นางสาว', 'นางสาว'),
    ('พลเอก', 'พลเอก'),
    ('พลโท', 'พลโท'),
    ('พลตรี', 'พลตรี'),
    ('พลเรือเอก', 'พลเรือเอก'),
    ('พลเรือโท', 'พลเรือโท'),
    ('พลเรือตรี', 'พลเรือตรี'),
    ('พลอากาศเอก', 'พลอากาศเอก'),
    ('พลอากาศโท', 'พลอากาศโท'),
    ('พลอากาศตรี', 'พลอากาศตรี'),
    ('พันเอก', 'พันเอก'),
    ('พันโท', 'พันโท'),
    ('พันตรี', 'พันตรี'),
    ('ร้อยเอก', 'ร้อยเอก'),
    ('ร้อยโท', 'ร้อยโท'),
    ('ร้อยตรี', 'ร้อยตรี'),
    ('ว่าที่ร้อยตรี', 'ว่าที่ร้อยตรี'),
    ('แพทย์หญิง', 'แพทย์หญิง'),
    ('ทันตแพทย์', 'ทันตแพทย์'),
    ('ทันตแพทย์หญิง', 'ทันตแพทย์หญิง'),
    ('เภสัชกร', 'เภสัชกร'),
    ('เภสัชกรหญิง', 'เภสัชกรหญิง'),
    ('ดร.', 'ดร.'),
    ('ศาสตราจารย์', 'ศาสตราจารย์'),
    ('รองศาสตราจารย์', 'รองศาสตราจารย์'),
    ('ผู้ช่วยศาสตราจารย์', 'ผู้ช่วยศาสตราจารย์'),
    ('อาจารย์', 'อาจารย์'),
)
prefixEng = (
    ('', 'Not specified'),
    ('Mr.', 'Mr.'),
    ('Mrs.', 'Mrs.'),
    ('Miss', 'Miss'),
    ('General', 'General'),
    ('Lieutenant General', 'Lieutenant General'),
    ('Major General', 'Major General'),
    ('Admiral', 'Admiral'),
    ('Vice Admiral', 'Vice Admiral'),
    ('Rear Admiral', 'Rear Admiral'),
    ('Air Chief Marshal', 'Air Chief Marshal'),
    ('Air Marshal', 'Air Marshal'),
    ('Air Vice Marshal', 'Air Vice Marshal'),
    ('Colonel', 'Colonel'),
    ('Lieutenant Colonel', 'Lieutenant Colonel'),
    ('Major', 'Major'),
    ('Captain', 'Captain'),
    ('First Lieutenant', 'First Lieutenant'),
    ('Second Lieutenant', 'Second Lieutenant'),
    ('Acting Second Lieutenant', 'Acting Second Lieutenant'),
    ('Dr.', 'Dr.'),
    ('Dentist', 'Dentist'),
    ('Female Dentist', 'Female Dentist'),
    ('Pharmacist', 'Pharmacist'),
    ('Female Pharmacist', 'Female Pharmacist'),
    ('Professor', 'Professor'),
    ('Associate Professor', 'Associate Professor'),
    ('Assistant Professor', 'Assistant Professor'),
    ('Lecturer', 'Lecturer'),
)
activeChoices = (
    ('1', 'เปิด'),
    ('0', 'ปิด'),
)

Levelchoices = (
    ('1', 'Basic'),
    ('2', 'Level A'),
    ('3', 'Level B'),
    ('4', 'Level C'),
)

teacherTypeChoices = (
    ('1', 'ครูหรือวิทยากรภายใน'),
    ('2', 'ครูหรือวิทยากรภายนอก'),
)

dayChoices = [(str(i), str(i)) for i in range(1, 32)]

thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม",
               "มิถุนายน", "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]

unitPayChoices = (
    ('hour', 'ชั่วโมง'),
    ('day', 'วัน'),
    ('week', 'สัปดาห์'),
    ('month', 'เดือน'),
)

THAI_MONTH_NAMES = [
    (1, 'มกราคม'),
    (2, 'กุมภาพันธ์'),
    (3, 'มีนาคม'),
    (4, 'เมษายน'),
    (5, 'พฤษภาคม'),
    (6, 'มิถุนายน'),
    (7, 'กรกฎาคม'),
    (8, 'สิงหาคม'),
    (9, 'กันยายน'),
    (10, 'ตุลาคม'),
    (11, 'พฤศจิกายน'),
    (12, 'ธันวาคม'),
]


listMenu = [
    {
        "value": "projectlist",
        "label": "ProjectCode",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
    {
        "value": "course",
        "label": "หลักสูตร",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
    {
        "value": "course/event",
        "label": "กำหนดวันอบรมและราคาอบรม",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
    {
        "value": "register/management",
        "label": "ดำเนินการ",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },

    {
        "value": "calendar_event",
        "label": "ปฏิทินหลักสูตรอบรม ผอ",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
       {
        "value": "calendar_event_staff",
        "label": "ปฏิทินหลักสูตรอบรม ผู้จัดการ",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
     {
        "value": "calendar_event_all",
        "label": "ปฏิทินหลักสูตรอบรมทั้งหมด",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
    {
        "value": "condition/management",
        "label": "กำหนดเงื่อนไข",
        "group_value": "pRem5",
        "group_label": "หลักสูตร",
    },
    {
        "value": "teachers",
        "label": "ครู - วิทยากร",
        "group_value": "5lgafI",
        "group_label": "ครู - วิทยากร",
    },
      {
        "value": "calendarteachers",
        "label": "กำหนดวันอบรมและราคาอบรม",
        "group_value": "5lgafI",
        "group_label": "ครู - วิทยากร",
    },
    {
        "value": "licenteachers",
        "label": "ใบอนุญาติขับรถ",
        "group_value": "5lgafI",
        "group_label": "ครู - วิทยากร",
    },
      {
        "value": "approvlicen",
        "label": "อนุมัติใบอนุญาติขับรถ",
        "group_value": "5lgafI",
        "group_label": "ครู - วิทยากร",
    },
    {
        "value": "teachersoutsource",
        "label": "Outsource",
        "group_value": "5lgafI",
        "group_label": "ครู - วิทยากร",
    },

    {
        "value": "approve/update/payment",
        "label": "แก้ไขใบเสร็จ - ใบเสนอราคา",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
    {
        "value": "approve/update/event",
        "label": "อนุมัติรายการ",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
        {
        "value": "approve/documents/internal",
        "label": "เอกสารบันทึกภายใน",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
    {
        "value": "approv/internal/manage",
        "label": "ตรวจสอบและอนุมัติ",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
       {
        "value": "approv/internal/gm",
        "label": "อนุมัติ",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
    {
        "value": "approve/update/processevent",
        "label": "อนุมัติการจบงาน",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
      {
        "value": "approve/update/eventdate",
        "label": "อนุมัติEventอบรม",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
    {
        "value": "approvebill/update/bill",
        "label": "ราคาจ้างเหมา",
        "group_value": "z2NIxi",
        "group_label": "อนุมัติเอกสาร",
    },
    {
        "value": "finance/teacher",
        "label": "รายการเบิกค่าตอบแทน",
        "group_value": "naSt0v",
        "group_label": "การเงิน",
    },
    {
        "value": "finance/billing/setting",
        "label": "กำหนดค่าตอบแทนวันอบรม",
        "group_value": "naSt0v",
        "group_label": "การเงิน",
    },
    {
        "value": "finance/billing/result",
        "label": "สรุปยอดค่าตอบแทน",
        "group_value": "naSt0v",
        "group_label": "การเงิน",
    },
     {
        "value": "finance/teacher/one",
        "label": "ค่าตอบแทน",
        "group_value": "naSt0v",
        "group_label": "การเงิน",
    },

    {
        "value": "billing/setting/form/create",
        "label": "ตัดรอบค่าตอบแทน",
        "group_value": "naSt0v",
        "group_label": "การเงิน",
    },
    {
        "value": "report/register/export/seller",
        "label": "รายงานข้อมูลการขาย",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/register/export/quotation",
        "label": "รายงานข้อมูลใบเสนอราคา",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/register/export/bill",
        "label": "รายงานข้อมูลใบเสร็จ",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
        {
        "value": "report/register/export/bill/today",
        "label": "รายงานข้อมูลใบเสร็จรประจำวัน",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
     {
        "value": "report/summarize/export/bill/today",
        "label": "สรุปรายงานขายประจำวัน",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/register/export/learning_status",
        "label": "รายงานจบ/ไม่จบหลักสูตร",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/register/export/approve_list",
        "label": "รายงานอนุมัติเอกสาร",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/teacher/export",
        "label": "รายงานค่าตอบแทน",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/withdraw/all/summary",
        "label": "สรุปรายชื่อค้างจ่ายครูฝึก",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "report/teacher/export/onemore",
        "label": "รายงานค่าตอบแทนตัวเอง",
        "group_value": "WRltr2",
        "group_label": "รายงาน",
    },
    {
        "value": "register/report/event/all",
        "label": "รายงานผู้เข้าอบรม",
        "group_value": "naSt14",
        "group_label": "ทะเบียนเข้าอบรม",
    },
    {
        "value": "register/event/all",
        "label": "ลงทะเบียนผู้เข้าอบรมทุกหลักสูตร",
        "group_value": "naSt14",
        "group_label": "ทะเบียนเข้าอบรม",
    },
     {
        "value": "register/event/teacher",
        "label": "ลงทะเบียนผู้เข้าอบรม (หน้างาน)",
        "group_value": "naSt14",
        "group_label": "ทะเบียนเข้าอบรม",
    },
        {
        "value": "rt/sale",
        "label": "เปิดการขายแบบไม่มีอีเวน",
        "group_value": "WR14515",
        "group_label": "เปิดการขาย",
    },

    

]

module_description = [
    {
        'module': 'tz',
        'address': '',
        'phone1': "",
        'phone2': "",
        'logo1': "",
        'logo2': ""
    }
]
