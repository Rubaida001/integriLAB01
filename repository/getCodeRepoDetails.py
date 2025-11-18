from datetime import datetime
import requests
from github import Github
from github import Auth
from github import Github


def get_code_repo_details(username, token,repo_name):     # using an access token
    try:
        auth = Auth.Token(token)

        list_details = []
        g = Github(auth=auth)
        repo = g.get_repo("{}/{}".format(username, repo_name))
        print(repo.name)
        branches = repo.get_branches()
        for branch in branches:
            print('branch: ', branch)
            for commit in repo.get_commits(branch.name):
                code_repo_details = {}
                code_repo_details['author'] = commit.commit.author.name
                code_repo_details['last_commit_date'] = commit.commit.author.date.strftime("%Y-%m-%d %H:%M:%S")
                code_repo_details['commit_message'] = commit.commit.message
                # print(code_repo_details['last_commit_date'], commit.commit.message,  commit.commit.sha)
                code_repo_details['commit_sha'] = commit.commit.sha
                code_repo_details['url'] = commit.commit.html_url
                # print('code_repo_details', code_repo_details)
                list_details.append(code_repo_details)
            # print('list_details: ', list_details)
        most_recent = {}
        for entry in list_details:
            event_datetime = datetime.strptime(entry['last_commit_date'], "%Y-%m-%d %H:%M:%S")
            event_date = event_datetime.date()
            if event_date not in most_recent or event_datetime > most_recent[event_date]['datetime']:
                most_recent[event_date] = {'entry': entry, 'datetime': event_datetime}
        result = [item['entry'] for item in most_recent.values()]
        # print('result', result)
        return result
    except Exception as e:
        print(f"Error retrieving repository details: {e}")
        return ['Error retrieving commit history. Check repository details.']
    finally:
        g.close()
        print("GitHub connection closed.")



def check_code_repo_connection(username, token):
    url = "https://api.github.com/user"  # Endpoint to fetch user details
    headers = {
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers)
    return response.status_code

