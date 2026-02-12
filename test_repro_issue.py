
import pandas as pd
import unittest
from unittest.mock import MagicMock
from typing import Any, List
from pydantic import UUID4, BaseModel
import uuid

# Mock classes to simulate backend environment
class Label(BaseModel):
    uuid: UUID4
    example_uuid: UUID4
    
    @classmethod
    def parse(cls, example_uuid, obj):
        raise NotImplementedError

class SpanLabel(Label):
    label: str
    start_offset: int
    end_offset: int
    
    @classmethod
    def parse(cls, example_uuid, obj):
        if isinstance(obj, (list, tuple)):
            return cls(example_uuid=example_uuid, label=obj[2], start_offset=obj[0], end_offset=obj[1])
        elif isinstance(obj, dict):
            return cls(example_uuid=example_uuid, **obj)
        raise ValueError("SpanLabel.parse()")

# Copy of LabelMaker from makers.py (with minimal dependencies)
class FileParseException(Exception):
    def __init__(self, filename, line_num, message):
        self.filename = filename
        self.line_num = line_num
        self.message = message

class LabelMaker:
    def __init__(self, column: str, label_class, text_column=None):
        self.column = column
        self.label_class = label_class
        self.text_column = text_column
        self._errors = []

    def make(self, df: pd.DataFrame):
        # Simplified make method focusing on the logic in question
        raw_columns = self.column.replace('，', ',')
        column_list = [c.strip() for c in raw_columns.split(',')]
        col_map = {str(c).strip(): c for c in df.columns}
        
        labels = []
        GENERIC_LABEL_NAMES = {'label', 'text', 'tag'} # Simplified
        UUID_COLUMN = 'uuid'
        
        for col_name in column_list:
            if col_name not in col_map: continue
            actual_col = col_map[col_name]
            
            # Indicator logic (simplified)
            is_indicator = False
            # ... skipping category logic for now as user issue is likely SpanLabel ...

            # Simulate explode and iterate
            # We assume 1 row for simplicity
            for i, row in df.iterrows():
                val = row[actual_col]
                row_dict = row.to_dict()
                
                try:
                    # Try standard parse
                    label = self.label_class.parse(row_dict[UUID_COLUMN], val)
                    labels.append(label)
                    print(f"Standard parse success: {label}")
                except ValueError:
                    # Fallback logic
                    if self.label_class.__name__ == 'SpanLabel' and self.text_column and self.text_column in row_dict:
                        try:
                            text = str(row_dict[self.text_column])
                            val_str = str(val).strip()
                            if val_str:
                                search_start = 0
                                while True:
                                    start = text.find(val_str, search_start)
                                    if start == -1:
                                        break
                                    
                                    label = self.label_class(
                                        uuid=uuid.uuid4(),
                                        example_uuid=row_dict[UUID_COLUMN],
                                        label=col_name, # HEADER AS LABEL
                                        start_offset=start,
                                        end_offset=start + len(val_str)
                                    )
                                    labels.append(label)
                                    print(f"Fallback success: {label.label} at {label.start_offset}")
                                    search_start = start + 1
                        except Exception as e:
                            print(f"Fallback error: {e}")

        return labels

# Test Case
valid_uuid = uuid.uuid4()
df = pd.DataFrame({
    'Disease': ['Pneumonia'],
    'ICD-10': ['J12.0'],
    'uuid': [valid_uuid],
    'merged_text': ['Pneumonia (J12.0) and J12.0 again']
})

maker = LabelMaker(column="Disease, ICD-10", label_class=SpanLabel, text_column="merged_text")
labels = maker.make(df)

print(f"Created {len(labels)} labels")
for l in labels:
    print(f"Label: {l.label}, Span: {l.start_offset}-{l.end_offset}")
