# Change Log

## [2.13] - 2026-02-13

### Frontend Visual Optimization (Localized Previews & Login Page)
- **Login Page Refactor**:
    - **Tech Purple/Blue Gradient**: Updated background to a professional gradient (`#363795` to `#005C97`).
    - **Brand Identity**: Added "Doccano 默联数据标注平台" title and logo for better branding.
    - **Card Layout**: Enhanced login form with a centered, elevated card design.
- **Localized Project Previews**:
    - **Dynamic Components**: Replaced static English images with `TaskPreview.vue` showing interactive Chinese examples.
    - **Scenario Demos**:
        - **Text Classification**: Chinese sentiment analysis (Positive/Negative).
        - **Sequence Labeling**: Entity recognition (Person/Location/Company).
        - **Seq2seq**: Translation (English to Chinese).
        - **Intent Detection**: Ticket booking intent with slot filling.
        - **Knowledge Correction**: Typo correction example.
    - **UI Details**: Added simulated window controls (Red/Yellow/Green dots) for a polished look.

### Code Quality
- **ESLint Fixes**: Resolved `max-len` and self-closing tag errors in `TaskPreview.vue` to comply with linting rules.

## [2.12] - 2026-02-12

### Import Logic Correction (Remote Sync & Local Fixes)
- **Column Recognition Strategy**:
    - **Default Behavior**: Selects **ALL Columns** as **Label Columns** (Headers = Label Types).
    - **Text Column**: Selects **ALL Columns** as **Text Columns** (Rows = Text Content).
    - **Rationale**: Supports users who want to import a file where the header row defines the label set, and all subsequent rows contain text data that needs to be annotated with those labels.

### Features (Synced from Remote)
- **Auto-Label Creation (Backend)**: 
    - **Binary/Indicator Columns**: Implemented logic to handle columns containing binary values (0/1, True/False).
    - **Automatic Tagging**: When such columns are imported, the system now automatically creates a label using the **Header Name** for any row marked as True/1. This allows for importing datasets with pre-existing multi-label annotations without manual label creation.
    - **Column Headers as Label Types (Sequence Labeling)**:
        - **Logic**: For Sequence Labeling projects, selecting columns as "Label" will now automatically add the **Column Headers** as available **Label Types** in the project.
        - **Behavior**: **No automatic span annotations** are created on the text. This allows users to quickly import a list of desired labels defined in the file header without pre-annotating the data.

### UI/UX Improvements (Localization & Layout)
- **Localization (Han-hua 汉化)**:
    - **Delete Confirmation**: Localized "Yes"/"Cancel" buttons in the delete confirmation dialog to "是"/"取消".
    - **Search Placeholder**: Localized search bar hint from `(e.g. label:positive)` to `(例如: label:positive)`.
    - **Import/Export Examples**: Updated default example files (CSV, JSON, JSONL, TXT) to use Chinese content (e.g., "糟糕的客户服务") instead of English, improving user experience for Chinese users.
    - **Document List Status**:
        - Header: `Status` -> `状态`
        - Content: `in progress` -> `待处理`, `finished` -> `已处理`
- **Layout Adjustments**:
    - **Button Styling**:
        - Renamed `Edit` button to `编辑`.
        - **Vertical Spacing**: Increased vertical margin between `编辑` (Edit) and `标注` (Annotate) buttons for better clickability.

### Sync & Merge
- **Codebase Sync**: Successfully synchronized with the remote repository, incorporating backend updates for automatic label creation and improved import defaults.
- **Conflict Resolution**: Merged local UI enhancements with remote backend changes.
