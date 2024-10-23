from django import forms

class ReportForm(forms.Form):

    username = forms.CharField(
        required=True,
        max_length=150,  # You can adjust the max length as needed
        widget=forms.TextInput(attrs={'placeholder': 'Enter Username'}),
        label='Username',
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
        label='Email',
    )

    website_url = forms.URLField(
        required=True,
        widget=forms.URLInput(attrs={'placeholder': 'Enter Website URL'}),
        label='Website URL',
    )

    REPORT_TYPE_CHOICES = [
        ('0', 'Basic Report'),   # Map to 0
        ('1', 'Detailed Report'), # Map to 1
    ]
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        required=True,
        label='Select Report Type',
        widget=forms.Select(attrs={'class': 'report-type-dropdown'}),
    )

    def clean_report_type(self):
        report_type = self.cleaned_data['report_type']
        # Convert the report type to an integer
        return int(report_type)  # Return 0 or 1
