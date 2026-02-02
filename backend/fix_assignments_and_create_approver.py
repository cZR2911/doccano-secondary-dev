import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.contrib.auth.models import User
from projects.models import Project, Member
from roles.models import Role  # Corrected import
from examples.models import Example, Assignment

def fix_assignments_and_create_approver():
    project = Project.objects.last() # ID 59
    if not project:
        print("No project found.")
        return

    print(f"Working on project: {project.name} (ID: {project.id})")

    # 1. Fix assignments for 'bz' (Annotator)
    try:
        bz_user = User.objects.get(username='bz')
        examples = Example.objects.filter(project=project)
        
        # Create assignments for bz
        count = 0
        for example in examples:
            _, created = Assignment.objects.get_or_create(
                project=project,
                example=example,
                assignee=bz_user
            )
            if created:
                count += 1
        print(f"Assigned {count} examples to user 'bz' (annotator). Now they should see data.")
    except User.DoesNotExist:
        print("User 'bz' not found.")

    # 2. Create 'sh' (Approver) for testing
    sh_user, created = User.objects.get_or_create(username='sh')
    if created:
        sh_user.set_password('password')
        sh_user.save()
        print("Created user 'sh' with password 'password'.")
    else:
        print("User 'sh' already exists.")

    # Add 'sh' to project as annotation_approver
    try:
        role_approver = Role.objects.get(name='annotation_approver')
        member, created = Member.objects.get_or_create(
            project=project,
            user=sh_user,
            defaults={'role': role_approver}
        )
        if not created and member.role != role_approver:
            member.role = role_approver
            member.save()
            print("Updated 'sh' role to annotation_approver.")
        elif created:
            print("Added 'sh' to project as annotation_approver.")
        
        # Assign examples to 'sh' so they can see them too
        count_sh = 0
        for example in examples:
            _, created = Assignment.objects.get_or_create(
                project=project,
                example=example,
                assignee=sh_user
            )
            if created:
                count_sh += 1
        print(f"Assigned {count_sh} examples to user 'sh' (approver).")

    except Exception as e:
        print(f"Error setting up approver: {e}")

if __name__ == "__main__":
    fix_assignments_and_create_approver()
