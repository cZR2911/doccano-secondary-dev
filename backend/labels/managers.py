from django.db.models import Count, Manager


class LabelManager(Manager):
    label_type_field = "label"

    def calc_label_distribution(self, examples, members, labels):
        """Calculate label distribution.

        【标签分布统计】
        前端位置：仪表盘 (Dashboard) -> 统计 (Statistics) -> 标签分布 (Label Distribution)
        功能说明：统计每个用户分别使用了多少次某个标签。
        数学意义：频数分布表 (Frequency Distribution Table)。

        Args:
            examples: example queryset. (筛选后的样本集合)
            members: user queryset. (参与统计的用户集合)
            labels: label queryset. (需要统计的标签集合)

        Returns:
            label distribution per user.
            返回格式：
            {
                'admin': {'positive': 10, 'negative': 5},
                'annotator1': {'positive': 8, 'negative': 12}
            }

        Examples:
            >>> self.calc_label_distribution(examples, members, labels)
            {'admin': {'positive': 10, 'negative': 5}}
        """
        # 初始化字典：为每个用户、每个标签的计数预设为 0
        distribution = {member.username: {label.text: 0 for label in labels} for member in members}
        
        # 核心 SQL 聚合查询
        # SELECT user.username, label.text, COUNT(label.text)
        # FROM labels
        # WHERE example_id IN (...)
        # GROUP BY user.username, label.text
        items = (
            self.filter(example_id__in=examples)
            .values("user__username", f"{self.label_type_field}__text")
            .annotate(count=Count(f"{self.label_type_field}__text"))
        )
        
        # 将数据库查询结果填充回字典
        for item in items:
            username = item["user__username"]
            label = item[f"{self.label_type_field}__text"]
            count = item["count"]
            if username in distribution and label in distribution[username]:
                distribution[username][label] = count
        return distribution

    def get_labels(self, label, project):
        if project.collaborative_annotation:
            return self.filter(example=label.example)
        else:
            return self.filter(example=label.example, user=label.user)

    def can_annotate(self, label, project) -> bool:
        raise NotImplementedError("Please implement this method in the subclass")

    def filter_annotatable_labels(self, labels, project):
        return [label for label in labels if self.can_annotate(label, project)]


class CategoryManager(LabelManager):
    def can_annotate(self, label, project) -> bool:
        is_exclusive = project.single_class_classification
        categories = self.get_labels(label, project)
        if is_exclusive:
            return not categories.exists()
        else:
            return not categories.filter(label=label.label).exists()


class SpanManager(LabelManager):
    def can_annotate(self, label, project) -> bool:
        overlapping = getattr(project, "allow_overlapping", False)
        spans = self.get_labels(label, project)
        if overlapping:
            return True
        for span in spans:
            if span.is_overlapping(label):
                return False
        return True


class TextLabelManager(LabelManager):
    def can_annotate(self, label, project) -> bool:
        texts = self.get_labels(label, project)
        for text in texts:
            if text.is_same_text(label):
                return False
        return True


class RelationManager(LabelManager):
    label_type_field = "type"

    def can_annotate(self, label, project) -> bool:
        return True


class BoundingBoxManager(LabelManager):
    def can_annotate(self, label, project) -> bool:
        return True


class SegmentationManager(LabelManager):
    def can_annotate(self, label, project) -> bool:
        return True
