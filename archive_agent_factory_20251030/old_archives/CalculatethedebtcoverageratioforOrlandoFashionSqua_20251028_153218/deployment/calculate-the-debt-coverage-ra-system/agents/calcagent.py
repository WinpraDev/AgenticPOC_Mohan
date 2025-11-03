import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from loguru import logger
import numpy as np

class MissingDataError(Exception):
    pass

class InvalidDataError(Exception):
    pass

class PropertyData(BaseModel):
    rental_income: float
    debt_payments: float

class CalcAgent:
    def __init__(self):
        self.agent_name = os.getenv('AGENT_NAME', 'CalcAgent')
        self.version = os.getenv('VERSION', '1.0.0')
        self.description = os.getenv('DESCRIPTION', 'CalcAgent is a primary agent designed to calculate the debt coverage ratio for properties and check if rental income covers debt payments.')
        self.role = os.getenv('ROLE', 'primary_agent')
        self.timeout_seconds = int(os.getenv('TIMEOUT_SECONDS', 10))
        self.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
        self.logging_level = os.getenv('LOGGING_LEVEL', 'INFO')
        logger.add(os.getenv('LOG_FILE', 'calc_agent.log'), level=self.logging_level)

    def calculate_debt_coverage_ratio(self, property_data: Dict[str, Any]) -> float:
        try:
            data = PropertyData(**property_data)
            debt_coverage_ratio = data.rental_income / data.debt_payments
            return debt_coverage_ratio
        except (ValidationError, KeyError) as e:
            logger.error("MissingDataError: Property data is missing required fields.")
            raise MissingDataError("Property data is missing required fields.") from e
        except ZeroDivisionError as e:
            logger.error("InvalidDataError: Invalid data provided for calculation.")
            raise InvalidDataError("Invalid data provided for calculation.") from e

    def check_rental_coverage(self, property_data: Dict[str, Any]) -> bool:
        try:
            data = PropertyData(**property_data)
            is_covered = data.rental_income >= data.debt_payments
            return is_covered
        except (ValidationError, KeyError) as e:
            logger.error("MissingDataError: Property data is missing required fields.")
            raise MissingDataError("Property data is missing required fields.") from e
        except Exception as e:
            logger.error("InvalidDataError: Invalid data provided for calculation.")
            raise InvalidDataError("Invalid data provided for calculation.") from e

# Example usage
if __name__ == "__main__":
    agent = CalcAgent()
    property_data = {"rental_income": 5000, "debt_payments": 2000}
    ratio = agent.calculate_debt_coverage_ratio(property_data)
    covered = agent.check_rental_coverage(property_data)
    print(f"Debt Coverage Ratio: {ratio}")
    print(f"Is Covered: {covered}")