#!/usr/bin/python
import time
import requests
# disable urllib cert warning message
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

base_url = morpheus['morpheus']['applianceUrl']+'/api'
auth_key = morpheus['morpheus']['apiAccessToken']
# name of the instance to run the task on
instance_name = 'SERVER1'
# name of the task to run
task_name = 'Task 1'
# dict which will be converted to json and POSTed when executing the task, this allows properties set in the workflow
# to be passed through to the task by using the "morpheus" variable.
task_json = {
    'job': {
        'targetType': 'instance',
        'instances': None,
        'customOptions': {
            'OptionOne': morpheus['customOptions']['OptionOne'],
            'OptionTwo': morpheus['customOptions']['OptionTwo']
        } 
    }
}

session = requests.Session()
session.verify = False
session.headers.update({'Authorization': 'BEARER '+auth_key})

def get_instance_id(session, name):
    """Get the instance ID using the name. """
    payload = {'name': name}
    response = session.get(base_url+'/instances', params=payload)

    if not response.ok:
        raise requests.HTTPError('Status Code: {} Body: {}'.format(response.status_code, response.json()))

    if response.json()['meta']['size'] == 0:
        raise RuntimeError('No instances found with the name {}.'.format(name))

    # this assumes there is only one instance returned, may not be true with mutliple "Clouds" in play
    return response.json()['instances'][0]['id']

def get_task_id(session, name):
    """Get the task ID using the name."""
    payload = {'name': name}
    response = session.get(base_url+'/tasks', params=payload)

    if not response.ok:
        raise requests.HTTPError('Status Code: {} Body: {}'.format(response.status_code, response.json()))

    if response.json()['meta']['size'] == 0:
        raise RuntimeError('No task found with the name {}.'.format(name))

    return response.json()['tasks'][0]['id']

def get_job_execution(session, id):
    """Execute the task using the ID."""
    response = session.get('{}/job-executions/{}'.format(base_url, id))

    if not response.ok:
        raise requests.HTTPError('Status Code: {} Body: {}'.format(response.status_code, response.json()))

    return response

# run the task against the chosen instance
instance_id = get_instance_id(session, instance_name)
task_id = get_task_id(session, task_name)
task_json['job']['instances'] = [instance_id]
task_url = '{}/tasks/{}/execute'.format(base_url, task_id)
task_response = session.post(task_url, json=task_json)

if not task_response.ok:
    raise requests.HTTPError('Status Code: {} Body: {}'.format(task_response.status_code, task_response.json()))

# the task response contains the job created to execute the task
job_id = task_response.json()['job']['id']
job_response = None

# poll the status of the job until it completes with a success or error status
timeout = 120
start = time.time()
while time.time() < start + timeout:
    job_response = get_job_execution(session, job_id)

    if job_response.json()['jobExecution']['status'] == 'success':
        break
    if job_response.json()['jobExecution']['status'] == 'error':
        raise RuntimeError('Task execution failed. {}'.format(job_response.json()['jobExecution']['resultData']))

    time.sleep(10) 
else:
    raise RuntimeError('Timeout during execution of task "{}".'.format(job_response.json()['jobExecution']['name']))

print('Task: {} Result: {}'.format(
    job_response.json()['jobExecution']['name'], job_response.json()['jobExecution']['resultData'])
)
