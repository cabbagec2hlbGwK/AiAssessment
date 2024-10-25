import os
from django.http import JsonResponse
from django.shortcuts import render
from django.db import connection
#from dashboard.agent_manager import AgentManager
from dashboard.agent_manager import AgentManager
from .forms import ReportForm


# The main view that handles the dashboard logic
def dashboard_view(request):
    form = ReportForm()

    if request.method == 'POST':
        form = ReportForm(request.POST) 
        secret_name = os.getenv("secret_name")
        rds_endpoint = os.getenv("rds_endpoint")
        region_name = os.getenv("AWS_DEFAULT_REGION")
        hostEndpoint = os.getenv("APIHOST")

        agent_manager = AgentManager(use_local=False, secret_name=secret_name, rds_endpoint=rds_endpoint, region_name=region_name)

        if form.is_valid():
            name = form.cleaned_data.get('username')
            email = form.cleaned_data['email']
            endpoint = form.cleaned_data['website_url']
            detailed_report = 1 if form.cleaned_data['report_type'] == 'detailed' else 0
            name = form.cleaned_data.get('username')  

            # Create a user based on the form input using raw SQL
            user_id =  agent_manager.insert_user(name=name, email=email, endpoint=endpoint, detailed_report=detailed_report)

            if user_id:
                print(f"Fetching user data for user_id: {user_id}")  # Debug log
                user_data = agent_manager.fetch_user(user_id)
                if user_data is not None:
                    response_data = {
                        'status': 'success',
                        'username': name,
                        'email': email,
                        'endpoint': endpoint,
                        'userData': user_data,  # This now includes parsed JSON
                    }
                else:
                    response_data = {
                        'status': 'error',
                        'message': "Failed to fetch user data."
                    }

            return JsonResponse(response_data)

    return render(request, 'dashboard/dashboard.html', {'form': form})


def report_view(request, userId):
    if request.method == 'GET':
        secret_name = os.getenv("secret_name")
        rds_endpoint = os.getenv("rds_endpoint")
        region_name = os.getenv("AWS_DEFAULT_REGION")
        agent_manager = AgentManager(use_local=False, secret_name=secret_name, rds_endpoint=rds_endpoint, region_name=region_name)
        if userId:
            userData = agent_manager.fetch_user(userId)
            data = userData.get("resultData")
            print(f"type: {data.get('project_info')['client_name']}")
            return render(request, 'result.html', data)
        return render(request, 'result.html',{})
