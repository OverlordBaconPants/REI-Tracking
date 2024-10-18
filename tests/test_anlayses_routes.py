import pytest
from flask import json
from app import create_app
from models import User
from config import Config
import os
import io
import time
import csv
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_create_analysis_get(client):
    response = client.get('/create_analysis')
    assert response.status_code == 200
    assert b'create_analysis.html' in response.data

def test_create_analysis_post_long_term_rental(client):
    data = {
        "analysis_name": "Test Long-Term Rental",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "hoa_coa_coop": "50",
        "renovation_costs": "5000",
        "renovation_duration": "2",
        "loans": [
            {
                "name": "Primary Mortgage",
                "amount": "200000",
                "interest_rate": "3.5",
                "term": "360",
                "down_payment": "40000",
                "closing_costs": "3000"
            }
        ]
    }
    response = client.post('/create_analysis', 
                           data=json.dumps(data),
                           content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True
    assert 'analysis' in result

def test_create_analysis_post_brrrr(client):
    data = {
        "analysis_name": "Test BRRRR",
        "analysis_type": "BRRRR",
        "purchase_price": "150000",
        "renovation_costs": "30000",
        "renovation_duration": "3",
        "after_repair_value": "220000",
        "initial_loan_amount": "120000",
        "initial_interest_rate": "4",
        "initial_loan_term": "360",
        "initial_closing_costs": "3000",
        "refinance_loan_amount": "176000",
        "refinance_interest_rate": "3.5",
        "refinance_loan_term": "360",
        "refinance_closing_costs": "3500",
        "monthly_rent": "2000",
        "property_taxes": "200",
        "insurance": "100",
        "maintenance_percentage": "5",
        "vacancy_percentage": "5",
        "capex_percentage": "5",
        "management_percentage": "10"
    }
    response = client.post('/create_analysis', 
                           data=json.dumps(data),
                           content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True
    assert 'analysis' in result

def test_create_analysis_missing_field(client):
    data = {
        "analysis_name": "Test Missing Field",
        "analysis_type": "Long-Term Rental"
        # Missing required fields
    }
    response = client.post('/create_analysis', 
                           data=json.dumps(data),
                           content_type='application/json')
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Missing required field' in result['message']

def test_get_analysis(client):
    # First create an analysis
    data = {
        "analysis_name": "Test Get Analysis",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "hoa_coa_coop": "50",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now try to get the analysis
    get_response = client.get(f'/get_analysis/{analysis_id}')
    assert get_response.status_code == 200
    get_result = json.loads(get_response.data)
    assert get_result['success'] == True
    assert get_result['analysis']['analysis_name'] == "Test Get Analysis"

def test_get_nonexistent_analysis(client):
    response = client.get('/get_analysis/nonexistent_id')
    assert response.status_code == 404
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Analysis not found' in result['message']

def test_view_edit_analysis(client):
    response = client.get('/view_edit_analysis')
    assert response.status_code == 200
    assert b'view_edit_analysis.html' in response.data

def test_update_analysis(client):
    # First create an analysis
    data = {
        "analysis_name": "Test Update Analysis",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "hoa_coa_coop": "50",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now update the analysis
    update_data = create_result['analysis']
    update_data['monthly_income'] = "2500"
    update_response = client.post('/update_analysis',
                                  data=json.dumps(update_data),
                                  content_type='application/json')
    assert update_response.status_code == 200
    update_result = json.loads(update_response.data)
    assert update_result['success'] == True
    assert update_result['analysis']['monthly_income'] == "2500"

def test_generate_pdf(client):
    # First create an analysis
    data = {
        "analysis_name": "Test PDF Generation",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "hoa_coa_coop": "50",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now generate PDF
    pdf_response = client.get(f'/generate_pdf/{analysis_id}')
    assert pdf_response.status_code == 200
    assert pdf_response.mimetype == 'application/pdf'

def test_generate_pdf_nonexistent_analysis(client):
    response = client.get('/generate_pdf/nonexistent_id')
    assert response.status_code == 404
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Analysis not found' in result['message']

def authenticated_client(client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/login', data={'username': 'testuser', 'password': 'password123'})
    assert response.status_code == 302  # Assuming redirect after successful login
    return client

def test_create_analysis_requires_auth(client):
    response = client.get('/create_analysis')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']

def test_create_analysis_invalid_data(authenticated_client):
    data = {
        "analysis_name": "Invalid Data Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "not a number",
        "management_percentage": "-5",
        "capex_percentage": "150",
        "property_taxes": "-200",
        "insurance": "1e10",
        "renovation_costs": "-5000",
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Invalid input' in result['message']

def test_create_analysis_max_length(authenticated_client):
    data = {
        "analysis_name": "A" * 256,  # Assuming 255 is max length
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'exceeds maximum length' in result['message']

def test_create_analysis_boundary_values(authenticated_client):
    data = {
        "analysis_name": "Boundary Value Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "0",
        "management_percentage": "0",
        "capex_percentage": "100",
        "repairs_percentage": "0",
        "vacancy_percentage": "100",
        "property_taxes": "0",
        "insurance": "0",
        "renovation_costs": "0",
        "renovation_duration": "0"
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True

def test_update_analysis_switch_type(authenticated_client):
    # First create a Long-Term Rental analysis
    ltr_data = {
        "analysis_name": "Switch Type Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(ltr_data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now update to BRRRR
    brrrr_data = {
        "id": analysis_id,
        "analysis_name": "Switch Type Test",
        "analysis_type": "BRRRR",
        "purchase_price": "150000",
        "renovation_costs": "30000",
        "after_repair_value": "220000",
        "initial_loan_amount": "120000",
        "initial_interest_rate": "4",
        "initial_loan_term": "360",
        "refinance_loan_amount": "176000",
        "refinance_interest_rate": "3.5",
        "refinance_loan_term": "360",
        "monthly_rent": "2000",
        "property_taxes": "200",
        "insurance": "100",
        "maintenance_percentage": "5",
        "vacancy_percentage": "5",
        "capex_percentage": "5",
        "management_percentage": "10"
    }
    update_response = authenticated_client.post('/update_analysis',
                                                data=json.dumps(brrrr_data),
                                                content_type='application/json')
    assert update_response.status_code == 200
    update_result = json.loads(update_response.data)
    assert update_result['success'] == True
    assert update_result['analysis']['analysis_type'] == "BRRRR"

def test_create_analysis_multiple_loans(authenticated_client):
    data = {
        "analysis_name": "Multiple Loans Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2",
        "loans": [
            {
                "name": "Primary Mortgage",
                "amount": "200000",
                "interest_rate": "3.5",
                "term": "360",
                "down_payment": "40000",
                "closing_costs": "3000"
            },
            {
                "name": "HELOC",
                "amount": "50000",
                "interest_rate": "5.0",
                "term": "180",
                "down_payment": "0",
                "closing_costs": "500"
            }
        ]
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True
    assert len(result['analysis']['loans']) == 2

def test_generate_pdf_content(authenticated_client):
    # First create an analysis
    data = {
        "analysis_name": "PDF Content Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now generate PDF
    pdf_response = authenticated_client.get(f'/generate_pdf/{analysis_id}')
    assert pdf_response.status_code == 200
    assert pdf_response.mimetype == 'application/pdf'
    
    # Check PDF content (this is a basic check, you might want to use a PDF parsing library for more thorough checks)
    pdf_content = pdf_response.data.decode('latin-1')
    assert 'PDF Content Test' in pdf_content
    assert 'Long-Term Rental' in pdf_content
    assert '2000' in pdf_content  # monthly income

def test_list_analyses(authenticated_client):
    # Create a few analyses
    for i in range(3):
        data = {
            "analysis_name": f"List Test {i}",
            "analysis_type": "Long-Term Rental",
            "monthly_income": "2000",
            "management_percentage": "10",
            "capex_percentage": "5",
            "repairs_percentage": "5",
            "vacancy_percentage": "5",
            "property_taxes": "200",
            "insurance": "100",
            "renovation_costs": "5000",
            "renovation_duration": "2"
        }
        authenticated_client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')

    # Now list analyses
    response = authenticated_client.get('/view_edit_analysis')
    assert response.status_code == 200
    assert b'List Test 0' in response.data
    assert b'List Test 1' in response.data
    assert b'List Test 2' in response.data

def test_csrf_protection(authenticated_client):
    data = {
        "analysis_name": "CSRF Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    
    # Attempt to create analysis without CSRF token
    headers = Headers()
    headers.add('Content-Type', 'application/json')
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         headers=headers)
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'CSRF' in result['message']

def test_performance_create_multiple_analyses(authenticated_client):
    start_time = time.time()
    num_analyses = 50  # Adjust based on your performance requirements

    for i in range(num_analyses):
        data = {
            "analysis_name": f"Performance Test {i}",
            "analysis_type": "Long-Term Rental",
            "monthly_income": "2000",
            "management_percentage": "10",
            "capex_percentage": "5",
            "repairs_percentage": "5",
            "vacancy_percentage": "5",
            "property_taxes": "200",
            "insurance": "100",
            "renovation_costs": "5000",
            "renovation_duration": "2"
        }
        response = authenticated_client.post('/create_analysis', 
                                             data=json.dumps(data),
                                             content_type='application/json')
        assert response.status_code == 200

    end_time = time.time()
    total_time = end_time - start_time
    assert total_time < 10  # Assuming less than 10 seconds is acceptable

def test_concurrency_create_analyses(authenticated_client):
    num_concurrent = 10  # Number of concurrent requests

    def create_analysis(i):
        data = {
            "analysis_name": f"Concurrency Test {i}",
            "analysis_type": "Long-Term Rental",
            "monthly_income": "2000",
            "management_percentage": "10",
            "capex_percentage": "5",
            "repairs_percentage": "5",
            "vacancy_percentage": "5",
            "property_taxes": "200",
            "insurance": "100",
            "renovation_costs": "5000",
            "renovation_duration": "2"
        }
        response = authenticated_client.post('/create_analysis', 
                                             data=json.dumps(data),
                                             content_type='application/json')
        return response.status_code

    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        future_to_analysis = {executor.submit(create_analysis, i): i for i in range(num_concurrent)}
        for future in as_completed(future_to_analysis):
            assert future.result() == 200

def test_error_handling_corrupted_file(authenticated_client, monkeypatch):
    def mock_open(*args, **kwargs):
        raise IOError("Simulated file corruption")

    # Create an analysis first
    data = {
        "analysis_name": "Corrupted File Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now try to get the analysis with a mocked corrupted file
    monkeypatch.setattr('builtins.open', mock_open)
    response = authenticated_client.get(f'/get_analysis/{analysis_id}')
    assert response.status_code == 500
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Error reading analysis file' in result['message']

def test_create_analysis_with_special_characters(authenticated_client):
    data = {
        "analysis_name": "Special Ch@r Test!",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True
    assert result['analysis']['analysis_name'] == "Special Ch@r Test!"

def test_update_nonexistent_analysis(authenticated_client):
    update_data = {
        "id": "nonexistent_id",
        "analysis_name": "Nonexistent Analysis",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2500",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    response = authenticated_client.post('/update_analysis',
                                         data=json.dumps(update_data),
                                         content_type='application/json')
    assert response.status_code == 404
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Analysis not found' in result['message']

@pytest.mark.parametrize("field,value", [
    ("monthly_income", ""),
    ("management_percentage", "101"),
    ("capex_percentage", "-1"),
    ("repairs_percentage", "not_a_number"),
    ("vacancy_percentage", "50.5"),
    ("property_taxes", "-100"),
    ("insurance", "1e10"),
    ("renovation_costs", "-5000"),
    ("renovation_duration", "0"),
])
def test_create_analysis_invalid_fields(authenticated_client, field, value):
    data = {
        "analysis_name": "Invalid Field Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    data[field] = value
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 400
    result = json.loads(response.data)
    assert result['success'] == False
    assert 'Invalid input' in result['message']

def test_create_duplicate_analysis_name(authenticated_client):
    data = {
        "analysis_name": "Duplicate Name Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    # Create first analysis
    response1 = authenticated_client.post('/create_analysis', 
                                          data=json.dumps(data),
                                          content_type='application/json')
    assert response1.status_code == 200

    # Attempt to create second analysis with same name
    response2 = authenticated_client.post('/create_analysis', 
                                          data=json.dumps(data),
                                          content_type='application/json')
    assert response2.status_code == 400
    result = json.loads(response2.data)
    assert result['success'] == False
    assert 'Analysis name already exists' in result['message']

def test_generate_pdf_nonexistent_logo(authenticated_client, monkeypatch):
    # Mock the logo path to a non-existent file
    monkeypatch.setattr('os.path.exists', lambda x: False if 'logo.png' in x else True)

    # Create an analysis
    data = {
        "analysis_name": "Missing Logo Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Try to generate PDF
    pdf_response = authenticated_client.get(f'/generate_pdf/{analysis_id}')
    assert pdf_response.status_code == 500
    result = json.loads(pdf_response.data)
    assert result['success'] == False
    assert 'Error generating PDF' in result['message']

def test_export_analysis_to_csv(authenticated_client):
    # First create an analysis
    data = {
        "analysis_name": "CSV Export Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now export to CSV
    export_response = authenticated_client.get(f'/export_analysis/{analysis_id}/csv')
    assert export_response.status_code == 200
    assert export_response.mimetype == 'text/csv'
    
    # Check CSV content
    csv_content = export_response.data.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(csv_content))
    headers = next(csv_reader)
    assert 'analysis_name' in headers
    assert 'monthly_income' in headers
    first_row = next(csv_reader)
    assert 'CSV Export Test' in first_row
    assert '2000' in first_row

def test_duplicate_analysis(authenticated_client):
    # First create an analysis
    data = {
        "analysis_name": "Original Analysis",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    original_id = create_result['analysis']['id']

    # Now duplicate the analysis
    duplicate_response = authenticated_client.post(f'/duplicate_analysis/{original_id}')
    assert duplicate_response.status_code == 200
    duplicate_result = json.loads(duplicate_response.data)
    assert duplicate_result['success'] == True
    assert duplicate_result['analysis']['analysis_name'] == "Copy of Original Analysis"
    assert duplicate_result['analysis']['id'] != original_id

def test_pagination_list_analyses(authenticated_client):
    # Create 25 analyses
    for i in range(25):
        data = {
            "analysis_name": f"Pagination Test {i}",
            "analysis_type": "Long-Term Rental",
            "monthly_income": "2000",
            "management_percentage": "10",
            "capex_percentage": "5",
            "repairs_percentage": "5",
            "vacancy_percentage": "5",
            "property_taxes": "200",
            "insurance": "100",
            "renovation_costs": "5000",
            "renovation_duration": "2"
        }
        authenticated_client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')

    # Test first page
    response = authenticated_client.get('/list_analyses?page=1&per_page=10')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert len(result['analyses']) == 10
    assert result['total'] == 25
    assert result['pages'] == 3
    assert 'Pagination Test 0' in [a['analysis_name'] for a in result['analyses']]

    # Test last page
    response = authenticated_client.get('/list_analyses?page=3&per_page=10')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert len(result['analyses']) == 5

def test_search_analyses(authenticated_client):
    # Create some analyses with different names
    analyses = [
        "Rental Property A",
        "BRRRR Strategy B",
        "Long-Term Investment C",
        "Short-Term Rental D"
    ]
    for analysis_name in analyses:
        data = {
            "analysis_name": analysis_name,
            "analysis_type": "Long-Term Rental",
            "monthly_income": "2000",
            "management_percentage": "10",
            "capex_percentage": "5",
            "repairs_percentage": "5",
            "vacancy_percentage": "5",
            "property_taxes": "200",
            "insurance": "100",
            "renovation_costs": "5000",
            "renovation_duration": "2"
        }
        authenticated_client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')

    # Test search functionality
    response = authenticated_client.get('/search_analyses?query=Rental')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert len(result['analyses']) == 2
    assert 'Rental Property A' in [a['analysis_name'] for a in result['analyses']]
    assert 'Short-Term Rental D' in [a['analysis_name'] for a in result['analyses']]

def test_filter_analyses_by_type(authenticated_client):
    # Create analyses of different types
    types = ["Long-Term Rental", "BRRRR", "Short-Term Rental"]
    for analysis_type in types:
        data = {
            "analysis_name": f"Filter Test - {analysis_type}",
            "analysis_type": analysis_type,
            "monthly_income": "2000",
            "management_percentage": "10",
            "capex_percentage": "5",
            "repairs_percentage": "5",
            "vacancy_percentage": "5",
            "property_taxes": "200",
            "insurance": "100",
            "renovation_costs": "5000",
            "renovation_duration": "2"
        }
        authenticated_client.post('/create_analysis', 
                                  data=json.dumps(data),
                                  content_type='application/json')

    # Test filter functionality
    response = authenticated_client.get('/list_analyses?type=BRRRR')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert len(result['analyses']) == 1
    assert result['analyses'][0]['analysis_type'] == 'BRRRR'

def test_create_analysis_with_very_large_numbers(authenticated_client):
    data = {
        "analysis_name": "Large Numbers Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "999999999999",  # Very large number
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "999999999999",  # Very large number
        "insurance": "999999999999",  # Very large number
        "renovation_costs": "999999999999",  # Very large number
        "renovation_duration": "2"
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True
    assert math.isclose(float(result['analysis']['monthly_income'].replace('$', '').replace(',', '')), 999999999999, rel_tol=1e-9)

def test_create_analysis_with_zero_values(authenticated_client):
    data = {
        "analysis_name": "Zero Values Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "0",
        "management_percentage": "0",
        "capex_percentage": "0",
        "repairs_percentage": "0",
        "vacancy_percentage": "0",
        "property_taxes": "0",
        "insurance": "0",
        "renovation_costs": "0",
        "renovation_duration": "0"
    }
    response = authenticated_client.post('/create_analysis', 
                                         data=json.dumps(data),
                                         content_type='application/json')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['success'] == True
    assert result['analysis']['monthly_income'] == '$0.00'
    assert float(result['analysis']['cash_on_cash_return'].rstrip('%')) == 0

def test_update_analysis_partial_data(authenticated_client):
    # First create an analysis
    data = {
        "analysis_name": "Partial Update Test",
        "analysis_type": "Long-Term Rental",
        "monthly_income": "2000",
        "management_percentage": "10",
        "capex_percentage": "5",
        "repairs_percentage": "5",
        "vacancy_percentage": "5",
        "property_taxes": "200",
        "insurance": "100",
        "renovation_costs": "5000",
        "renovation_duration": "2"
    }
    create_response = authenticated_client.post('/create_analysis', 
                                                data=json.dumps(data),
                                                content_type='application/json')
    create_result = json.loads(create_response.data)
    analysis_id = create_result['analysis']['id']

    # Now update only some fields
    update_data = {
        "id": analysis_id,
        "monthly_income": "2500",
        "management_percentage": "12"
    }
    update_response = authenticated_client.post('/update_analysis',
                                                data=json.dumps(update_data),
                                                content_type='application/json')
    assert update_response.status_code == 200
    update_result = json.loads(update_response.data)
    assert update_result['success'] == True
    assert update_result['analysis']['monthly_income'] == '$2,500.00'
    assert update_result['analysis']['management_percentage'] == '12'
    # Check that other fields remained unchanged
    assert update_result['analysis']['capex_percentage'] == '5'