from django.conf import settings
from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import Member


class RolePermission(BasePermission):
    UNSAFE_METHODS = ("POST", "PATCH", "DELETE")
    unsafe_methods_check = True
    feature_name = ""

    @classmethod
    def get_project_id(cls, request, view):
        return view.kwargs.get("project_id") or request.query_params.get("project_id")

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if self.unsafe_methods_check and request.method in self.UNSAFE_METHODS:
            return request.user.is_superuser

        project_id = self.get_project_id(request, view)
        if not project_id and request.method in SAFE_METHODS:
            return True

        return Member.objects.has_feature(project_id, request.user, self.feature_name)


class IsProjectAdmin(RolePermission):
    unsafe_methods_check = False
    feature_name = "is_project_admin"


class IsAnnotatorAndReadOnly(RolePermission):
    feature_name = "is_annotator"


class IsAnnotator(RolePermission):
    unsafe_methods_check = False
    feature_name = "is_annotator"


class IsAnnotationApproverAndReadOnly(RolePermission):
    feature_name = "is_annotation_approver"


class IsAnnotationApprover(RolePermission):
    unsafe_methods_check = False
    feature_name = "is_annotation_approver"


IsProjectMember = IsAnnotator | IsAnnotationApprover | IsProjectAdmin  # type: ignore
IsProjectAdminOrApprover = IsProjectAdmin | IsAnnotationApprover  # type: ignore
IsProjectStaffAndReadOnly = IsAnnotatorAndReadOnly | IsAnnotationApproverAndReadOnly  # type: ignore
