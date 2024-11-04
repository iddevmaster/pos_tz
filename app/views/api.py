from rest_framework import generics, permissions, views
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from datetime import datetime
from ..models import course, student
from ..serializers.serializers import courseSerializer, studentSerializer


class courseStudent(generics.ListAPIView):
    queryset = course.objects.filter(cancelled=1)
    serializer_class = courseSerializer
    permission_classes = [permissions.IsAuthenticated]


# class CustomPostView(views.APIView):
#     serializer_class = CustomPostSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, *args, **kwargs):
#         serializer = CustomPostSerializer(data=request.data)
#         if serializer.is_valid():
#             print(serializer.data)
#             data = serializer.data
#             year = data['year']
#             objCourse = []
#             courses = course.objects.filter(cancelled=1)
#             for rs in courses:
#                 j = {'course_code': rs.course_code}
#                 objCourse.append(j)
#             # Perform additional processing if needed
#             # serializer.save()
#             return Response(objCourse)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class studentReport(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, date, *args, **kwargs):
        # Return raw data in JSON format
        objCourse = []
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return Response(
                {'msg': "Invalid date format. It must be in YYYY-MM-DD format."})
        courses = course.objects.filter(cancelled=1, active=1)
        for rs in courses:
            course_id = rs.course_id
            r = student.objects.select_related("register").filter(
                register__ev__course__course_id=course_id, crt_date__date=date)
            serializer = studentSerializer(r, many=True)
            j = {'course_id': rs.course_id, 'course_code': rs.course_code, 'course_name_th': rs.course_name, 'course_name_eng': rs.course_name_eng, 'crt_date': rs.crt_date,
                 'upd_date': rs.upd_date, 'data': serializer.data}
            objCourse.append(j)
        return Response(objCourse)
