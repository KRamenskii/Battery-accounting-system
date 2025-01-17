from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render
from .models import BatteryType
from .forms import BatteryTypeForm

def battery_types_view(request):
    battery_types = BatteryType.objects.all()
    return render(request, 'battery_types/battery_types.html', {'battery_types': battery_types})

def battery_type_detail(request, pk):
    battery_type = get_object_or_404(BatteryType, pk=pk)
    fields = [
        (field.verbose_name, getattr(battery_type, field.name))
        for field in BatteryType._meta.get_fields()
        if field.concrete and not field.many_to_many and not field.one_to_many
    ]
    return render(request, 'battery_types/battery_type_detail.html', {
        'fields': fields,
        'battery_type': battery_type
    })

class BatteryTypeCreateView(CreateView):
    model = BatteryType
    form_class = BatteryTypeForm
    template_name = 'battery_types/battery_type_create.html'
    success_url = reverse_lazy('battery_types')

class BatteryTypeUpdateView(UpdateView):
    model = BatteryType
    form_class = BatteryTypeForm
    template_name = 'battery_types/battery_type_edit.html'
    success_url = reverse_lazy('battery_types')
    context_object_name = 'battery_type_edit'

class BatteryTypeDeleteView(DeleteView):
    model = BatteryType
    template_name = 'battery_types/battery_type_confirm_delete.html'
    success_url = reverse_lazy('battery_types')
    context_object_name = 'battery_type_confirm_delete'