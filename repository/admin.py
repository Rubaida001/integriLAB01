from django.contrib import admin

from repository.models import DocRepositoryConnection, DocRepositoryProject, DocRepositoryDetail, \
    CodeRepositoryConnection, CodeRepositoryProject, DataRepositoryConnection, \
    DataRepositoryProject, BlockRepositoryConnection, CodeRepositoryDetail, DataRepositoryDetail, \
    BlockRepositoryDetail


# Register your models here.
class DocRepositoryConnectionAdmin(admin.ModelAdmin):
    list_display = ('doc_repo_id', 'notebook_user_id', 'repo_username', 'git_token')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False



class DocRepositoryProjectAdmin(admin.ModelAdmin):
    list_display = ('doc_project_id', 'notebook_user_id', 'project_id', 'document_name')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False


class DocRepositoryDetailsAdmin(admin.ModelAdmin):
    list_display = ('doc_details_id','committed_hash','committed_by','committed_msg','committed_date',)
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False

class CodeRepositoryConnectionAdmin(admin.ModelAdmin):
    list_display = ('code_repo_id', 'notebook_user_id', 'repo_username', 'repo_password')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False


class CodeRepositoryProjectAdmin(admin.ModelAdmin):
    list_display = ('code_project_id', 'repo_username_for_connection', 'code_repo_name', 'project_id')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True
    def has_view_permission(self, request, obj=None):
        return True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(project_id__isnull=False)  # Example filter


class CodeRepositoryDetailsAdmin(admin.ModelAdmin):
    list_display = ('code_details_id','committed_hash','committed_by','committed_msg','committed_date','committed_url')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False




class DataRepositoryConnectionAdmin(admin.ModelAdmin):
    list_display = ('data_repo_id', 'notebook_user_id', 'repo_username', 'repo_password', 'data_server')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False



class DataRepositoryProjectAdmin(admin.ModelAdmin):
    list_display = ('data_project_id', 'repo_username_for_connection', 'data_repo_path', 'project_id')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False

class DataRepositoryDetailsAdmin(admin.ModelAdmin):
    list_display = ('data_details_id','committed_hash','committed_by','committed_msg','committed_date')
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


class BlockRepositoryConnectionAdmin(admin.ModelAdmin):
    list_display = ('block_repo_id', 'notebook_user_id', 'block_username', 'block_password')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True

class BlockRepositoryDetailAdmin(admin.ModelAdmin):
    list_display = ('block_details_id','project','data_hash','code_hash','doc_hash','block_hash', 'committed_date')
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return False
    def has_view_permission(self, request, obj=None):
        return True
    def get_queryset(self, request):
        return super().get_queryset(request)

admin.site.register(DocRepositoryConnection,DocRepositoryConnectionAdmin)
admin.site.register(DocRepositoryProject,DocRepositoryProjectAdmin)
admin.site.register(DocRepositoryDetail,DocRepositoryDetailsAdmin)

admin.site.register(CodeRepositoryConnection,CodeRepositoryConnectionAdmin)
admin.site.register(CodeRepositoryProject,CodeRepositoryProjectAdmin)
admin.site.register(CodeRepositoryDetail,CodeRepositoryDetailsAdmin)

admin.site.register(DataRepositoryConnection,DataRepositoryConnectionAdmin)
admin.site.register(DataRepositoryProject,DataRepositoryProjectAdmin)
admin.site.register(DataRepositoryDetail,DataRepositoryDetailsAdmin)

admin.site.register(BlockRepositoryConnection,BlockRepositoryConnectionAdmin)
admin.site.register(BlockRepositoryDetail,BlockRepositoryDetailAdmin)
