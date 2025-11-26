from django.views.generic import CreateView
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from .models import ErrorReport
from .forms import ErrorReportForm

@login_required
def personal_account(request):
    user = request.user
    error_reports = ErrorReport.objects.filter(user=user)
    error_form = ErrorReportForm()
    return render(request, 'accounts/personal_account.html', {'user': user, 'errors': error_reports, 'form': error_form})

def error_reports(request):
    user = request.user
    error_reports = ErrorReport.objects.filter(user=user)
    return render(request, 'accounts/error_reports.html', {'user': user, 'errors': error_reports})

class ErrorReportCreateView(CreateView):
    model = ErrorReport
    form_class = ErrorReportForm
    template_name = 'accounts/add_error_report.html'
    success_url = reverse_lazy('personal_account')

    def form_valid(self, form):
        # Устанавливаем пользователя перед сохранением
        form.instance.user = self.request.user
        
        # Устанавливаем статус "Новая"
        try:
            from .models import ErrorStatus
            form.instance.status = ErrorStatus.objects.get(name="Новая")
        except ErrorStatus.DoesNotExist:
            form.instance.status = ErrorStatus.objects.first()
            
        return super().form_valid(form)

import logging
logger = logging.getLogger(__name__)

@require_POST
@login_required
def delete_error_report(request, error_id):
    try:
        # Находим ошибку текущего пользователя
        error_report = ErrorReport.objects.get(id=error_id, user=request.user)
        error_report.delete()
        return JsonResponse({'success': True})
    except ErrorReport.DoesNotExist:
        return JsonResponse({'error': 'Error report not found'}, status=404)