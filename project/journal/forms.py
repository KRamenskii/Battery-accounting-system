from django import forms
from .models import InstallationLocation, TestingDBT12D, TestingIC105, Battery, BatteryInstallationHistory, SerialParameters

class InstallationLocationForm(forms.ModelForm):
    class Meta:
        model = InstallationLocation
        fields = ['location_title', 'location_type', 'system_title', 'system_name', 'nominal_capacity', 'battery_count', 'parent_location', 'nesting_level']

    def __init__(self, *args, **kwargs):
        parent_location = kwargs.pop('parent_location', None)
        super().__init__(*args, **kwargs)
        if parent_location:
            self.fields['parent_location'].initial = parent_location
            self.fields['nesting_level'].initial = parent_location.nesting_level + 1


class TestingDBT12DForm(forms.ModelForm):
    class Meta:
        model = TestingDBT12D
        fields = ['battery', 'testing_date', 'SOH', 'SOC', 'VOL', 'R', 'STD', 'CCA']


class TestingIC105Form(forms.ModelForm):
    class Meta:
        model = TestingIC105
        fields = ['battery', 'testing_date', 'SOH', 'VOL', 'R', 'STD', 'CCA']


class BatteryForm(forms.ModelForm):
    installation_location = forms.ModelChoiceField(
        queryset=InstallationLocation.objects.all(),
        required=True,
        label="Место установки"
    )
    installation_date = forms.DateField(
        required=True,
        label="Дата установки",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    class Meta:
        model = Battery
        fields = ['battery_type', 'serial_parameters', 'battery_number', 'acceptance_date', 'installation_location']

    def save(self, commit=True):
        battery = super().save(commit=False)
        if commit:
            battery.save()
            # Создаём запись в истории установки
            BatteryInstallationHistory.objects.create(
                battery=battery,
                installation_location=self.cleaned_data['installation_location'],
                installation_date=self.cleaned_data['installation_date'],
            )
        return battery


class BatteryUpdateForm(forms.ModelForm):

    class Meta:
        model = Battery
        fields = [
            'battery_type',
            'serial_parameters',
            'battery_number',
            'acceptance_date',
        ]


class BatteryInstallationHistoryForm(forms.ModelForm):
    class Meta:
        model = BatteryInstallationHistory
        fields = ['installation_location', 'installation_date']  # Убираем 'battery'
        widgets = {
            'installation_date': forms.DateInput(attrs={
                'type': 'date',
            })
        }

    def __init__(self, *args, **kwargs):
        # Получаем аккумулятор из аргументов
        self.battery = kwargs.pop('battery', None)
        super().__init__(*args, **kwargs)

        # Устанавливаем поле battery в предустановленное значение
        if self.battery:
            self.instance.battery = self.battery

    def clean_installation_date(self):
        installation_date = self.cleaned_data.get('installation_date')
        # Добавьте здесь любую дополнительную валидацию для даты установки
        return installation_date


# Создаем кастомную форму для админки
class BatteryAdminForm(forms.ModelForm):
    class Meta:
        model = Battery
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Фильтруем серийные параметры по выбранному типу АКБ
        if 'battery_type' in self.data:
            try:
                battery_type_id = int(self.data.get('battery_type'))
                self.fields['serial_parameters'].queryset = SerialParameters.objects.filter(
                    battery_type_id=battery_type_id
                )
            except (ValueError, TypeError):
                self.fields['serial_parameters'].queryset = SerialParameters.objects.none()
        elif self.instance and self.instance.battery_type:
            self.fields['serial_parameters'].queryset = SerialParameters.objects.filter(
                battery_type=self.instance.battery_type
            )
        else:
            self.fields['serial_parameters'].queryset = SerialParameters.objects.none()