from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import ErrorReport

@login_required
def personal_account(request):
    user = request.user
    errorReports = ErrorReport
    return render(request, 'accounts/personal_account.html', {'user': user, 'errors': errorReports})