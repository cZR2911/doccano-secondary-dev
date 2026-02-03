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

        # Handle multiple columns concatenation
        raw_columns = self.column_data.replace('，', ',')
        column_list = [c.strip() for c in raw_columns.split(',')]
        if len(column_list) > 1:
            merged_col_name = f"merged_{uuid.uuid4().hex[:8]}"
            col_map = {str(c).strip(): c for c in df.columns}
            
            # Filter ONLY columns that actually exist in the file
            existing_cols = [col_map[c] for c in column_list if c in col_map]
            
            if existing_cols:
                df[merged_col_name] = df[existing_cols].fillna('').astype(str).agg('\n'.join, axis=1)
                self.column_data = merged_col_name
            elif self.column_data in df.columns:
                pass
            else:
                 available = ", ".join([f"'{c}'" for c in df.columns if str(c) not in {UPLOAD_NAME_COLUMN, UUID_COLUMN, LINE_NUMBER_COLUMN, "filename"}])
                 message = f"Column(s) '{self.column_data}' not found. Available: {available}"
                 filename = df[UPLOAD_NAME_COLUMN].iloc[0] if not df.empty else "Unknown"
                 self._errors.append(FileParseException(filename, 0, message))
                 return []

        self.check_value_existence(df)
        # make dataframe without exclude columns and missing data
        df_with_data_column = df.loc[:, ~df.columns.isin(self.exclude_columns)]
        
        # Ensure the target data column is treated as string
        df_with_data_column[self.column_data] = df_with_data_column[self.column_data].fillna('').astype(str).str.strip()
        
        # Filter out empty records
        df_with_data_column = df_with_data_column[
            (df_with_data_column[self.column_data] != "") &
            (df_with_data_column[self.column_data].str.lower() != "nan") &
            (df_with_data_column[self.column_data].str.lower() != "none")
        ]

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
        # 1. Handle wildcard merge (Merge all external columns)
        if self.column_data == '*':
            internal_cols = {UPLOAD_NAME_COLUMN, UUID_COLUMN, LINE_NUMBER_COLUMN, "filename"}
            external_cols = [c for c in df.columns if c not in internal_cols]
            if external_cols:
                self.column_data = ','.join(external_cols)
                return True
            return False

        # 2. Handle explicit multiple columns (comma-separated)
        raw_columns = self.column_data.replace('，', ',')
        if ',' in raw_columns:
            column_list = [c.strip() for c in raw_columns.split(',')]
            col_map = {str(c).strip(): c for c in df.columns}
            
            # If at least one column matches, we consider it exists and will filter missing ones later in make()
            existing_cols = [col_map[c] for c in column_list if c in col_map]
            if existing_cols:
                return True
            
            if self.column_data in df.columns:
                return True

        # 3. Standard check for single column
        if self.column_data in df.columns:
            return True

        # 4. Fallback logic for default "text" column
        if self.column_data == DEFAULT_TEXT_COLUMN:
            # Common aliases for text content
            aliases = [
                'text', 'Text', 'TEXT', '文本', '内容', '句子', '方向', '工作内容',
                'query', 'Query', 'question', 'Question', 'data', 'Data',
                'title', 'Title', 'subject', 'Subject', 'description', 'Description',
                'body', 'Body', 'prompt', 'Prompt', 'completion', 'Completion',
                'input', 'Input', 'output', 'Output', 'context', 'Context',
                'response', 'Response', 'instruction', 'Instruction',
                'summary', 'Summary', 'abstract', 'Abstract'
            ]
            
            # Find all columns that match any alias (case-insensitive)
            matched_cols = []
            for col in df.columns:
                if any(alias.lower() == str(col).lower() for alias in aliases):
                    matched_cols.append(col)
            
            if matched_cols:
                # If multiple aliases found, suggest merging them
                self.column_data = ','.join(matched_cols)
                return True

            # If no aliases found, try partial matches
            partial_matches = []
            for col in df.columns:
                if any(alias.lower() in str(col).lower() for alias in aliases):
                    partial_matches.append(col)
            
            if partial_matches:
                self.column_data = ','.join(partial_matches)
                return True

            # Last resort: If multiple external columns exist, merge them all
            internal_cols = {UPLOAD_NAME_COLUMN, UUID_COLUMN, LINE_NUMBER_COLUMN, "filename"}
            external_cols = [c for c in df.columns if c not in internal_cols]
            if len(external_cols) > 0:
                # Merge all external columns as a convenient default
                self.column_data = ','.join(external_cols)
                return True
        
        # 4. Error reporting if no column found
        internal_cols = {UPLOAD_NAME_COLUMN, UUID_COLUMN, LINE_NUMBER_COLUMN, "filename"}
        available_list = [str(c) for c in df.columns if str(c) not in internal_cols]
        available = ", ".join([f"'{c}'" for c in available_list])
        message = f"Column(s) '{self.column_data}' not found. Available: {available}"
        for filename in df[UPLOAD_NAME_COLUMN].unique():
            self._errors.append(FileParseException(filename, 0, message))
        return False

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

        # Support multiple label columns separated by comma
        raw_columns = self.column.replace('，', ',')
        column_list = [c.strip() for c in raw_columns.split(',')]
        
        # Mapping for robust matching
        col_map = {str(c).strip(): c for c in df.columns}
        
        labels = []
        for col_name in column_list:
            if col_name not in col_map:
                continue
            
            actual_col = col_map[col_name]
            df_label = df.explode(actual_col)
            df_label = df_label[[UUID_COLUMN, actual_col]]
            df_label.dropna(subset=[actual_col], inplace=True)
            for row in df_label.to_dict(orient="records"):
                try:
                    label = self.label_class.parse(row[UUID_COLUMN], row[actual_col])
                    labels.append(label)
                except ValueError:
                    pass
        return labels

    def check_column_existence(self, df: pd.DataFrame) -> bool:
        # Support comma-separated columns
        raw_columns = self.column.replace('，', ',')
        column_list = [c.strip() for c in raw_columns.split(',')]
        col_map = {str(c).strip(): c for c in df.columns}

        if len(column_list) > 1:
            # If any of the columns exist, we consider it valid
            if any(col in col_map for col in column_list):
                return True

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
