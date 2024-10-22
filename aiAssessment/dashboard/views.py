from django.http import JsonResponse
from django.shortcuts import render
from .forms import ReportForm
from .models import Report

def dashboard_view(request):
    form = ReportForm()

    if request.method == 'POST':
        form = ReportForm(request.POST)

        if form.is_valid():
            # Extract form data
            email = form.cleaned_data['email']
            website_url = form.cleaned_data['website_url']
            report_type = form.cleaned_data['report_type']
            
            # Create a report instance
            report_content = f"Generating {report_type} report for {email} and {website_url}."
            report = Report.objects.create(
                email=email,
                website_url=website_url,
                report_type=report_type,
                report_content=report_content
            )
            report_data = {
                'id': report.id,
                'email': report.email,
                'website_url': report.website_url,
                'report_type': report.report_type,
                'report_content': report.report_content,
            }

            # Ensure the data is serializable
            response_data = {
                'status': 'success',
                'report': report_data  
            }

            return JsonResponse(response_data)

        else:
            # If form is invalid, return the errors
            errors = form.errors.as_json()
            return JsonResponse({
                'status': 'error',
                'message': 'Form validation failed',
                'errors': json.loads(errors),  
            })

    # Render the form for GET requests
    return render(request, 'dashboard/dashboard.html', {'form': form})
