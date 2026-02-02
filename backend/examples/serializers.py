from rest_framework import serializers

from .models import Assignment, Comment, Example, ExampleState


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "username",
            "example",
            "text",
            "created_at",
        )
        read_only_fields = ("user", "example")


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ("id", "assignee", "example", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ExampleSerializer(serializers.ModelSerializer):
    annotation_approver = serializers.SerializerMethodField()
    is_confirmed = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()

    @classmethod
    def get_annotation_approver(cls, instance):
        approver = instance.annotations_approved_by
        return approver.username if approver else None

    def get_is_confirmed(self, instance):
        user = self.context.get("request").user
        if instance.project.collaborative_annotation:
            states = instance.states.all()
        else:
            states = instance.states.filter(confirmed_by_id=user.id)
        return states.count() > 0

    def get_assignments(self, instance):
        return [
            {
                "id": assignment.id,
                "assignee": assignment.assignee.username,
                "assignee_id": assignment.assignee.id,
            }
            for assignment in instance.assignments.all()
        ]

    class Meta:
        model = Example
        fields = [
            "id",
            "filename",
            "meta",
            "annotation_approver",
            "comment_count",
            "text",
            "is_confirmed",
            "upload_name",
            "score",
            "assignments",
        ]
        read_only_fields = ["filename", "is_confirmed", "upload_name", "assignments"]

    def update(self, instance, validated_data):
        new_text = validated_data.get("text")
        if new_text and new_text != instance.text:
            # [EXPERIMENTAL-FEATURE-START] Preserve original text in meta if not present
            # We must update validated_data['meta'] because super().update will overwrite instance.meta
            meta = validated_data.get("meta", instance.meta)
            # Ensure meta is a dict (it might be None if not passed, though instance.meta defaults to dict)
            if meta is None:
                meta = {}
            
            if "original_text" not in meta:
                # Use strict copy to avoid reference issues, though simple dict assignment is usually fine here
                meta = dict(meta)
                meta["original_text"] = instance.text
                validated_data["meta"] = meta
            # [EXPERIMENTAL-FEATURE-END]
        return super().update(instance, validated_data)


class ExampleStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExampleState
        fields = ("id", "example", "confirmed_by", "confirmed_at")
        read_only_fields = ("id", "example", "confirmed_by", "confirmed_at")
