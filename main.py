import os
import json
import requests
import gitlab  # Import the GitLab library
from slack_sdk import WebClient  # Import the Slack library

def create_gitlab_branch(request):
    # Verify the request is from Slack (optional but recommended)
    slack_token = os.environ.get("SLACK_VERIFICATION_TOKEN")
    if request.args.get("token") != slack_token:
        return "Unauthorized", 401

    # Parse the Slack command
    text = request.args.get("text")
    parts = text.split()
    if len(parts) != 2:
        return "Invalid command format. Usage: /createbranch branch_name project_id", 200

    branch_name, project_id = parts

    # Replace with your GitLab API URL and access token
    gitlab_url = "https://gitlab.com/api/v4"
    gitlab_token = os.environ.get("GITLAB_API_TOKEN")

    # Create the branch in GitLab
    gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
    project = gl.projects.get(project_id)
    branch = project.branches.create({'branch_name': branch_name, 'ref': 'master'})

    if branch:
        # Branch creation is expected to trigger a pipeline automatically.
        # You can optionally add logic to wait for the pipeline to complete.

        # Create interactive message with buttons for pipeline jobs
        pipeline_jobs = get_pipeline_jobs(project_id, gitlab_url, gitlab_token)
        if pipeline_jobs:
            message = create_job_buttons_message(pipeline_jobs)
            return json.dumps(message), 200
        else:
            return "Pipeline jobs not found", 200
    else:
        return f"Error creating branch in GitLab", 200

def get_pipeline_jobs(project_id, gitlab_url, gitlab_token):
    # Retrieve information about the most recent pipeline for the project
    gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
    project = gl.projects.get(project_id)
    pipelines = project.pipelines.list()
    
    if pipelines:
        # Get the most recent pipeline
        pipeline = pipelines[0]
        
        # Retrieve information about jobs in the pipeline
        jobs = pipeline.jobs.list()
        return jobs
    
    return None

def create_job_buttons_message(pipeline_jobs):
    # Create interactive message with buttons for pipeline jobs
    message = {
        "text": "Pipeline has been triggered. Click a button to view job details:",
        "attachments": [
            {
                "fallback": "You are unable to choose a job",
                "callback_id": "job_actions",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": []
            }
        ]
    }

    # Add buttons for each job in the pipeline
    for job in pipeline_jobs:
        action = {
            "name": job.name,
            "text": job.name,
            "type": "button",
            "value": str(job.id)
        }
        message["attachments"][0]["actions"].append(action)

    return message
