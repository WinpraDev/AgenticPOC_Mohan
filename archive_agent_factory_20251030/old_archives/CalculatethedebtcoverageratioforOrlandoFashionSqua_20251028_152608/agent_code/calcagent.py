import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from loguru import logger
import pandas as pd

class MissingDataError(Exception):
    """Exception raised when required data is missing."""
    pass

class InvalidDataError(Exception):
    """Exception raised when invalid data is provided for calculation."""
    pass

class PropertyData(BaseModel):
    rental_income: float
    debt_payments: float

class CalcAgent:
    def __init__(self):
        self.logger = logger
        self.logger.add(os.getenv('LOG_FILE', 'calc_agent.log'), level=os.getenv('LOG_LEVEL', 'INFO'))

    def calculate_debt_coverage_ratio(self, property_data: Dict[str, Any]) -> float:
        """
        Calculates the debt coverage ratio for a given property.
        
        Args:
            property_data (Dict[str, Any]): A dictionary containing 'rental_income' and 'debt_payments'.
        
        Returns:
            float: The debt coverage ratio.
        
        Raises:
            MissingDataError: If required data is missing.
            InvalidDataError: If invalid data is provided for calculation.
        """
        try:
            property_data = PropertyData(**property_data)
        except ValidationError as e:
            self.logger.error(f"Invalid data provided for calculation: {e}")
            raise InvalidDataError("Invalid data provided for calculation.") from e
        
        if property_data.rental_income <= 0 or property_data.debt_payments <= 0:
            self.logger.error("Invalid data provided for calculation.")
            raise InvalidDataError("Invalid data provided for calculation.")
        
        debt_coverage_ratio = property_data.rental_income / property_data.debt_payments
        return debt_coverage_ratio

    def check_rental_coverage(self, property_data: Dict[str, Any]) -> bool:
        """
        Checks if rental income covers debt payments.
        
        Args:
            property_data (Dict[str, Any]): A dictionary containing 'rental_income' and 'debt_payments'.
        
        Returns:
            bool: True if rental income covers debt payments, False otherwise.
        
        Raises:
            MissingDataError: If required data is missing.
            InvalidDataError: If invalid data is provided for calculation.
        """
        try:
            property_data = PropertyData(**property_data)
        except ValidationError as e:
            self.logger.error(f"Invalid data provided for calculation: {e}")
            raise InvalidDataError("Invalid data provided for calculation.") from e
        
        if property_data.rental_income <= 0 or property_data.debt_payments <= 0:
            self.logger.error("Invalid data provided for calculation.")
            raise InvalidDataError("Invalid data provided for calculation.")
        
        is_covered = property_data.rental_income >= property_data.debt_payments
        return is_covered

# Example usage:
if __name__ == "__main__":
    agent = CalcAgent()
    property_data = {"rental_income": 5000, "debt_payments": 2000}
    
    try:
        ratio = agent.calculate_debt_coverage_ratio(property_data)
        print(f"Debt Coverage Ratio: {ratio}")
        
        is_covered = agent.check_rental_coverage(property_data)
        print(f"Rental Income Covers Debt Payments: {is_covered}")
    except (MissingDataError, InvalidDataError) as e:
        print(e)