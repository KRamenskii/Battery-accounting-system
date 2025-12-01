from django.views.generic import CreateView
from django.views.decorators.http import require_POST, require_http_methods
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ErrorReport, ErrorType, ErrorStatus
from .forms import ErrorReportForm


# Для сериализации ссылок
def serialize_error_report(er):
    return {
        "id": er.id,
        "error_type": {"id": er.error_type.id, "name": str(er.error_type)} if er.error_type else None,
        "description": er.description,
        "feedback": er.feedback,
        "status": {"id": er.status.id, "name": str(er.status)} if er.status else None,
        "user_id": er.user.id,
    }

@login_required
def get_error_report(request, error_id):
    """
    Возвращает JSON с данными обращения и флагом is_superuser
    """
    er = get_object_or_404(ErrorReport, id=error_id)

    # доступ: админ может просматривать все, обычный — только свои
    if not request.user.is_superuser and er.user != request.user:
        return JsonResponse({'message': 'Доступ запрещён'}, status=403)

    data = serialize_error_report(er)
    data['is_superuser'] = request.user.is_superuser
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def update_error_report(request, error_id):
    """
    Обработчик обновления обращения.
    - Обычный пользователь: может изменить только error_type и description (и только если он — владелец)
    - Админ: может изменить статус и feedback; видит тему/описание, но не может их менять
    Возвращает JSON (успех/ошибки)
    """
    er = get_object_or_404(ErrorReport, id=error_id)

    # Проверка прав просмотра/редактирования
    if not request.user.is_superuser and er.user != request.user:
        return JsonResponse({'message': 'Доступ запрещён'}, status=403)

    # Получим данные из POST (FormData)
    error_type_id = request.POST.get('error_type')
    description = request.POST.get('description')
    status_id = request.POST.get('status')
    feedback = request.POST.get('feedback')

    errors = {}

    # Обычный пользователь: может менять только type и description
    if not request.user.is_superuser:
        # проверим, что он владелец (проверка выше)
        # валидируем поля
        if not error_type_id:
            errors['error_type'] = ['Выберите тему обращения']
        if not description or description.strip() == '':
            errors['description'] = ['Описание не может быть пустым']

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        # применяем изменения
        try:
            from .models import ErrorType
            et = ErrorType.objects.get(id=error_type_id)
            er.error_type = et
        except ErrorType.DoesNotExist:
            errors['error_type'] = ['Выбран неверный тип']
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        er.description = description
        er.save()
        return JsonResponse({'success': True, 'message': 'Обращение обновлено'})

    # Админ: меняет только статус и feedback
    else:
        if status_id:
            try:
                from .models import ErrorStatus
                st = ErrorStatus.objects.get(id=status_id)
                er.status = st
            except ErrorStatus.DoesNotExist:
                errors['status'] = ['Выбран неверный статус']

        er.feedback = feedback if feedback is not None else er.feedback

        if errors:
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        er.save()
        return JsonResponse({'success': True, 'message': 'Обращение обновлено администратором'})

@login_required
def personal_account(request):
    user = request.user
    error_reports = ErrorReport.objects.filter(user=user)
    error_form = ErrorReportForm()
    return render(request, 'accounts/personal_account.html', {'user': user, 'errors': error_reports, 'form': error_form})

def error_reports(request):
    user = request.user

    if user.is_superuser:
        # Администратор видит все обращения
        error_reports = ErrorReport.objects.all()
    else:
        # Обычный пользователь видит только свои
        error_reports = ErrorReport.objects.filter(user=user)

    return render(request, 'accounts/error_reports.html', {
        'user': user,
        'errors': error_reports,
        'error_types': ErrorType.objects.all(),
        'statuses': ErrorStatus.objects.all()
    })

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
        if request.user.is_superuser:
            # Суперпользователь — может удалить любую запись
            error_report = ErrorReport.objects.get(id=error_id)
        else:
            # Обычный пользователь — только свои записи
            error_report = ErrorReport.objects.get(id=error_id, user=request.user)

        error_report.delete()
        return JsonResponse({'success': True})

    except ErrorReport.DoesNotExist:
        return JsonResponse({'error': 'Error report not found'}, status=404)