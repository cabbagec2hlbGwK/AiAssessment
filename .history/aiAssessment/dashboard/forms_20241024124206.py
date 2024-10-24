from django import forms

class ReportForm(forms.Form):

    username = forms.CharField(
        required=True,
        max_length=150,  # Adjust the max length as needed
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Username', 
            'class': 'block w-full px-4 py-2 mt-2 text-gray-700 bg-white border border-gray-300 rounded-md focus:border-green-500 focus:ring-green-500 focus:ring-opacity-50 focus:outline-none'
        }),
        label='Username',
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'placeholder': 'Enter Email', 
            'class': 'block w-full px-4 py-2 mt-2 text-gray-700 bg-white border border-gray-300 rounded-md focus:border-green-500 focus:ring-green-500 focus:ring-opacity-50 focus:outline-none'
        }),
        label='Email',
    )

    website_url = forms.URLField(
        required=True,
        widget=forms.URLInput(attrs={
            'placeholder': 'Enter Website URL', 
            'class': 'block w-full px-4 py-2 mt-2 text-gray-700 bg-white border border-gray-300 rounded-md focus:border-green-500 focus:ring-green-500 focus:ring-opacity-50 focus:outline-none'
        }),
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
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-2 mt-2 bg-white border border-gray-300 rounded-md focus:border-green-500 focus:ring-green-500 focus:ring-opacity-50 focus:outline-none'
        }),
    )

    def clean_report_type(self):
        report_type = self.cleaned_data['report_type']
        # Convert the report type to an integer
        return int(report_type)  # Return 0 or 1
