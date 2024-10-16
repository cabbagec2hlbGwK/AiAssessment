from django.http import JsonResponse
from django.shortcuts import render
import json
import os

from .forms import ReportForm

def dashboard_view(request):
    form = ReportForm()

    if request.method == 'POST':
        form = ReportForm(request.POST)

        if form.is_valid():
            # Extract form data
            email = form.cleaned_data['email']
            website_url = form.cleaned_data['website_url']
            report_type = form.cleaned_data['report_type']
            
            # Generate the report using the JSON file
            report_data = generate_report(email, website_url, report_type)
            
            # Ensure the data is serializable
            response_data = {
                'status': 'success',
                'report': report_data  # This should be a dictionary
            }

            return JsonResponse(response_data)

        else:
            # If form is invalid, return the errors
            errors = form.errors.as_json()
            return JsonResponse({
                'status': 'error',
                'message': 'Form validation failed',
                'errors': json.loads(errors),  # Convert the form errors to a JSON object
            })

    # Render the form for GET requests
    return render(request, 'dashboard/dashboard.html', {'form': form})

def generate_report(email, website_url, report_type):
    # Define the path to the JSON file
    json_file_path = os.path.join(os.path.dirname(__file__), 'data', 'sample.json')

    # Read the JSON file
    try:
        with open(json_file_path, 'r') as file:
            report_template = json.load(file)  # Load the JSON data
            print("report_template", report_template)
    except FileNotFoundError:
        return {'status': 'error', 'message': 'JSON file not found'}
    except json.JSONDecodeError:
        return {'status': 'error', 'message': 'Error decoding JSON'}

    # Modify the template with form data
    report = {
        'email': email,
        'website_url': website_url,
        'report_type': report_type,
        'report_content': f"Generating {report_type} report for {email} and {website_url}.",
        'report_template': report_template,  
    }

    return report
