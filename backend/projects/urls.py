from django.urls import path

from .views.attachment import AttachmentDetail, AttachmentList
from .views.member import MemberDetail, MemberList, MyRole
from .views.project import CloneProject, ProjectDetail, ProjectList
from .views.tag import TagDetail, TagList

urlpatterns = [
    path(route="projects", view=ProjectList.as_view(), name="project_list"),
    path(route="projects/<int:project_id>", view=ProjectDetail.as_view(), name="project_detail"),
    path(route="projects/<int:project_id>/my-role", view=MyRole.as_view(), name="my_role"),
    path(route="projects/<int:project_id>/tags", view=TagList.as_view(), name="tag_list"),
    path(route="projects/<int:project_id>/tags/<int:tag_id>", view=TagDetail.as_view(), name="tag_detail"),
    path(route="projects/<int:project_id>/members", view=MemberList.as_view(), name="member_list"),
    path(route="projects/<int:project_id>/clone", view=CloneProject.as_view(), name="clone_project"),
    path(route="projects/<int:project_id>/members/<int:member_id>", view=MemberDetail.as_view(), name="member_detail"),
    path(route="projects/<int:project_id>/attachments", view=AttachmentList.as_view(), name="attachment_list"),
    path(
        route="projects/<int:project_id>/attachments/<int:attachment_id>",
        view=AttachmentDetail.as_view(),
        name="attachment_detail",
    ),
]
