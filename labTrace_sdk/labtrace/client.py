import os
import re
import jwt
import requests
import json

from typing import Dict, List, Optional
from datetime import datetime

LABTRACE_URL = os.getenv('LABTRACE_URL', default='https://labtrace-php-backend-156e4f37e351.herokuapp.com')


class ResponseException(Exception):
    """
    Exception class raised on error responses status codes
    """

    def __init__(self, status_code: int, msg: str):
        super().__init__(f'status: {status_code}, msg: {msg}')
        self.status_code = status_code
        self.msg = msg


class Client(object):
    """
    Labtrace Client class
    """

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self._auth = self._login()
        self._user_id = jwt.decode(self._auth, options={"verify_signature": False})['id']

    def get_user_id(self):
        return self._user_id

    def _make_request(self,
                      url: str,
                      path: str,
                      method: str,
                      body: Optional[Dict] = None,
                      headers: Optional[Dict] = None,
                      auth: Optional[bool] = True,
                      content_type: str = 'application/json',
                      files: Optional[Dict] = None,
                      query_params: Optional[Dict] = None,
                      pdf_Download: Optional[bool] = False) -> requests.Response:

        """
        makes an http request.
        content type can be either application/json or multipart
        if auth is set to True, the authorization header is appended with the token
        stored in the client instance
        """
        body = body or {}
        req_params = query_params or {}
        req_headers = headers or {}
        if auth:
            req_headers['Authorization'] = f'Bearer {self._auth}'
        req = getattr(requests, method)
        if content_type == 'application/json':
            req_headers['Content-Type'] = content_type
            response = req(f'{url}/{path}', json=body, headers=req_headers, params=req_params)
        elif content_type == 'multipart':
            response = req(f'{url}/{path}', data=body, files=files, headers=req_headers, params=req_params)
        else:
            raise TypeError(f'Invalid Content type: {content_type}')
        if response.status_code > 299:
            if response.status_code == 401 and response.json()['message'] == 'Expired JWT Token':
                self._auth = self._login()
                return self._make_request(url,
                                          path,
                                          method,
                                          body,
                                          headers,
                                          auth,
                                          content_type,
                                          files,
                                          query_params)
            raise ResponseException(status_code=response.status_code, msg=response.content)

        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                response.json()
                return response
            except ValueError as e:
                print(f'Error decoding json: {e}')
        if pdf_Download:
            return response
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            json_content = json_match.group(0)
            response._content = json_content.encode()
        return response

    def _login(self) -> str:
        """
        performs the login and returns the jwt token
        """
        return self._make_request(
            url=LABTRACE_URL,
            path='login',
            method='post',
            body={'email': self.username,
                  'password': self.password},
            auth=False).json()['token']

    def _upload_file(self,
                     url: str,
                     path: str,
                     content: bytes,
                     file_type: str,
                     name: str,
                     label: str,
                     primary_data: Optional[str] = None,
                     link_to_procedure: Optional[str] = None,
                     procedure_description: Optional[str] = None) -> str:
        """
        uploads a file in a project public directory
        """
        body = {'type': file_type,
                'label': label,
                'uploaded': str(datetime.now())
                }
        if file_type == 'secondary':
            body['linkToProcedure'] = link_to_procedure
            body['procedureDescription'] = procedure_description
            body['primaryData'] = primary_data
        return self._make_request(
            url=url,
            path=path,
            method='post',
            body=body,
            files={'file': (name, content)},
            content_type='multipart').json()

    def upload_public_file(self,
                           project_id: str,
                           content: bytes,
                           file_type: str,
                           name: str,
                           label: Optional[str] = '',
                           primary_data: Optional[str] = None,
                           link_to_procedure: Optional[str] = None,
                           procedure_description: Optional[str] = None) -> str:
        """
        uploads a file in a project public directory
        """
        return self._upload_file(LABTRACE_URL,
                                 path=f'projects/{project_id}/files',
                                 content=content,
                                 file_type=file_type,
                                 name=name,
                                 label=label,
                                 primary_data=primary_data,
                                 link_to_procedure=link_to_procedure,
                                 procedure_description=procedure_description)

    def upload_private_file(self,
                            project_id: str,
                            content: bytes,
                            file_type: str,
                            name: str,
                            label: Optional[str] = '',
                            primary_data: Optional[str] = None,
                            link_to_procedure: Optional[str] = None,
                            procedure_description: Optional[str] = None) -> str:
        """
        uploads a file in a project private directory
        """
        return self._upload_file(LABTRACE_URL,
                                 path=f'private-files/project/{project_id}',
                                 content=content,
                                 file_type=file_type,
                                 name=name,
                                 label=label,
                                 primary_data=primary_data,
                                 link_to_procedure=link_to_procedure,
                                 procedure_description=procedure_description)

    def verify_file_content(self,
                            content: bytes,
                            name: str) -> str:
        """
        uploads a file in a project public directory
        """

        return self._upload_file(LABTRACE_URL,
                                 path=f'projects/files/verify',
                                 content=content,
                                 file_type='file_type',
                                 name=name,
                                 label='label')

    def get_projects(self,
                     project_name: Optional[str] = None,
                     organisation: Optional[str] = None,
                     location: Optional[str] = None,
                     leader: Optional[str] = None,
                     member: Optional[str] = None,
                     ) -> List[Dict]:
        """
        returns the list of user project ids
        """
        params = {}
        if project_name:
            params['projectName'] = project_name
        if organisation:
            params['organisation'] = organisation
        if location:
            params['location'] = location
        if leader:
            params['projectLeader'] = leader
        if member:
            params['projectMember'] = member
        return self._make_request(
            url=LABTRACE_URL,
            path='projects',
            method='get').json()

    def get_project(self, project_id: str) -> Dict:
        """
        returns project info
        """
        return self._make_request(
            url=LABTRACE_URL,
            path=f'projects/{project_id}',
            method='get').json()

    def get_public_project_files(self, project_id: str) -> List[Dict]:
        """
        returns the list of a project's public file ids
        """
        return self._make_request(
            url=LABTRACE_URL,
            path=f'projects/{project_id}/files',
            method='get').json()

    def get_private_project_files(self, project_id: str) -> List[Dict]:
        """
        returns the list of a project's private file ids
        """
        return self._make_request(
            url=LABTRACE_URL,
            path=f'private-files/project/{project_id}',
            method='get').json()

    def get_public_file(self, project_id: str, file_id: str, save_path: Optional[str] = None) -> Dict:
        """
        returns a public file's content
        """
        content = self._make_request(
            url=LABTRACE_URL,
            path=f'projects/{project_id}/files/{file_id}/download',
            method='get').content
        url = json.loads(content)['s3Url']
        url = url.replace('\\/', '/')

        os.makedirs(save_path, exist_ok=True)

        filename = url.split('/')[-1]
        file_path = os.path.join(save_path, filename)

        resp = requests.get(url)
        with open(file_path, 'wb') as f:
            f.write(resp.content)

        print("File download complete!")
        return content

    def get_public_file_certificate(self, project_id: str, file_id: str, save_path: Optional[str] = None,
                                    raw: Optional[bool] = False) -> Dict:
        """
        returns a public file's certificate
        """
        content = self._make_request(
            url=LABTRACE_URL,
            path=f'projects/{project_id}/files/{file_id}/download/certificate',
            method='get',
            query_params={'raw': raw},
            pdf_Download=True
        ).content
        os.makedirs(save_path, exist_ok=True)

        project = self.get_public_project_files(project_id)
        project_files = project['records']
        matching_file = next((file for file in project_files if file['id'] == file_id), None)
        name = os.path.splitext(matching_file['name'])[0]
        certificate_name = name + "_certificate.pdf"
        file_path = os.path.join(save_path, certificate_name)
        with open(file_path, 'wb') as f:
            f.write(content)
        print("File certificate download complete!")
        return content

    def get_private_file_certificate(self, project_id: str, file_id: str, save_path: Optional[str] = None,
                                     raw: Optional[bool] = False) -> Dict:
        """
        returns a private file's certificate
        """
        content = self._make_request(
            url=LABTRACE_URL,
            path=f'private-files/project/{project_id}/files/{file_id}/download/certificate',
            method='get',
            query_params={'raw': raw},
            pdf_Download=True).content
        os.makedirs(save_path, exist_ok=True)
        project = self.get_private_project_files(project_id)
        project_files = project['records']
        matching_file = next((file for file in project_files if file['id'] == file_id), None)
        name = os.path.splitext(matching_file['name'])[0]
        certificate_name = name + "_certificate.pdf"
        file_path = os.path.join(save_path, certificate_name)
        with open(file_path, 'wb') as f:
            f.write(content)
        print("File certificate download complete!")
        return certificate_name

    def _delete_file(self,
                     url: str,
                     path: str,
                     user_id: str,
                     reason: str) -> str:
        """
        delete a file in a project public directory
        """
        body = {'userId': user_id,
                'reason': reason,
                }
        return self._make_request(
            url=url,
            path=path,
            body=body,
            method='patch').json()

    def delete_public_file(self,
                           project_id: str,
                           file_id: str,
                           user_id: str,
                           reason: str) -> str:
        """
        delete a file in a project public directory
        """
        return self._delete_file(LABTRACE_URL,
                                 path=f'projects/{project_id}/file/{file_id}/delete',
                                 user_id=user_id,
                                 reason=reason)

    def delete_private_file(self,
                            project_id: str,
                            file_id: str,
                            user_id: str,
                            reason: str) -> str:
        """
        delete a file in a project public directory
        """
        return self._delete_file(
            LABTRACE_URL,
            path=f'private-files/project/{project_id}/file/{file_id}/delete',
            user_id=user_id,
            reason=reason)