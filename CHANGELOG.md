# Change Log

## [2.12] - 2026-02-12

### Import Logic Correction (Remote Sync & Local Fixes)
- **Column Recognition Strategy**:
    - **Text Column**: Defaults to the **First Column** (Index 0).
    - **Label Columns**: Defaults to **All Other Columns** (Index 1..N).
    - **Behavior Change**: Previously, the system might have defaulted to the last column for labels or required manual selection. Now, for a file with structure `[Text, Tag1, Tag2, Tag3]`, it automatically selects `Text` as the content and `Tag1, Tag2, Tag3` as labels.

### Features (Synced from Remote)
- **Auto-Label Creation (Backend)**: 
    - **Binary/Indicator Columns**: Implemented logic to handle columns containing binary values (0/1, True/False).
    - **Automatic Tagging**: When such columns are imported, the system now automatically creates a label using the **Header Name** for any row marked as True/1. This allows for importing datasets with pre-existing multi-label annotations without manual label creation.

### UI/UX Improvements (Localization & Layout)
- **Document List**:
    - **Localization**: Fully localized the "Status" column.
        - Header: `Status` -> `状态`
        - Content: `in progress` -> `待处理`, `finished` -> `已处理`
    - **Button Styling**:
        - Renamed `Edit` button to `编辑`.
        - **Vertical Spacing**: Increased vertical margin between `编辑` (Edit) and `标注` (Annotate) buttons for better clickability (added `mb-4` class).

### Sync & Merge
- **Codebase Sync**: Successfully synchronized with the remote repository (commits `d9faf29c`, `d6239dc1`), incorporating backend updates for automatic label creation and improved import defaults.
- **Conflict Resolution**: Merged local UI enhancements with remote backend changes.
