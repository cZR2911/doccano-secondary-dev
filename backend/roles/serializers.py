from rest_framework import serializers

from .models import Feature, Role


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ("id", "name", "description")


class RoleSerializer(serializers.ModelSerializer):
    features = FeatureSerializer(many=True, read_only=True)
    feature_ids = serializers.PrimaryKeyRelatedField(
        queryset=Feature.objects.all(), source="features", write_only=True, many=True
    )

    class Meta:
        model = Role
        fields = ("id", "name", "description", "features", "feature_ids")
