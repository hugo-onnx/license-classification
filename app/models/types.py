from typing import Annotated, Any
from pydantic import BeforeValidator, AfterValidator, Field
from app.config.config import settings

def truncate_logic(v: Any) -> Any:
    """Logic to truncate strings before Pydantic checks max_length"""
    if isinstance(v, str) and len(v) > settings.MAX_EXPLANATION_LENGTH:
        return v[:settings.MAX_EXPLANATION_LENGTH - 3] + "..."
    return v

def category_logic(v: str) -> str:
    """Logic to validate category against allowed settings"""
    if v not in settings.VALID_CATEGORIES:
        raise ValueError(
            f"Category must be one of: {', '.join(settings.VALID_CATEGORIES)}"
        )
    return v


TruncatedExplanation = Annotated[str, BeforeValidator(truncate_logic), Field(max_length=settings.MAX_EXPLANATION_LENGTH)]
LicenseCategory = Annotated[str, AfterValidator(category_logic)]