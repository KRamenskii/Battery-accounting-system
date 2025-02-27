from django import forms
from .models import InstallationLocation, TestingDBT12D, TestingIC105

class InstallationLocationForm(forms.ModelForm):
    class Meta:
        model = InstallationLocation
        fields = ['location_title', 'system_title', 'parent_location', 'nesting_level']

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