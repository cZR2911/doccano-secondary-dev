import uuid
from typing import List, Optional, Type

import pandas as pd
from pydantic import UUID4, BaseModel

from .data import BaseData
from .exceptions import FileParseException
from .label import Label
from .readers import (
    DEFAULT_LABEL_COLUMN,
    DEFAULT_TEXT_COLUMN,
    LINE_NUMBER_COLUMN,
    UPLOAD_NAME_COLUMN,
    UUID_COLUMN,
)
from examples.models import Comment as CommentModel
from examples.models import Example
from projects.models import Project


class ExampleMaker:
    def __init__(
        self,
        project: Project,
        data_class: Type[BaseData],
        column_data: str = DEFAULT_TEXT_COLUMN,
        exclude_columns: Optional[List[str]] = None,
    ):
        self.project = project
        self.data_class = data_class
        self.column_data = column_data
        self.exclude_columns = exclude_columns or []
        self._errors: List[FileParseException] = []

    def make(self, df: pd.DataFrame) -> List[Example]:
        if not self.check_column_existence(df):
            return []
        self.check_value_existence(df)
        # make dataframe without exclude columns and missing data
        df_with_data_column = df.loc[:, ~df.columns.isin(self.exclude_columns)]
        
        # Convert to string and strip whitespace before checking for empty text
        df_with_data_column[self.column_data] = df_with_data_column[self.column_data].astype(str).str.strip()
        df_with_data_column = df_with_data_column[df_with_data_column[self.column_data] != ""]
        df_with_data_column = df_with_data_column[df_with_data_column[self.column_data] != "nan"]
        df_with_data_column = df_with_data_column[df_with_data_column[self.column_data] != "None"]

        examples = []
        for row in df_with_data_column.to_dict(orient="records"):
            line_num = row.pop(LINE_NUMBER_COLUMN, 0)
            row[DEFAULT_TEXT_COLUMN] = row.pop(self.column_data)  # Rename column for parsing
            try:
                data = self.data_class.parse(**row)
                example = data.create(self.project)
                examples.append(example)
            except ValueError:
                # Skip invalid data instead of adding an error to the UI
                continue
        return examples

    def check_column_existence(self, df: pd.DataFrame) -> bool:
        if self.column_data not in df.columns:
            # Try to find a fallback column from known aliases
            if self.column_data == DEFAULT_TEXT_COLUMN:
                # Broaden aliases and clean them
                aliases = ['text', 'Text', 'TEXT', '文本', '内容', '句子', '方向', '工作内容', 'query', 'Query', 'question', 'Question', 'data', 'Data']
                
                # Check for exact matches first
                for alias in aliases:
                    if alias in df.columns:
                        self.column_data = alias
                        return True
                
                # Check for partial matches or case-insensitive matches
                for col in df.columns:
                    for alias in aliases:
                        if alias.lower() in col.lower():
                            self.column_data = col
                            return True

                # If there's only one non-internal column, use it as text
                internal_cols = {UPLOAD_NAME_COLUMN, UUID_COLUMN, LINE_NUMBER_COLUMN, "filename"}
                external_cols = [c for c in df.columns if c not in internal_cols]
                if len(external_cols) >= 1:
                    # Pick the first non-internal column as a last resort
                    self.column_data = external_cols[0]
                    return True
            
            # Filter out internal columns for clearer error message
            internal_cols = {UPLOAD_NAME_COLUMN, UUID_COLUMN, LINE_NUMBER_COLUMN, "filename"}
            available = ", ".join([c for c in df.columns if c not in internal_cols])
            message = f"Column '{self.column_data}' not found in the file. Available columns: {available}"
            for filename in df[UPLOAD_NAME_COLUMN].unique():
                self._errors.append(FileParseException(filename, 0, message))
            return False
        return True

    def check_value_existence(self, df: pd.DataFrame):
        df_without_data_column = df[df[self.column_data].isnull()]
        for row in df_without_data_column.to_dict(orient="records"):
            message = f"Column {self.column_data} not found in record"
            error = FileParseException(row[UPLOAD_NAME_COLUMN], row.get(LINE_NUMBER_COLUMN, 0), message)
            self._errors.append(error)

    @property
    def errors(self) -> List[FileParseException]:
        self._errors.sort(key=lambda error: error.line_num)
        return self._errors


