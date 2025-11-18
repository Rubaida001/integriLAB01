import git, os
import tempfile
import shutil
from datetime import datetime
from zipfile import ZipFile


def get_commit_history(repo_path):
    """Function to print commit history from the specified Git repository path."""
    try:
        repo = git.Repo(repo_path)
        commits = list(repo.iter_commits('HEAD'))
        commit_details_list = []

        for commit in commits:
            commit_details = {}
            commit_details['commit_time'] = datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d')
            commit_details['author_name'] = commit.author.name
            commit_details['author_email'] = commit.author.email
            commit_details['message'] = commit.message.strip()
            commit_details['hash'] = commit.hexsha
            commit_details_list.append(commit_details)

    except Exception as e:
        print(f"Error reading commit history: {e}")
        commit_details_list = ['Error retrieving commit history.']
    return commit_details_list


def clone_and_get_history(overleaf_repo_url):
    """Clone the Overleaf project to a temporary directory, get commit history, and clean up."""
    temp_dir = "/tmp/overleaf_repo"
    commit_details_list = []

    # Ensure the directory exists
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    print(f"Cloning repository into temporary directory: {temp_dir}")

    try:
        print('overleaf_repo_url',overleaf_repo_url)
        # Clone the repository using the token
        git.Repo.clone_from(overleaf_repo_url, temp_dir)
        print("Repository cloned successfully!")

        # Get the commit history
        commit_details_list = get_commit_history(temp_dir)
        # get_old_doc_version(temp_dir)

    except Exception as e:
        print(f"Error during cloning or commit history retrieval: {e}")
        commit_details_list = ['Error retrieving commit history. Check repository details.']

    finally:
        # Clean up: Delete the temporary directory
        print(f"Deleting temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir,ignore_errors=True)
        print("Temporary directory deleted.")
    return commit_details_list


#if __name__ == "__main__":
def get_doc_repo_details(email, git_token, git_link, full_name):
    # Token and Overleaf Git repository details
    TOKEN = git_token 
    OVERLEAF_PROJECT_ID = git_link.split('/')[-1] 
    OVERLEAF_REPO_URL = f"git:{TOKEN}@git.overleaf.com/{OVERLEAF_PROJECT_ID}"

    commit_details_list = clone_and_get_history(OVERLEAF_REPO_URL)
    print('commit_details_list', commit_details_list)
    return commit_details_list



def clone_repo(git_link, git_token):
    TOKEN = git_token 
    OVERLEAF_PROJECT_ID = git_link.split('/')[-1] 
    overleaf_repo_url = f"git:{TOKEN}@git.overleaf.com/{OVERLEAF_PROJECT_ID}"

    TMP_DIR = tempfile.mkdtemp()
    repo_path = os.path.join(TMP_DIR,'overleaf_project') 

    """Clone the Overleaf Git repository if it doesn't exist."""
    if not os.path.exists(repo_path):
        git.Repo.clone_from(overleaf_repo_url, repo_path)
    return repo_path



def checkout_commit_and_zip(repo_path, commit_hash):
    """Checkout a specific commit and create a zip archive of the project."""
    repo = git.Repo(repo_path)
    repo.git.checkout(commit_hash)

    # Create a zip archive of the repository
    zip_path = os.path.join(os.path.dirname(repo_path), f"overleaf_{commit_hash}.zip")
    with ZipFile(zip_path, 'w') as zipf:
        for root, _, files in os.walk(repo_path):
            for file in files:
                print('file', file)
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, repo_path)
                zipf.write(full_path, arcname)

    # Reset to the main branch after creating the zip
    try:
        repo.git.checkout("main")
    except:
        repo.git.checkout("master")
    return zip_path


def cleanup_temp_files(repo_path):
    """Remove the temporary directory."""
    if os.path.exists(repo_path):
        print('Removing temporary directory', repo_path)
        shutil.rmtree(repo_path)

