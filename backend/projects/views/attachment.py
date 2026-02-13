from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from projects.models import Attachment, Project
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from projects.serializers import AttachmentSerializer


class AttachmentList(generics.ListCreateAPIView):
    serializer_class = AttachmentSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    pagination_class = None

    def get_queryset(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        return project.attachments.all()

    def perform_create(self, serializer):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        serializer.save(project=project)


class AttachmentDetail(generics.RetrieveDestroyAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer
    lookup_url_kwarg = "attachment_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
