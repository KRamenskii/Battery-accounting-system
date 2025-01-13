from django.shortcuts import render

def battery_types(request):
    return render(request, 'battery_types/battery_types.html')