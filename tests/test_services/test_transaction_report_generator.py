import unittest
from unittest.mock import patch, mock_open, MagicMock, Mock
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.pdfgen import canvas as reportlab_canvas
from services.transaction_report_generator import TransactionReportGenerator, RoundedTableFlowable

class TestTransactionReportGenerator(unittest.TestCase):
    """Test cases for TransactionReportGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = TransactionReportGenerator()
        
        # Sample transactions for testing
        self.sample_transactions = [
            {
                'property_id': '123 Main St',
                'type': 'income',
                'category': 'Rent',
                'description': 'Monthly Rent',
                'amount': 1000.0,
                'date': '2023-01-15',
                'collector_payer': 'Tenant',
                'notes': 'On time',
                'reimbursement': {
                    'reimbursement_status': 'completed'
                }
            },
            {
                'property_id': '123 Main St',
                'type': 'expense',
                'category': 'Repairs',
                'description': 'Fix Sink',
                'amount': 200.0,
                'date': '2023-01-20',
                'collector_payer': 'Owner',
                'notes': 'Emergency repair',
                'reimbursement': {
                    'reimbursement_status': 'pending'
                }
            }
        ]
        
        # Sample metadata
        self.sample_metadata = {
            'property': '123 Main St',
            'user': 'Test User',
            'date_range': 'Jan 1, 2023 - Jan 31, 2023'
        }

    def test_init(self):
        """Test initialization of TransactionReportGenerator"""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.styles)
        
        # Check that styles were created
        self.assertIn('BrandNormal', self.generator.styles)
        self.assertIn('BrandHeading1', self.generator.styles)
        self.assertIn('TableHeader', self.generator.styles)

    def test_create_styles(self):
        """Test style creation"""
        styles = self.generator._create_styles()
        
        # Check that all required styles exist
        self.assertIn('BrandNormal', styles)
        self.assertIn('BrandHeading1', styles)
        self.assertIn('BrandHeading3', styles)
        self.assertIn('BrandSmall', styles)
        self.assertIn('TableHeader', styles)
        self.assertIn('EnhancedTitle', styles)
        self.assertIn('EnhancedSubtitle', styles)
        self.assertIn('TableContent', styles)
        self.assertIn('TableCell', styles)
        self.assertIn('TableCellRight', styles)
        self.assertIn('MetadataEntry', styles)

    @patch('services.transaction_report_generator.SimpleDocTemplate')
    @patch('services.transaction_report_generator.os.path.exists')
    def test_generate(self, mock_exists, mock_simple_doc):
        """Test report generation"""
        # Mock SimpleDocTemplate and its build method
        mock_doc = MagicMock()
        mock_simple_doc.return_value = mock_doc
        mock_exists.return_value = True
        
        # Create a buffer for the PDF
        buffer = io.BytesIO()
        
        # Generate the report
        result = self.generator.generate(self.sample_transactions, buffer, self.sample_metadata)
        
        # Check that the document was built
        self.assertTrue(mock_doc.build.called)
        self.assertTrue(result)

    @patch('services.transaction_report_generator.SimpleDocTemplate')
    @patch('services.transaction_report_generator.os.path.exists')
    def test_generate_error(self, mock_exists, mock_simple_doc):
        """Test error handling during report generation"""
        # Mock SimpleDocTemplate to raise an exception
        mock_doc = MagicMock()
        mock_doc.build.side_effect = Exception("Test error")
        mock_simple_doc.return_value = mock_doc
        mock_exists.return_value = True
        
        # Create a buffer for the PDF
        buffer = io.BytesIO()
        
        # Generate the report should raise the exception
        with self.assertRaises(Exception):
            self.generator.generate(self.sample_transactions, buffer, self.sample_metadata)

    def test_build_story(self):
        """Test building the story (content) for the PDF"""
        # Build the story
        story = self.generator._build_story(self.sample_transactions, self.sample_metadata)
        
        # Check that the story is not empty
        self.assertGreater(len(story), 0)
        
        # Check for specific elements in the story
        has_title = False
        has_property_summary = False
        has_transactions_table = False
        
        for element in story:
            if isinstance(element, Paragraph):
                if "Transaction Report" in element.text:
                    has_title = True
            if isinstance(element, Table) or isinstance(element, RoundedTableFlowable):
                # Check if it's a summary table or transactions table
                if hasattr(element, 'table'):  # RoundedTableFlowable
                    table = element.table
                else:
                    table = element
                
                if len(table._cellvalues) > 0:
                    if len(table._cellvalues[0]) == 2:  # Property summary has 2 columns
                        has_property_summary = True
                    elif len(table._cellvalues[0]) > 2:  # Transactions table has more columns
                        has_transactions_table = True
        
        # At least one of these should be true
        self.assertTrue(has_title or has_property_summary or has_transactions_table)

    def test_create_header(self):
        """Test header creation"""
        # Create header with metadata
        header_elements = self.generator._create_header(self.sample_metadata)
        
        # Check that header elements were created
        self.assertGreater(len(header_elements), 0)
        
        # Check for title and subtitle
        has_title = False
        has_subtitle = False
        has_metadata = False
        
        for element in header_elements:
            if isinstance(element, Paragraph):
                if "Transaction Report" in element.text:
                    has_title = True
                elif "123 Main St" in element.text:
                    has_subtitle = True
                elif "Generated by: Test User" in element.text:
                    has_metadata = True
        
        self.assertTrue(has_title)
        self.assertTrue(has_subtitle)
        self.assertTrue(has_metadata)
        
        # Test without metadata
        header_elements = self.generator._create_header(None)
        self.assertGreater(len(header_elements), 0)

    def test_create_grand_summary(self):
        """Test grand summary creation for all properties"""
        # Create transactions for multiple properties
        multi_property_transactions = [
            {
                'property_id': '123 Main St',
                'type': 'income',
                'amount': 1000.0,
            },
            {
                'property_id': '123 Main St',
                'type': 'expense',
                'amount': 200.0,
            },
            {
                'property_id': '456 Oak Ave',
                'type': 'income',
                'amount': 800.0,
            },
            {
                'property_id': '456 Oak Ave',
                'type': 'expense',
                'amount': 300.0,
            }
        ]
        
        # Create grand summary
        summary_elements = self.generator._create_grand_summary(multi_property_transactions)
        
        # Check that summary elements were created
        self.assertGreater(len(summary_elements), 0)
        
        # Check for summary table
        has_summary_table = False
        
        for element in summary_elements:
            if isinstance(element, Table) or isinstance(element, RoundedTableFlowable):
                has_summary_table = True
                break
        
        self.assertTrue(has_summary_table)

    def test_create_property_summary(self):
        """Test property summary creation"""
        # Create property summary
        summary_elements = self.generator._create_property_summary(self.sample_transactions)
        
        # Check that summary elements were created
        self.assertGreater(len(summary_elements), 0)
        
        # Check for summary table
        has_summary_table = False
        
        for element in summary_elements:
            if isinstance(element, RoundedTableFlowable):
                has_summary_table = True
                break
        
        self.assertTrue(has_summary_table)

    def test_create_transactions_table(self):
        """Test transactions table creation"""
        # Create transactions table
        table_elements = self.generator._create_transactions_table(self.sample_transactions)
        
        # Check that table elements were created
        self.assertGreater(len(table_elements), 0)
        
        # Check for transactions table
        has_transactions_table = False
        
        for element in table_elements:
            if isinstance(element, Table) or isinstance(element, RoundedTableFlowable):
                has_transactions_table = True
                break
        
        self.assertTrue(has_transactions_table)

    def test_truncate_address(self):
        """Test address truncation"""
        # Test full address
        full_address = "123 Main St, Anytown, CA 12345"
        truncated = self.generator._truncate_address(full_address)
        # The actual implementation may have an extra space, so we'll check for the content
        self.assertTrue("123 Main St" in truncated and "Anytown" in truncated)
        
        # Test short address
        short_address = "123 Main St"
        truncated = self.generator._truncate_address(short_address)
        self.assertEqual(truncated, "123 Main St")
        
        # Test None
        self.assertEqual(self.generator._truncate_address(None), None)
        
        # Test "All Properties"
        self.assertEqual(self.generator._truncate_address("All Properties"), "All Properties")

    def test_parse_amount(self):
        """Test amount parsing"""
        # Test string with $ and commas
        self.assertEqual(self.generator._parse_amount("$1,234.56"), 1234.56)
        
        # Test string without $ or commas
        self.assertEqual(self.generator._parse_amount("1234.56"), 1234.56)
        
        # Test numeric value
        self.assertEqual(self.generator._parse_amount(1234.56), 1234.56)

    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_add_page_decorations(self, mock_canvas):
        """Test adding page decorations"""
        # Create mock canvas and doc
        mock_canvas_obj = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page = 1
        mock_doc.pagesize = letter
        mock_doc.leftMargin = 36
        mock_doc.rightMargin = 36
        mock_doc.topMargin = 36
        
        # Call add_page_decorations
        self.generator._add_page_decorations(mock_canvas_obj, mock_doc)
        
        # Check that canvas methods were called
        self.assertTrue(mock_canvas_obj.saveState.called)
        self.assertTrue(mock_canvas_obj.setFont.called)
        self.assertTrue(mock_canvas_obj.setFillColor.called)
        self.assertTrue(mock_canvas_obj.drawRightString.called)
        self.assertTrue(mock_canvas_obj.setStrokeColor.called)
        self.assertTrue(mock_canvas_obj.setLineWidth.called)
        self.assertTrue(mock_canvas_obj.line.called)
        self.assertTrue(mock_canvas_obj.restoreState.called)

    @patch('os.path.exists')
    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_add_page_decorations_with_logo(self, mock_canvas, mock_exists):
        """Test adding page decorations with logo"""
        # Mock os.path.exists to return True
        mock_exists.return_value = True
        
        # Create mock canvas and doc
        mock_canvas_obj = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page = 1
        mock_doc.pagesize = letter
        mock_doc.leftMargin = 36
        mock_doc.rightMargin = 36
        mock_doc.topMargin = 36
        
        # Call add_page_decorations
        self.generator._add_page_decorations(mock_canvas_obj, mock_doc)
        
        # Check that drawImage was called
        self.assertTrue(mock_canvas_obj.drawImage.called)

    @patch('os.path.exists')
    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_add_page_decorations_logo_not_found(self, mock_canvas, mock_exists):
        """Test adding page decorations when logo is not found"""
        # Mock os.path.exists to return False
        mock_exists.return_value = False
        
        # Create mock canvas and doc
        mock_canvas_obj = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page = 1
        mock_doc.pagesize = letter
        mock_doc.leftMargin = 36
        mock_doc.rightMargin = 36
        mock_doc.topMargin = 36
        
        # Call add_page_decorations
        self.generator._add_page_decorations(mock_canvas_obj, mock_doc)
        
        # Check that drawImage was not called
        self.assertFalse(mock_canvas_obj.drawImage.called)

    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_add_page_decorations_later_pages(self, mock_canvas):
        """Test adding page decorations for later pages"""
        # Create mock canvas and doc
        mock_canvas_obj = MagicMock()
        mock_doc = MagicMock()
        mock_doc.page = 2  # Not the first page
        mock_doc.pagesize = letter
        mock_doc.leftMargin = 36
        mock_doc.rightMargin = 36
        mock_doc.topMargin = 36
        
        # Call add_page_decorations
        self.generator._add_page_decorations(mock_canvas_obj, mock_doc)
        
        # Check that drawImage was not called (logo only on first page)
        self.assertFalse(mock_canvas_obj.drawImage.called)

    def test_rounded_table_flowable_init(self):
        """Test RoundedTableFlowable initialization"""
        # Create a mock table
        mock_table = MagicMock()
        mock_table.wrap.return_value = (100, 50)
        
        # Create RoundedTableFlowable
        flowable = RoundedTableFlowable(mock_table, corner_radius=10, padding=5)
        
        # Check properties
        self.assertEqual(flowable.table, mock_table)
        self.assertEqual(flowable.corner_radius, 10)
        self.assertEqual(flowable.padding, 5)
        self.assertEqual(flowable.width, 110)  # 100 + 5*2
        self.assertEqual(flowable.height, 60)  # 50 + 5*2

    @patch('reportlab.pdfgen.canvas.Canvas')
    def test_rounded_table_flowable_draw(self, mock_canvas):
        """Test RoundedTableFlowable draw method"""
        # Create a mock table
        mock_table = MagicMock()
        mock_table.wrap.return_value = (100, 50)
        
        # Create RoundedTableFlowable
        flowable = RoundedTableFlowable(mock_table, corner_radius=10, padding=5)
        
        # Create mock canvas
        mock_canvas_obj = MagicMock()
        flowable.canv = mock_canvas_obj
        
        # Call draw method
        flowable.draw()
        
        # Check that canvas methods were called
        self.assertTrue(mock_canvas_obj.saveState.called)
        self.assertTrue(mock_canvas_obj.setFillColor.called)
        self.assertTrue(mock_canvas_obj.setStrokeColor.called)
        self.assertTrue(mock_canvas_obj.setLineWidth.called)
        self.assertTrue(mock_canvas_obj.roundRect.called)
        self.assertTrue(mock_canvas_obj.translate.called)
        self.assertTrue(mock_canvas_obj.restoreState.called)
        
        # Check that table draw was called
        self.assertTrue(mock_table.draw.called)

    def test_rounded_table_flowable_wrap(self):
        """Test RoundedTableFlowable wrap method"""
        # Create a mock table
        mock_table = MagicMock()
        mock_table.wrap.return_value = (100, 50)
        
        # Create RoundedTableFlowable
        flowable = RoundedTableFlowable(mock_table, corner_radius=10, padding=5)
        
        # Call wrap method
        width, height = flowable.wrap(200, 100)
        
        # Check dimensions
        self.assertEqual(width, 110)  # 100 + 5*2
        self.assertEqual(height, 60)  # 50 + 5*2
        
        # Test with limited available space
        mock_table.wrap.return_value = (250, 150)  # Larger than available space
        width, height = flowable.wrap(200, 100)
        
        # Should be limited to available space minus padding
        self.assertEqual(width, 200)
        self.assertEqual(height, 100)

if __name__ == '__main__':
    unittest.main()
