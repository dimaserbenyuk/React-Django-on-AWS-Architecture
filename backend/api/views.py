from rest_framework.views import APIView
from rest_framework.response import Response
from .tasks import generate_pdf

class GeneratePDFView(APIView):
    def post(self, request):
        # пока временно фиксированное значение для теста
        report_id = 1
        task = generate_pdf.delay(report_id)
        return Response({'task_id': task.id, 'status': 'started'})
