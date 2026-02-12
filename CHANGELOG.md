# Change Log

## [2.12] - 2026-02-12

### Import Logic Correction
- **Default Column Selection**: 
    - **Text Column**: Defaults to the **First Column** (Index 0) if no specific alias is found.
    - **Label Columns**: Defaults to **All Other Columns** (Index 1..N).
    - This ensures that in multi-column files (e.g., `Text, Label1, Label2`), the first column is treated as the text content, and all subsequent columns are treated as potential labels.

### Sync & Merge
- **Codebase Sync**: Successfully synchronized with the remote repository, incorporating backend updates (Roles & Projects modules) from the team.
- **Conflict Resolution**: Merged local UI enhancements with remote backend changes.

### UI/UX Improvements (Localization & Layout)
- **Document List**:
    - **Localization**: Fully localized the "Status" column.
        - Header: `Status` -> `状态`
        - Content: `in progress` -> `待处理`, `finished` -> `已处理`
    - **Button Styling**:
        - Renamed `Edit` button to `编辑`.
        - **Vertical Spacing**: Increased vertical margin between `编辑` (Edit) and `标注` (Annotate) buttons for better clickability (added `mb-4` class).

### Features
- **Auto-Label Creation (Import)**: Implemented automatic label creation from binary/indicator columns.
    - If a user imports a column (e.g., "Sports") containing only binary values (0/1, True/False), the system now automatically creates a label named "Sports" for rows marked as True.
