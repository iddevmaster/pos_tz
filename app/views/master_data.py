from django.http.response import JsonResponse
from django.db.models import Q
from ..models import location_thai


def get_locationThai(request):
    try:
        searchTerm = request.POST['searchTerm']
    except KeyError:
        searchTerm = None
        return JsonResponse({'status': "Fail", 'message': 'ไม่พบข้อมูล'}, safe=False)
    try:
        content = location_thai.objects.filter(Q(district_name__icontains=searchTerm) |
                                               Q(amphur_name__icontains=searchTerm) |
                                               Q(province_name__icontains=searchTerm) |
                                               Q(zipcode__icontains=searchTerm))[:25]
    except location_thai.DoesNotExist:
        content = None
        return JsonResponse({'status': "Fail", 'message': 'ไม่พบข้อมูล'}, safe=False)
    context = []
    for re in content:
        text = str(re.district_name) + ' - ' + \
            str(re.amphur_name) + ' - ' + \
            str(re.province_name) + ' ' + str(re.zipcode)
        list = {'id': re.location_id, 'text': text}
        context.append(list)
    return JsonResponse(context, safe=False)
