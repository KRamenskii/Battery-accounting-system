from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import render
from .models import BatteryType
from .forms import BatteryTypeForm

def battery_types_view(request):
    battery_types = BatteryType.objects.all()
    return render(request, 'battery_types/battery_types.html', {'battery_types': battery_types})

class BatteryTypeCreateView(CreateView):
    model = BatteryType
    form_class = BatteryTypeForm
    template_name = 'battery_types/battery_type_create.html'
    success_url = reverse_lazy('battery_types')