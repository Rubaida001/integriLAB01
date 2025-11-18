from labtrace.client import Client
import os

#Install pipeline
# Go inside the folder where setup.py exists
#pip install .


## LOGIN
username = ""
password = ""
labtrace_client = Client(username, password)
my_user_id = labtrace_client.get_user_id()
print(labtrace_client.get_projects(leader=my_user_id))


'''
# VERIFY FILE CONTENT
file_path = ''
with open(file_path, "rb") as file:
        file_content = file.read()

file_name = os.path.basename(file_path)
print('Checking ', file_name, ' ...')
response = labtrace_client.verify_file_content(content=file_content, name=file_name)
print('main response', response)


def upload_file(file_path, file_info):
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
            return

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

        except Exception as e:
            project = labtrace_client.get_private_project_files(project_id)
            project_files = project['records']
            for file in project_files:
                if file['name'] == file_name:
                    print(f"Successfully Uploaded file '{file_name}'")
                    break
            else:
                if isinstance(e, Exception) and 'status: 503' in str(e):
                        print(f"Successfully Uploaded file '{file_name}'")
                else:
                    print('Other error')
                    print(e)


    else:
        print('File ', file['name'] + ' already present')


with open('filesList.json', 'r') as json_file:
    data = json.load(json_file)
for key, file_info in data.items():
    file_path = os.path.join(file_info['path'], file_info['fileName']) 
    upload_file(file_path, file_info )
'''

