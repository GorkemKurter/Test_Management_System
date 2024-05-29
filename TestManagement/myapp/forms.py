from django import forms


class LoginForm(forms.Form):

    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class TestTypeForm(forms.Form):

    TEST_TYPES = [
        ('malzeme', 'Malzeme Testleri'),
        ('elektriksel', 'Elektriksel Güvenlik Testleri'),
    ]
    test_type = forms.ChoiceField(choices=TEST_TYPES, label='')


class TestFilterForm(forms.Form):

    requester = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    requested_date = forms.CharField(widget=forms.DateInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    test_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    component = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    brand = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    model = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    result = forms.ChoiceField(choices=[("", ""), ("Tamamlanmadı", "Tamamlanmadı"), ('OK', 'OK'), ('NOK', 'NOK')], required=False,widget=forms.Select(attrs={'class': 'form-control'}))
    explanation = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)



    def clean(self):
        cleaned_data = super().clean()
        fields = ['requester', 'requested_date', 'test_name', 'component', 'brand', 'model', 'result', 'explanation']

        if not any(cleaned_data.get(field) for field in fields):
            raise forms.ValidationError("En az bir alanın doldurulması gerekiyor.")

        return cleaned_data


class CreateTestRequest(forms.Form):

    komponent = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=True)
    marka = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=True)
    model = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=True)
    aciklama = forms.CharField(help_text="Lütfen komponentte veya makinede yapılan değişikliği ayrıntılarıyla açıklayınız.", widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=True)

class FilterTestRequestForm(forms.Form):

    komponent = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    marka = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    model = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    filtreleme_tarihi = forms.CharField(widget=forms.DateInput(attrs={'class': 'form-control'}), empty_value="", required=False)
    requester = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), empty_value="", required=False)
