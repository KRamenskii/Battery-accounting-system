from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ErrorReport
from .forms import ErrorReportForm

@login_required
def personal_account(request):
    user = request.user
    errorReports = ErrorReport.objects.filter(user=user)
    error_form = ErrorReportForm()
    return render(request, 'accounts/personal_account.html', {'user': user, 'errors': errorReports, 'form': error_form})

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