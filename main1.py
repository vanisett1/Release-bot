import os
import json
import requests
import gitlab
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request, jsonify


app = Flask(__name__)

# Enable debug mode
app.debug = True

@app.route('/create-branch', methods=['POST'])


def create_gitlab_branch():
    # Verify the request is from Slack
    slack_verification_token = os.environ.get("SLACK_VERIFICATION_TOKEN")
    if request.form.get("token") != slack_verification_token:
        return jsonify({"error": "Unauthorized"}), 401

    # Parse the Slack command
    text = request.form.get("text")
    parts = text.split()
    
    if len(parts) != 2:
        return jsonify({"error": "Invalid command format. Usage: /createbranch branch_name project_id"}), 200

    branch_name, project_id = parts
    print(branch_name, project_id)
    # Replace with your GitLab API URL and access token
    gitlab_url = "https://gitlab.com/api/v4"
    gitlab_token = os.environ.get("GITLAB_API_TOKEN")

    # Create the branch in GitLab
    try:
        gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        print("Gitlab API request: GET", gitlab_url)

        print(f"Attempting to fetch project with ID: {project_id}")
        try:
            project = gl.projects.get(project_id)
            print("GitLab API request: GET projects/{project_id}")
            print(f"Fetched project name: {project.name}")
        except gitlab.exceptions.GitlabAuthenticationError as auth_error:
            print(f"GitLab authentication error: {auth_error}")
        except gitlab.exceptions.GitlabGetError as get_error:
            print(f"GitLab get error: {get_error}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")

        project = gl.projects.get(project_id)
        print("GitLab API request: GET projects/{project_id}")
        
        # Fetch the default branch name from GitLab
        project_info = project.info()
        default_branch = project_info["default_branch"]
        
        # Create the branch using the default branch as the ref
        branch = project.branches.create({'branch_name': branch_name, 'ref': default_branch})

        if branch:
            # Branch creation is expected to trigger a pipeline automatically.
            # You can optionally add logic to wait for the pipeline to complete.

            # Create interactive message with buttons for pipeline jobs
            pipeline_jobs = get_pipeline_jobs(project_id, gitlab_url, gitlab_token)
            if pipeline_jobs:
                message = create_job_buttons_message(pipeline_jobs)
                return jsonify(message), 200
            else:
                return jsonify({"error": "Pipeline jobs not found"}), 200
        else:
            return jsonify({"error": "Error creating branch in GitLab"}), 200
    except gitlab.exceptions.GitlabAuthenticationError:
        return jsonify({"error": "GitLab authentication failed"}), 500
    except gitlab.exceptions.GitlabGetError:
        return jsonify({"error": "GitLab project not found"}), 404
    except gitlab.exceptions.GitlabCreateError:
        return jsonify({"error": "Error creating branch in GitLab"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# The rest of your code (get_pipeline_jobs and create_job_buttons_message) remains the same

if __name__ == '__main__':
    app.run()
