# retry_helper.py
from retry import retry
import requests

@retry(requests.ConnectionError, tries=5, delay=5, backoff=2)
def fetch_pipeline_jobs():
    # Your code to fetch pipeline jobs from GitLab
    response = requests.get('YOUR_GITLAB_API_ENDPOINT_FOR_PIPELINE_JOBS', headers={'Authorization': 'YOUR_TOKEN'})

    # Check if the response was successful
    response.raise_for_status()

    # If everything went well, return the response (or process it accordingly)
    return response.json()
