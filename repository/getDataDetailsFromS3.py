from datetime import datetime

from Notebook import settings


def extract_git_log_from_s3(s3_client, git_log_path):
    try:
        git_log_obj = s3_client.get_object()
        git_log_data = git_log_obj["Body"].read().decode("utf-8")

        commit_history = []

        for line in git_log_data.split("\n"):
            if line.strip():
                parts = line.split(" ")
                print('line', parts)
                commit_hash = parts[1]
                author = " ".join(parts[2:3])
                timestamp = int(parts[4])
                date = datetime.utcfromtimestamp(timestamp)
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")
                print('date', date, date_str)
                message = " ".join(parts[6:])

                commit_history.append({
                    "hash": commit_hash,
                    "author": author,
                    "date": date,
                    "message": message,
                })
        most_recent = {}
        for entry in commit_history:
            event_datetime = entry['date']
            event_date = event_datetime.date()
            if event_date not in most_recent or event_datetime > most_recent[event_date]['datetime']:
                most_recent[event_date] = {'entry': entry, 'datetime': event_datetime}

        # Collect the most recent commits for each date
        result = [item['entry'] for item in most_recent.values()]
        print('result',result)

        return result #commit_history

    except Exception as e:
        print(f"Error fetching git log from S3: {e}")
        return []


def delete_folder_from_s3(s3_client, folder_name):
    try:
        # Get list of objects in folder
        objects_to_delete = s3_client.list_objects_v2(Bucket, Prefix)

        if "Contents" in objects_to_delete:
            for obj in objects_to_delete["Contents"]:
                s3_client.delete_object(Bucket, Key=obj["Key"])


    except Exception as e:
        print(f"Error deleting folder from S3: {e}")