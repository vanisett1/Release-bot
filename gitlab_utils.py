import gitlab

def get_pipeline_jobs(project_id, gitlab_url, gitlab_token):
    try:
        gl = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
        project = gl.projects.get(project_id)
        pipelines = project.pipelines.list()
        
        if pipelines:
            pipeline = pipelines[0]
            jobs = pipeline.jobs.list()
            return jobs
    except Exception as e:
        print(f"Error retrieving pipeline jobs: {str(e)}")
    
    return None

def create_job_buttons_message(pipeline_jobs):
    """
    Create a Slack message with buttons for each pipeline job.
    :param pipeline_jobs: List of pipeline jobs.
    :return: Slack message structure.
    """
    # Define the base structure of the Slack message
    message = {
        "text": "Pipeline Jobs:",
        "attachments": []
    }

    # Add a button for each pipeline job
    for job in pipeline_jobs:
        attachment = {
            "text": job["name"],
            "callback_id": "job_button",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "view_job",
                    "text": "View Job",
                    "type": "button",
                    "url": job["web_url"]
                }
            ]
        }
        message["attachments"].append(attachment)

    return message
