from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def personal_account(request):
    return render(request, 'accounts/personal_account.html')