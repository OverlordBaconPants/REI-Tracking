# Transaction File Extraction System

This document outlines the implementation plan for the new "Extract Transaction from File" feature as a series of atomic, testable changes. Each implementation represents a single deployment unit that can be individually developed, tested, and committed to GitHub.

## Feature Overview

This feature allows users to upload a document (receipt, invoice, etc.) and automatically extract transaction data:

1. User selects "Add Transaction from File" from the navbar or Quick Links card
2. User uploads a file (PDF, image) via drag-and-drop or file browser
3. System extracts transaction data (amount, date, property, etc.)
4. User reviews extracted data in a preview screen
5. System populates the Add Transaction form with the extracted data
6. User completes the transaction using the normal workflow

## Implementation Plan

The feature will be implemented in 10 atomic deployments, each building on the previous one:

---

## Implementation 1: File Upload Page Setup

**Goal**: Create basic file upload page with routing and navigation links

**Tasks**:
- Create "Extract Transaction from File" route in `transactions_bp`
- Create basic `extract_from_file.html` template with page structure
- Add navigation links in navbar and Quick Links card
- Add route tests

**Files to Create/Modify**:
- `src/routes/transactions.py` - Add new route
- `templates/transactions/extract_from_file.html` - Create new template
- `templates/components/navbar.html` - Add navigation link
- `templates/dashboard/index.html` - Update Quick Links card
- `tests/test_routes/test_transactions.py` - Add route tests

**Testing**:
- Verify route returns 200 status code
- Confirm navigation links exist and point to correct URL
- Test page renders correctly

---

## Implementation 2: File Upload Component

**Goal**: Implement file upload functionality with drag-and-drop and file selection

**Tasks**:
- Create file upload component with drag-and-drop
- Implement file type validation (PDF, PNG, JPG, JPEG)
- Add file selection button
- Style upload area with feedback for drag events

**Files to Create/Modify**:
- `templates/transactions/extract_from_file.html` - Update with upload component
- `static/js/file_upload.js` - Create JS for drag-and-drop functionality
- `static/css/file_upload.css` - Add styling for upload component
- `src/utils/file_utils.py` - Extend file validation functions
- `tests/test_utils/test_file_utils.py` - Test file validation

**Testing**:
- Test file type validation for allowed and disallowed types
- Verify drag-and-drop functionality works
- Test file selection button works

---

## Implementation 3: Cancel and Processing Functionality

**Goal**: Add cancel button and processing overlay

**Tasks**:
- Implement cancel button functionality
- Add toastr notification for cancellation
- Create processing overlay with spinner
- Handle form submission for upload

**Files to Create/Modify**:
- `templates/transactions/extract_from_file.html` - Add cancel button and overlay
- `static/js/file_upload.js` - Add cancel and processing logic
- `src/routes/transactions.py` - Handle cancellation
- `tests/test_routes/test_transactions.py` - Test cancellation

**Testing**:
- Verify cancel button redirects correctly
- Test toastr notification appears on cancel
- Confirm processing overlay appears during upload

---

## Implementation 4: Text Extraction Service - Base

**Goal**: Create base text extraction service for processing uploaded files

**Tasks**:
- Create TextExtractionService class
- Implement file type detection
- Create logging and error handling framework
- Setup basic interface for extraction methods

**Files to Create/Modify**:
- `src/services/extraction_service.py` - Create new service file
- `tests/test_services/test_extraction_service.py` - Add unit tests
- `requirements.txt` - Add any new dependencies

**Testing**:
- Test file type detection for various file types
- Verify logging works correctly
- Test error handling with invalid files

---

## Implementation 5: Text Extraction Service - PDF and Image Support

**Goal**: Implement text extraction from PDFs and images

**Tasks**:
- Add PDF text extraction using PyPDF2 or pdfplumber
- Implement image OCR using Tesseract
- Add image preprocessing for better OCR results
- Create fallback handling for extraction failures

**Files to Create/Modify**:
- `src/services/extraction_service.py` - Update with extraction implementations
- `tests/test_services/test_extraction_service.py` - Add tests with sample files
- `requirements.txt` - Add OCR dependencies
- `config.py` - Add OCR configuration options

**Testing**:
- Test PDF extraction with sample files
- Verify image OCR works with various image qualities
- Test handling of multi-page PDFs
- Confirm error handling for corrupt files

---

## Implementation 6: Transaction Data Extraction - Amount and Date

**Goal**: Implement extraction of amount and date information

**Tasks**:
- Create TransactionExtractionService class
- Implement amount extraction with pattern matching
- Add date extraction with format detection
- Create unit tests with various sample texts

**Files to Create/Modify**:
- `src/services/transaction_extraction_service.py` - Create new service
- `src/utils/extraction_patterns.py` - Define regex patterns
- `tests/test_services/test_transaction_extraction.py` - Add unit tests
- `tests/fixtures/extraction_samples.py` - Create test fixtures

**Testing**:
- Test amount extraction with various formats ($100.00, 100.00, etc.)
- Verify date extraction with different formats (MM/DD/YYYY, etc.)
- Test prioritization of amounts (total vs subtotal)
- Confirm handling of multiple dates (choose most recent)

