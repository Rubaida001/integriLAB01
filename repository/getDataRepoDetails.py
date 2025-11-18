import paramiko
from datetime import datetime
def get_data_repo_details(hostname, username, password, datapath):
    # Create an SSH client instance
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key if not already known
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    list_details = []
    try:
        # Connect to the remote server
        ssh.connect(hostname, port=22, username=username, password=password)

        # Run a command to get git log
        stdin, stdout, stderr = ssh.exec_command(
            'cd {};git log --pretty=format:"%H|%an|%s|%ad" --date=format:"%Y-%m-%d %H:%M:%S"'.format(datapath))
        commitHistory = stdout.readlines()

        # Collect commit details
        for commit in commitHistory:
            history_details = {
                'commitId': commit.split('|')[0],
                'commitAuthor': commit.split('|')[1],
                'commitMsg': commit.split('|')[2],
                'commitDate': commit.split('|')[3].strip('\n')
            }
            list_details.append(history_details)
            print(history_details)

        # Determine the most recent commit per day
        most_recent = {}
        for entry in list_details:
            event_datetime = datetime.strptime(entry['commitDate'], "%Y-%m-%d %H:%M:%S")
            event_date = event_datetime.date()
            if event_date not in most_recent or event_datetime > most_recent[event_date]['datetime']:
                most_recent[event_date] = {'entry': entry, 'datetime': event_datetime}

        # Collect the most recent commits for each date
        result = [item['entry'] for item in most_recent.values()]
        print(result)

        # Get any error message (if any)
        error = stderr.read().decode()
        if error:
            print(f"Error: {error}")

        return result

    finally:
        # Close the SSH connection
        ssh.close()