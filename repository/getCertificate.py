from django.http import FileResponse

from Notebook.settings import base
from labTrace_sdk.labtrace.client import Client
import os, time
import tempfile
from datetime import datetime
from pathlib import Path


def create_file(content, filename):
    TMP_DIR = tempfile.mkdtemp()
    file_path = os.path.join(TMP_DIR, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(content)
    return file_path

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def upload_file(file_path, file_info, labtrace_client,project_id):
    with open(file_path, "rb") as file:
        file_content = file.read()

    file_name = os.path.basename(file_path)
    print('Uploading ', file_name, ' ...')

    project = labtrace_client.get_private_project_files(project_id)
    project_files = project['records']
    if file_info['fileType'] == 'secondary':

        matching_primary_file = None
        matching_link_to_procedure = None
        timeout = time.time() + 10  # Set timeout for 10 seconds

        while time.time() < timeout:

            matching_primary_file = next((file for file in project_files if file['name'] == file_info['primaryData'] and file['status'] == 'Available'), None)
            matching_link_to_procedure = next((file for file in project_files if file['name'] == file_info['linkToProcedure'] and file['status'] == 'Available'), None)

            if matching_primary_file and matching_link_to_procedure:
                break  # Both files found, exit the loop

            time.sleep(1)  # Wait for 1 second before retrying

        if not matching_primary_file or not matching_link_to_procedure:
            print("Timed out waiting for files.")
            return "Timed out waiting for files."

        file_info['primaryData'] = matching_primary_file['id']
        file_info['linkToProcedure'] = matching_link_to_procedure['id']

    file_already_present = False
    for file in project_files:
        if file['name'] == file_name and file['status'] == 'Available' :
            file_already_present = True
            break

    if not file_already_present:
        try:
            upload_result = labtrace_client.upload_private_file(
                project_id=project_id,
                content=file_content,
                file_type=file_info['fileType'],
                name=file_name,
                label=file_info['label'],
                primary_data=file_info['primaryData'],
                link_to_procedure=file_info['linkToProcedure'],
                procedure_description=file_info['procedureDescription']
            )

            print(f"Successfully Uploaded file '{file_name}'")
            return f"Successfully Uploaded file '{file_name}'"

        except Exception as e:
            project = labtrace_client.get_private_project_files(project_id)
            project_files = project['records']
            for file in project_files:
                if file['name'] == file_name:
                    print(f"Successfully Uploaded file '{file_name}'")
                    break
                return f"Successfully Uploaded file '{file_name}'"
            else:
                if isinstance(e, Exception) and 'status: 503' in str(e):
                        print(f"Successfully Uploaded file '{file_name}'")
                        return f"Successfully Uploaded file '{file_name}'"
                else:
                    print('Other error')
                    print(e)
                    return 'Other error:'+e


    else:
        print('File ', file['name'] + ' already present')
        return 'File ', file['name'] + ' already present'


def getCertificate(username, password, project_id, data_hash,code_hash, doc_hash):
    labtrace_client = Client(username, password)
    print('labtrace_client', labtrace_client)
    my_user_id = labtrace_client.get_user_id()
    print(labtrace_client.get_projects(leader=my_user_id))
    global temp_file_path
    data = {}
    file_hash = ''
    # Define the specific name you want
    filename = 'integrilab-' + data_hash[:5] +'-'+ code_hash[:5] +'-'+ doc_hash[:5] + ".txt"
    temp_file_path = create_file(data_hash + code_hash + doc_hash, filename)
    file_extension = os.path.splitext(filename)[1]
    label = os.path.splitext(filename)[0]

    file_data = {
        "fileName": filename,
        "fileType": "primary",
        "primaryData": "",
        "linkToProcedure": "",
        "procedureDescription": "",
        "label": label,
        "path": os.path.dirname(temp_file_path)  # temp_dir
    }
    data[str(1)] = file_data
    #print(data)
    file_path = os.path.join(file_data['path'], file_data['fileName'])
    print('file_path', file_path)
    upload_details = upload_file(file_path, file_data, labtrace_client, project_id)
    file_hash = ''
    if 'Successfully Uploaded file' or ' already present' in upload_details:
        records = labtrace_client.get_private_project_files(project_id)['records']
        for record in records:
            if record['name'] == filename:
                file_hash = record['id']
                print('fileHash', file_hash)
                break
    delete_file(temp_file_path)
    return file_hash



def check_block_repo_connection(username,password):
    try:
        client = Client(username, password)
        return 200
    except:
        return 401




