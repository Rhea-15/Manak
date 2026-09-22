"""
Dev 3: Validation Rules Engine
Validates standards against QCO, ISI, and mandatory requirements
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CertificationType(Enum):
    """Certification types for standards"""
    QCO = "qco"  # Quality Control Order
    ISI = "isi"  # Indian Standards Institution
    MANDATORY = "mandatory"
    OPTIONAL = "optional"


@dataclass
class ValidationError:
    """Single validation error"""
    field: str
    error_type: str
    message: str
    severity: str  # "error", "warning", "info"


@dataclass
class ValidationResult:
    """Complete validation result"""
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError]
    score: float  # 0-100


class RulesEngine:
    """Rule-based validation engine for standards"""

    def __init__(self):
        """Initialize rules engine"""
        self.logger = logging.getLogger(__name__)
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> dict:
        """Define validation rules for standards"""
        return {
            "code": {
                "pattern": r"^IS\s*(\d{4,5})(?::\d{4})?$",
                "required": True,
                "message": "Standard code must be in format 'IS XXXX' or 'IS XXXX:YYYY'"
            },
            "title": {
                "min_length": 10,
                "max_length": 500,
                "required": True,
                "message": "Title must be 10-500 characters"
            },
            "definition": {
                "min_length": 20,
                "required": True,
                "message": "Definition required, minimum 20 characters"
            },
            "year": {
                "pattern": r"^\d{4}$",
                "min_value": 1950,
                "max_value": 2030,
                "required": False,
                "message": "Year must be YYYY format, between 1950 and 2030"
            },
        }

    def validate_standard(self, standard: dict) -> ValidationResult:
        """
        Validate a complete standard.
        
        Args:
            standard: {
                "code": "IS 1554",
                "title": "Fire-retardant wires",
                "definition": "...",
                "year": 2018,
                "qco_required": True,
                "isi_required": False,
            }
        
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # Validate each field
        for field, rule in self.rules.items():
            value = standard.get(field)
            
            # Normalize strings by stripping whitespace
            normalized_value = value.strip() if isinstance(value, str) else value
            
            # Check required
            if rule.get("required") and not normalized_value:
                errors.append(ValidationError(
                    field=field,
                    error_type="required",
                    message=f"{field} is required",
                    severity="error"
                ))
                continue
            
            if normalized_value is None or normalized_value == "":
                continue
            
            # Check pattern
            if "pattern" in rule and not re.match(rule["pattern"], str(normalized_value)):
                errors.append(ValidationError(
                    field=field,
                    error_type="format",
                    message=rule["message"],
                    severity="error"
                ))
            
            # Check length
            if "min_length" in rule and len(str(normalized_value)) < rule["min_length"]:
                errors.append(ValidationError(
                    field=field,
                    error_type="length",
                    message=rule["message"],
                    severity="error"
                ))
            
            if "max_length" in rule and len(str(normalized_value)) > rule["max_length"]:
                errors.append(ValidationError(
                    field=field,
                    error_type="length",
                    message=rule["message"],
                    severity="error"
                ))
            
            # Check numeric range
            if "min_value" in rule:
                try:
                    if int(normalized_value) < rule["min_value"]:
                        errors.append(ValidationError(
                            field=field,
                            error_type="range",
                            message=rule["message"],
                            severity="error"
                        ))
                except (ValueError, TypeError):
                    pass
            
            if "max_value" in rule:
                try:
                    if int(normalized_value) > rule["max_value"]:
                        errors.append(ValidationError(
                            field=field,
                            error_type="range",
                            message=rule["message"],
                            severity="error"
                        ))
                except (ValueError, TypeError):
                    pass
        
        # Validate certifications
        cert_errors = self._validate_certifications(standard)
        errors.extend(cert_errors)
        
        # Calculate score
        score = max(0, 100 - (len(errors) * 25))
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            score=score
        )

    def _validate_certifications(self, standard: dict) -> list[ValidationError]:
        """Validate certification requirements"""
        errors = []
        
        # Check QCO requirement
        if standard.get("qco_required") and not standard.get("qco_code"):
            errors.append(ValidationError(
                field="qco_code",
                error_type="certification",
                message="QCO code required but not provided",
                severity="error"
            ))
        
        # Check ISI requirement
        if standard.get("isi_required") and not standard.get("isi_mark"):
            errors.append(ValidationError(
                field="isi_mark",
                error_type="certification",
                message="ISI mark required but not provided",
                severity="error"
            ))
        
        return errors

    def get_validation_summary(self, result: ValidationResult) -> dict:
        """Get human-readable summary of validation"""
        error_count = len(result.errors)
        warning_count = len(result.warnings)
        
        return {
            "valid": result.is_valid,
            "score": result.score,
            "error_count": error_count,
            "warning_count": warning_count,
            "status": "Valid" if result.is_valid else "Invalid",
            "summary": f"{error_count} errors, {warning_count} warnings"
        }