# [EXPERIMENTAL-FEATURE-START]
# The following classes support the "Knowledge Correction" workflow by allowing
# comments and corrections to be imported from Excel columns.
class CommentData(BaseModel):
    uuid: UUID4
    example_uuid: UUID4
    text: str

    def __init__(self, **data):
        if "uuid" not in data:
            data["uuid"] = uuid.uuid4()
        super().__init__(**data)

    @classmethod
    def parse(cls, example_uuid: UUID4, text: str):
        return cls(example_uuid=example_uuid, text=text)

    def create(self, user, example: Example) -> CommentModel:
        return CommentModel(user=user, example=example, text=self.text)


class CommentMaker:
    def __init__(self, comment_column: str = "comment", correction_column: str = "correction"):
        self.comment_column = comment_column
        self.correction_column = correction_column
        self._errors: List[FileParseException] = []

    def make(self, df: pd.DataFrame) -> List[CommentData]:
        # Alias resolution for comment and correction columns
        self.resolve_column(df, "comment_column", ["comment", "Comment", "批注", "备注", "comments", "Comments"])
        self.resolve_column(
            df, "correction_column", ["correction", "Correction", "纠错", "更正", "corrections", "Corrections"]
        )

        has_comment = self.comment_column in df.columns
        has_correction = self.correction_column in df.columns

        if not has_comment and not has_correction:
            return []

        comments = []
        for row in df.to_dict(orient="records"):
            text_parts = []
            if has_comment and pd.notna(row.get(self.comment_column)):
                val = str(row[self.comment_column]).strip()
                if val and val.lower() != "nan" and val.lower() != "none":
                    text_parts.append(f"Comment: {val}")

            if has_correction and pd.notna(row.get(self.correction_column)):
                val = str(row[self.correction_column]).strip()
                if val and val.lower() != "nan" and val.lower() != "none":
                    text_parts.append(f"Correction: {val}")

            if text_parts:
                full_text = "\n".join(text_parts)
                comments.append(CommentData.parse(row[UUID_COLUMN], full_text))
        return comments

    def resolve_column(self, df: pd.DataFrame, attr_name: str, aliases: List[str]):
        current = getattr(self, attr_name)
        if current in df.columns:
            return

        for alias in aliases:
            if alias in df.columns:
                setattr(self, attr_name, alias)
                return
            # Case insensitive
            for col in df.columns:
                if alias.lower() == col.lower():
                    setattr(self, attr_name, col)
                    return
# [EXPERIMENTAL-FEATURE-END]


class BinaryExampleMaker(ExampleMaker):
    def make(self, df: pd.DataFrame) -> List[Example]:
        examples = []
        for row in df.to_dict(orient="records"):
            data = self.data_class.parse(**row)
            example = data.create(self.project)
            examples.append(example)
        return examples


class LabelMaker:
    def __init__(self, column: str, label_class: Type[Label]):
        self.column = column
        self.label_class = label_class
        self._errors: List[FileParseException] = []

    def make(self, df: pd.DataFrame) -> List[Label]:
        if not self.check_column_existence(df):
            return []

        df_label = df.explode(self.column)
        df_label = df_label[[UUID_COLUMN, self.column]]
        df_label.dropna(subset=[self.column], inplace=True)
        labels = []
        for row in df_label.to_dict(orient="records"):
            try:
                label = self.label_class.parse(row[UUID_COLUMN], row[self.column])
                labels.append(label)
            except ValueError:
                pass
        return labels

    def check_column_existence(self, df: pd.DataFrame) -> bool:
        if self.column not in df.columns:
            # Try to find a fallback column from known aliases
            if self.column == DEFAULT_LABEL_COLUMN:
                aliases = ['label', 'Label', 'LABEL', '标签', '类别', 'tag', 'Tag', 'category', 'Category']
                
                # Check for exact matches first
                for alias in aliases:
                    if alias in df.columns:
                        self.column = alias
                        return True
                
                # Check for partial matches or case-insensitive matches
                for col in df.columns:
                    for alias in aliases:
                        if alias.lower() in col.lower():
                            self.column = col
                            return True
            
            # Label column is optional for many projects, so we don't raise an error here
            return False
        return True

    @property
    def errors(self) -> List[FileParseException]:
        self._errors.sort(key=lambda error: error.line_num)
        return self._errors
