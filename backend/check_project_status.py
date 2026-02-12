import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from examples.models import Assignment, Example
from projects.models import Member, Project


def check_project_status():
    project = Project.objects.last()
    if not project:
        print("No projects found.")
        return

    print(f"Project: {project.name} (ID: {project.id})")
    print(f"Type: {project.project_type}")
    print(f"Collaborative Annotation: {project.collaborative_annotation}")

    members = Member.objects.filter(project=project)
    print(f"Members: {members.count()}")
    for member in members:
        assignment_count = Assignment.objects.filter(project=project, assignee=member.user).count()
        print(f"  - User: {member.user.username}, Role: {member.role.name}, Assigned Examples: {assignment_count}")

    print("Total Examples:", Example.objects.filter(project=project).count())
    print("Total Assignments:", Assignment.objects.filter(project=project).count())


if __name__ == "__main__":
    check_project_status()
