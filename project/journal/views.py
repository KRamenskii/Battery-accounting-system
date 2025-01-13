from django.shortcuts import render

def journal_home(request):
    return render(request, 'journal/journal.html')