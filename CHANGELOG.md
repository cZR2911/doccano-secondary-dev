# Change Log

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
