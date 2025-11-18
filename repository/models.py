from django.db import models
from management.models import Project, User


class DocRepositoryConnection(models.Model):
    doc_repo_id = models.AutoField(primary_key=True)
    notebook_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_username = models.EmailField(max_length=255)
    git_token = models.CharField(max_length=255)

    def __int__(self):
        return self.doc_repo_id


class DocRepositoryProject(models.Model):
    doc_project_id = models.AutoField(primary_key=True)
    document_name = models.CharField(max_length=255)
    git_link = models.CharField(max_length=255)
    notebook_user_id = models.ForeignKey(DocRepositoryConnection, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.document_name


class DocRepositoryDetail(models.Model):
    doc_details_id = models.ForeignKey(DocRepositoryProject, on_delete=models.CASCADE,
                                       related_name='DocRepositoryDetails')
    committed_hash = models.CharField(max_length=255, unique=True)
    committed_by = models.CharField(max_length=255)
    committed_msg = models.CharField(max_length=255)
    committed_date = models.DateField()

    def __int__(self):
        return self.doc_details_id


class CodeRepositoryConnection(models.Model):
    code_repo_id = models.AutoField(primary_key=True)
    notebook_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_username = models.CharField(max_length=255)
    repo_password = models.CharField(max_length=255)

    def __int__(self):
        return self.code_repo_id


class CodeRepositoryProject(models.Model):
    code_project_id = models.AutoField(primary_key=True)
    code_repo_name = models.CharField(max_length=255)
    repo_username_for_connection = models.ForeignKey(CodeRepositoryConnection, on_delete=models.CASCADE) 
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.code_repo_name


class CodeRepositoryDetail(models.Model):
    code_details_id = models.ForeignKey(CodeRepositoryProject, on_delete=models.CASCADE,
                                        related_name="CodeRepositoryDetails")
    committed_hash = models.CharField(max_length=255, unique=True)
    committed_by = models.CharField(max_length=255)
    committed_msg = models.CharField(max_length=255)
    committed_date = models.DateField()
    committed_url = models.CharField(max_length=500)

    def __int__(self):
        return self.code_details_id


class DataRepositoryConnection(models.Model):
    data_repo_id = models.AutoField(primary_key=True)
    notebook_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_username = models.CharField(max_length=255)
    repo_password = models.CharField(max_length=255)
    data_server = models.CharField(max_length=255)

    def __int__(self):
        return self.data_repo_id


class DataRepositoryProject(models.Model):
    data_project_id = models.AutoField(primary_key=True)
    data_repo_path = models.CharField(max_length=255)
    repo_username_for_connection = models.ForeignKey(DataRepositoryConnection, on_delete=models.CASCADE) 
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __int__(self):
        return self.data_project_id


class DataRepositoryDetail(models.Model):
    data_details_id = models.ForeignKey(DataRepositoryProject, on_delete=models.CASCADE,
                                        related_name='DataRepositoryDetails')
    committed_hash = models.CharField(max_length=255, unique=True)
    committed_by = models.CharField(max_length=255)
    committed_msg = models.CharField(max_length=255)
    committed_date = models.DateField()

    def __int__(self):
        return self.data_details_id


class BlockRepositoryConnection(models.Model):
    block_repo_id = models.AutoField(primary_key=True)
    notebook_user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    block_username = models.EmailField(max_length=255)
    block_password = models.CharField(max_length=255)

    def __int__(self):
        return self.block_repo_id


class BlockRepositoryDetail(models.Model):
    block_details_id = models.ForeignKey(BlockRepositoryConnection, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='BlockRepositoryDetails')
    data_repo = models.ForeignKey(DataRepositoryProject, on_delete=models.CASCADE, related_name='DataRepository')
    code_repo = models.ForeignKey(CodeRepositoryProject, on_delete=models.CASCADE, related_name='CodeRepository')
    doc_repo = models.ForeignKey(DocRepositoryProject, on_delete=models.CASCADE, related_name='DocRepository')
    data_hash = models.CharField(max_length=255)
    code_hash = models.CharField(max_length=255)
    doc_hash = models.CharField(max_length=255)
    block_hash = models.CharField(max_length=255, unique=True)
    comment = models.CharField(max_length=500)
    committed_date = models.DateField()

    class Meta:
        unique_together = ["data_hash", "code_hash", "doc_hash"]

    def __str__(self):
        return f"Combined Hash for {self.project.project_name}"
