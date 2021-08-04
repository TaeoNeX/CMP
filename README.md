# Cloud Management Portal

## run_task_on_instance.py
In a CMP a workflow (and the tasks in it) can only be targeted against one instance/server. This script can be added into a workflow and will run a chosen task against another instance that is defined in the script.

For example, during a server build workflow the script could run a task against a domain controller to make changes in Active Directory.
