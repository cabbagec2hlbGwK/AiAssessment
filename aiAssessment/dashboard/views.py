from django.shortcuts import render
from django.http import JsonResponse
from .forms import ReportForm

def dashboard_view(request):
    form = ReportForm()

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            website_url = form.cleaned_data['website_url']
            report_type = form.cleaned_data['report_type']  # New field for report type
            report_data = generate_report(email, website_url, report_type)
            return JsonResponse({'status': 'success', 'report': report_data})

    return render(request, 'dashboard/dashboard.html', {'form': form})

def generate_report(email, website_url, report_type):
    # Simulate report generation based on the entered data
    report = {
        'email': email,
        'website_url': website_url,
        'report_type': report_type,
        'report_content': f"Generating {report_type} report for {email} and {website_url}.",
    }
    return report
