"""
Utility for generating random test data.
"""
import random
import uuid
from datetime import datetime, timedelta

class DataGenerator:
    """Utility for generating random test data."""
    
    @staticmethod
    def generate_property():
        """
        Generate random property data.
        
        Returns:
            dict: Random property data
        """
        property_id = str(uuid.uuid4())
        return {
            "id": property_id,
            "name": f"Test Property {uuid.uuid4().hex[:8]}",
            "address": {
                "street": f"{random.randint(100, 9999)} Main St",
                "city": "Anytown",
                "state": "CA",
                "zip": f"{random.randint(10000, 99999)}"
            },
            "purchase_price": random.randint(100000, 1000000),
            "purchase_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "bedrooms": random.randint(1, 5),
            "bathrooms": random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4]),
            "square_feet": random.randint(800, 3000)
        }
    
    @staticmethod
    def generate_transaction(property_id=None):
        """
        Generate random transaction data.
        
        Args:
            property_id: Optional property ID to associate with the transaction
            
        Returns:
            dict: Random transaction data
        """
        transaction_type = random.choice(["income", "expense"])
        categories = {
            "income": ["Rent", "Laundry", "Parking", "Other"],
            "expense": ["Mortgage", "Taxes", "Insurance", "Repairs", "Utilities", "Management"]
        }
        
        return {
            "id": str(uuid.uuid4()),
            "property_id": property_id or str(uuid.uuid4()),
            "date": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d"),
            "type": transaction_type,
            "category": random.choice(categories[transaction_type]),
            "amount": random.randint(100, 2000) if transaction_type == "expense" else random.randint(1000, 3000),
            "description": f"Test {transaction_type} - {uuid.uuid4().hex[:8]}"
        }
    
    @staticmethod
    def generate_user():
        """
        Generate random user data.
        
        Returns:
            dict: Random user data
        """
        first_name = random.choice(["John", "Jane", "Michael", "Sarah", "David", "Emily"])
        last_name = random.choice(["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis"])
        
        return {
            "id": str(uuid.uuid4()),
            "email": f"{first_name.lower()}.{last_name.lower()}_{uuid.uuid4().hex[:6]}@example.com",
            "password": f"Password{random.randint(100, 999)}!",
            "first_name": first_name,
            "last_name": last_name
        }
    
    @staticmethod
    def generate_analysis(property_id=None, analysis_type="LTR"):
        """
        Generate random analysis data.
        
        Args:
            property_id: Optional property ID to associate with the analysis
            analysis_type: Type of analysis (LTR, BRRRR, Lease Option, Multi-Family, PadSplit)
            
        Returns:
            dict: Random analysis data
        """
        property_id = property_id or str(uuid.uuid4())
        purchase_price = random.randint(100000, 1000000)
        
        base_analysis = {
            "id": str(uuid.uuid4()),
            "property_id": property_id,
            "analysis_type": analysis_type,
            "purchase_price": purchase_price,
            "monthly_rent": int(purchase_price * 0.01),  # 1% rule
            "property_taxes": int(purchase_price * 0.015 / 12),  # 1.5% annually
            "insurance": int(purchase_price * 0.005 / 12),  # 0.5% annually
            "vacancy_percentage": random.randint(3, 10),
            "repairs_percentage": random.randint(5, 15),
            "capex_percentage": random.randint(5, 15),
            "management_percentage": random.randint(8, 12),
            "utilities": random.randint(0, 300),
            "other_expenses": random.randint(0, 200)
        }
        
        # Add analysis-specific fields
        if analysis_type == "BRRRR":
            base_analysis.update({
                "rehab_cost": int(purchase_price * random.uniform(0.1, 0.3)),
                "after_repair_value": int(purchase_price * random.uniform(1.3, 1.7)),
                "refinance_amount_percentage": random.randint(70, 80),
                "refinance_interest_rate": round(random.uniform(3.5, 6.0), 2),
                "refinance_term_years": random.choice([15, 20, 30]),
                "refinance_closing_costs": int(purchase_price * random.uniform(0.02, 0.04))
            })
        elif analysis_type == "Lease Option":
            base_analysis.update({
                "option_consideration_fee": random.randint(1000, 5000),
                "option_term_months": random.randint(12, 36),
                "rent_credit_percentage": random.randint(10, 30),
                "strike_price": int(purchase_price * random.uniform(1.1, 1.3))
            })
        elif analysis_type == "Multi-Family":
            base_analysis.update({
                "total_units": random.randint(2, 20),
                "occupied_units": random.randint(1, 20),  # Will be capped at total_units
                "average_rent_per_unit": random.randint(800, 2000),
                "common_area_maintenance": random.randint(100, 500),
                "elevator_maintenance": random.randint(0, 300),
                "staff_payroll": random.randint(0, 2000)
            })
            # Ensure occupied_units <= total_units
            base_analysis["occupied_units"] = min(base_analysis["occupied_units"], base_analysis["total_units"])
        elif analysis_type == "PadSplit":
            num_rooms = random.randint(3, 8)
            base_analysis.update({
                "total_rooms": num_rooms,
                "average_rent_per_room": random.randint(500, 1200),
                "platform_percentage": random.randint(5, 15),
                "furnishing_costs": random.randint(500, 1500) * num_rooms,
                "common_area_maintenance": random.randint(100, 300)
            })
        
        return base_analysis
    
    @staticmethod
    def generate_loan(property_id=None):
        """
        Generate random loan data.
        
        Args:
            property_id: Optional property ID to associate with the loan
            
        Returns:
            dict: Random loan data
        """
        property_id = property_id or str(uuid.uuid4())
        loan_amount = random.randint(100000, 800000)
        
        return {
            "id": str(uuid.uuid4()),
            "property_id": property_id,
            "loan_type": random.choice(["Primary", "Secondary", "Refinance", "HELOC"]),
            "loan_amount": loan_amount,
            "interest_rate": round(random.uniform(3.0, 7.0), 2),
            "term_months": random.choice([180, 240, 360]),  # 15, 20, or 30 years
            "start_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "payment_amount": round(loan_amount * (random.uniform(0.004, 0.007))),  # Approximate monthly payment
            "has_balloon": random.choice([True, False]),
            "balloon_months": random.choice([60, 84, 120]) if random.choice([True, False]) else None
        }
