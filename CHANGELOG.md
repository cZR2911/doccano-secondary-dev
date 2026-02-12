# Change Log

## [2.12] - 2026-02-12

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

### Fixes
- **Import Logic**: Adjusted the "Force Strategy" for column recognition based on user feedback.
    - **Logic Change**: If no column matches known aliases, default the **First Column** as the **Label** and the **Second Column** as the **Text** (previously Label=Last, Text=First).

## [2.11] - 2026-02-11

### Added
- **Frontend (Import)**: Implemented automatic recognition of file headers as labels during dataset import.
    - Added alias matching for label columns (e.g., `label`, `tag`, `category`, `class`, `target`, `sentiment`, `intent`).
    - Added alias matching for text columns (e.g., `text`, `data`, `body`, `content`, `question`, `answer`, `review`).
    - Added partial string matching for column names.
    - Added "Force Strategy": Default to 1st column as Text and last column as Label if no match found.
- **Backend (Import)**: Synced column alias logic in `LabelMaker` to match frontend capabilities.

### Changed
- **Frontend (DocumentList)**: Increased vertical spacing between "Edit" and "Annotate" buttons for better usability.
