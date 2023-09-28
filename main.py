import os
import json
import requests
import gitlab
import time
from flask import Flask, request, jsonify
from gitlab_utils import get_pipeline_jobs  # Import the function

app = Flask(__name__)

# Enable debug mode
app.debug = True

MAX_RETRIES = 3
RETRY_DELAY = 10  # in seconds

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
        return jsonify({"error": "Invalid command format. Usage: /create-branch branch_name project_id"}), 400

    branch_name, project_id = parts

    # Replace with your GitLab API URL and access token
    gitlab_api_endpoint = "https://gitlab.com/api/v4/projects"
    gitlab_token = os.environ.get("GITLAB_API_TOKEN")

    # Set the source branch to either "main" or "master"
    source_branch = "main"  # You can change this to "master" if needed

    create_branch_url = f"{gitlab_api_endpoint}/{project_id}/repository/branches?branch={branch_name}&ref={source_branch}"

    for _ in range(MAX_RETRIES):
        try:
            headers = {"Private-Token": gitlab_token}
            response = requests.post(create_branch_url, headers=headers)

            if response.status_code == 201:
                # Branch creation is expected to trigger a pipeline automatically.
                pipeline_jobs = get_pipeline_jobs(project_id, gitlab_api_endpoint, gitlab_token)
                if pipeline_jobs:
                    message = create_job_buttons_message(pipeline_jobs)
                    return jsonify(message), 200
                else:
                    return jsonify({"error": "Pipeline jobs not found"}), 200
            else:
                return jsonify({"error": f"Error creating branch in GitLab: {response.text}"}), 500
        except requests.exceptions.RequestException as e:
            if _ < MAX_RETRIES - 1:  # i.e. if not on the last attempt
                time.sleep(RETRY_DELAY)
                continue  # retry
            else:
                return jsonify({"error": f"Request exception after {MAX_RETRIES} attempts: {str(e)}"}), 500
        break  # if successful, break out of the loop

    # The rest of your code (get_pipeline_jobs and create_job_buttons_message) remains the same

if __name__ == '__main__':
    app.run()
