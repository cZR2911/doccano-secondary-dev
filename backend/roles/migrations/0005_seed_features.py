from django.conf import settings
from django.db import migrations


def create_default_features(apps, schema_editor):
    Feature = apps.get_model("roles", "Feature")
    Role = apps.get_model("roles", "Role")

    # Define features mapping to existing role functionality
    features = {
        "is_project_admin": "Grants project administration privileges",
        "is_annotator": "Grants annotation privileges",
        "is_annotation_approver": "Grants annotation approval privileges",
    }

    feature_objects = {}
    for name, description in features.items():
        feature, _ = Feature.objects.get_or_create(name=name, description=description)
        feature_objects[name] = feature

    # Assign features to existing roles
    role_mapping = {
        settings.ROLE_PROJECT_ADMIN: ["is_project_admin", "is_annotator", "is_annotation_approver"],
        settings.ROLE_ANNOTATOR: ["is_annotator"],
        settings.ROLE_ANNOTATION_APPROVER: ["is_annotation_approver", "is_annotator"],
    }

    for role_name, feature_names in role_mapping.items():
        role, _ = Role.objects.get_or_create(name=role_name)
        role.features.add(*[feature_objects[name] for name in feature_names])


def remove_default_features(apps, schema_editor):
    Feature = apps.get_model("roles", "Feature")
    Feature.objects.filter(name__in=["is_project_admin", "is_annotator", "is_annotation_approver"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("roles", "0004_feature_role_features"),
    ]

    operations = [
        migrations.RunPython(create_default_features, remove_default_features),
    ]
