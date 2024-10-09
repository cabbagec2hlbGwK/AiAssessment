from django import forms

class ReportForm(forms.Form):
    # Required email field
    email = forms.EmailField(
        required=True,  # Email is required
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'}),
        label='Email',
    )

    # Required website URL field
    website_url = forms.URLField(
        required=True,  # Website URL is required
        widget=forms.URLInput(attrs={'placeholder': 'Enter Website URL'}),
        label='Website URL',
    )

    # Dropdown field for selecting report type (Basic or Detailed)
    REPORT_TYPE_CHOICES = [
        ('basic', 'Basic Report'),
        ('detailed', 'Detailed Report'),
    ]
    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        required=True,
        label='Select Report Type',
        widget=forms.Select(attrs={'class': 'report-type-dropdown'}),
    )