---

## Implementation 7: Transaction Data Extraction - Property and Category

**Goal**: Implement property matching and transaction categorization

**Tasks**:
- Add property address matching functionality
- Implement transaction type detection (income/expense)
- Create category matching based on keywords
- Add vendor/payer extraction

**Files to Create/Modify**:
- `src/services/transaction_extraction_service.py` - Update service
- `src/utils/extraction_patterns.py` - Add property and category patterns
- `tests/test_services/test_transaction_extraction.py` - Expand unit tests
- `config.py` - Add category keyword mappings

**Testing**:
- Test property matching with exact and partial addresses
- Verify transaction type detection accuracy
- Test category assignment for common vendors
- Confirm vendor/payer extraction works correctly

---

## Implementation 8: Extraction Preview Interface

**Goal**: Create preview page to display and edit extracted transaction data

**Tasks**:
- Create extraction results preview page
- Implement route to handle extraction preview
- Design UI for displaying extracted fields
- Add field editing functionality
- Create action buttons (Cancel, Add to Transaction)

**Files to Create/Modify**:
- `templates/transactions/preview_extraction.html` - Create new template
- `src/routes/transactions.py` - Add preview route
- `static/js/extraction_preview.js` - Add preview functionality
- `static/css/extraction_preview.css` - Style preview page
- `tests/test_routes/test_transactions.py` - Add preview route tests

**Testing**:
- Verify preview page displays all extracted fields
- Test editing functionality for each field
- Confirm navigation buttons work correctly
- Test handling of missing extraction data

---

## Implementation 9: Transaction Form Population

**Goal**: Implement automatic population of the Add Transaction form

**Tasks**:
- Modify Add Transaction route to accept extracted data
- Implement form population from extraction results
- Add file attachment from original uploaded document
- Create integration tests for full workflow

**Files to Create/Modify**:
- `src/routes/transactions.py` - Update Add Transaction route
- `templates/transactions/add_transaction.html` - Update form
- `static/js/transaction_form.js` - Add population logic
- `tests/test_integration/test_extraction_workflow.py` - Create integration tests

**Testing**:
- Test end-to-end workflow from extraction to form population
- Verify all fields are correctly populated
- Confirm file attachment works
- Test with various document types

---

## Implementation 10: Configuration System and Documentation

**Goal**: Add configuration options and complete documentation

**Tasks**:
- Create configurable extraction settings
- Define vendor patterns and category mappings
- Update README.md with feature documentation
- Add help text and user guidance

**Files to Create/Modify**:
- `src/utils/extraction_config.py` - Create configuration file
- `config.py` - Add extraction settings
- `README.md` - Update with feature documentation
- `templates/help/extraction.html` - Add help documentation

**Testing**:
- Verify configuration options work correctly
- Test customized vendor patterns
- Confirm documentation is accurate and complete

---

## Testing Strategy for Each Implementation

### Unit Tests

For each implementation, create dedicated unit tests that:
- Test the specific functionality being added
- Verify integration with existing components
- Include positive and negative test cases
- Test edge cases specific to the implementation

### Integration Tests

After multiple implementations are completed:
- Create integration tests that verify workflow across components
- Test end-to-end user journeys
- Verify error handling and recovery

### UI Tests

For implementations with significant UI components:
- Test responsive design on different screen sizes
- Verify accessibility features
- Test with keyboard navigation

---

## Required Libraries and Dependencies

- **PyPDF2 or pdfplumber**: For PDF text extraction
- **pytesseract**: Python wrapper for Tesseract OCR
- **Pillow**: For image processing and manipulation
- **regex**: For enhanced regular expression support
- **Flask-WTF**: For form handling and validation

## Appendix: Example Extraction Patterns

### Amount Extraction Patterns

```python
AMOUNT_PATTERNS = [
    r'total:?\s*\$?(\d{1,3}(,\d{3})*(\.\d{2})?)',
    r'amount\s*due:?\s*\$?(\d{1,3}(,\d{3})*(\.\d{2})?)',
    r'balance:?\s*\$?(\d{1,3}(,\d{3})*(\.\d{2})?)',
    r'payment:?\s*\$?(\d{1,3}(,\d{3})*(\.\d{2})?)',
    r'\$(\d{1,3}(,\d{3})*(\.\d{2})?)'
]
```

### Date Extraction Patterns

```python
DATE_PATTERNS = [
    r'(\d{1,2})\/(\d{1,2})\/(\d{4})',  # MM/DD/YYYY or DD/MM/YYYY
    r'(\d{1,2})-(\d{1,2})-(\d{4})',     # MM-DD-YYYY or DD-MM-YYYY
    r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{1,2}),? (\d{4})'  # Month DD, YYYY
]
```

### Category Keywords

```python
CATEGORY_KEYWORDS = {
    'Mortgage': ['mortgage', 'loan payment', 'home loan'],
    'Insurance': ['insurance', 'policy', 'coverage'],
    'Utilities': ['utility', 'electric', 'gas', 'water', 'sewer'],
    'Repairs': ['repair', 'fix', 'maintenance', 'service'],
    'Property Tax': ['property tax', 'tax bill', 'assessment']
}
```
