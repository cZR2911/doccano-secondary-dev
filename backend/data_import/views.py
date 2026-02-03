from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .celery_tasks import import_dataset
from .pipeline.catalog import Options
from projects.models import Project
from projects.permissions import IsProjectAdmin
from django_drf_filepond.models import TemporaryUpload
import pandas as pd


class DatasetCatalog(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get(self, request, *args, **kwargs):
        project_id = kwargs["project_id"]
        project = get_object_or_404(Project, pk=project_id)
        use_relation = getattr(project, "use_relation", False)
        options = Options.filter_by_task(project.project_type, use_relation)
        return Response(data=options, status=status.HTTP_200_OK)


class DatasetImportAPI(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, *args, **kwargs):
        upload_ids = request.data.pop("uploadIds")
        file_format = request.data.pop("format")
        task = request.data.pop("task")
        celery_task = import_dataset.delay(
            user_id=request.user.id,
            project_id=self.kwargs["project_id"],
            file_format=file_format,
            upload_ids=upload_ids,
            task=task,
            **request.data,
        )
        return Response({"task_id": celery_task.task_id})


class DatasetColumnPreview(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get(self, request, *args, **kwargs):
        upload_id = request.query_params.get("upload_id")
        if not upload_id:
            return Response({"columns": []}, status=status.HTTP_200_OK)

        try:
            print(f"Debug: Requesting columns for upload_id={upload_id}")
            tu = TemporaryUpload.objects.get(upload_id=upload_id)
            file_path = tu.file.path
            print(f"Debug: File path found: {file_path}")

            # Basic support for Excel and CSV
            if str(file_path).lower().endswith('.csv'):
                print("Debug: Reading CSV")
                df = pd.read_csv(file_path, nrows=0)
            # Check for Excel extensions or no extension (FilePond sometimes saves without extension)
            else:
                try:
                    print("Debug: Trying to read as Excel")
                    df = pd.read_excel(file_path, nrows=0)
                except Exception as excel_error:
                     print(f"Debug: Excel read failed: {excel_error}. Trying CSV fallback.")
                     try:
                        df = pd.read_csv(file_path, nrows=0)
                     except Exception as csv_error:
                        print(f"Debug: CSV fallback failed: {csv_error}")
                        return Response({"columns": []}, status=status.HTTP_200_OK)

            cols = list(df.columns)
            print(f"Debug: Columns found: {cols}")
            return Response({"columns": cols}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error in DatasetColumnPreview: {e}")
            return Response({"columns": []}, status=status.HTTP_200_OK)
