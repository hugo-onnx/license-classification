from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List
from app.models.schemas import (
    LicenseClassification,
    UpdateLicenseRequest,
    StatsResponse,
    ErrorResponse
)
from app.services.classification_service import classification_service
from app.utils.csv_parser import CSVParser


router = APIRouter(prefix="/api/v1", tags=["classification"])


@router.post(
    "/classify",
    response_model=List[LicenseClassification],
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file format"},
        500: {"model": ErrorResponse, "description": "Classification error"}
    }
)
async def classify_licenses(file: UploadFile = File(...)):
    """
    Upload CSV file and classify all software licenses
    
    The CSV file should contain license names in the first column.
    Header rows are automatically detected and skipped.
    
    Returns a list of classifications with category and explanation (max 150 chars).
    """
    if not CSVParser.validate_csv_format(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted"
        )
    
    try:
        content = await file.read()
        license_names = CSVParser.parse_licenses(content)
        
        results = await classification_service.classify_multiple(license_names)
        
        return results
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
    

@router.get(
    "/results",
    response_model=List[LicenseClassification],
    responses={
        404: {"model": ErrorResponse, "description": "No classifications found"}
    }
)
async def get_all_results():
    """
    Retrieve all classification results
    
    Returns empty list if no classifications exist.
    """
    results = classification_service.get_all_classifications()
    
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No classifications found. Please upload a CSV file first."
        )
    
    return results


@router.get(
    "/results/{license_name}",
    response_model=LicenseClassification,
    responses={
        404: {"model": ErrorResponse, "description": "License not found"}
    }
)
async def get_result_by_name(license_name: str):
    """
    Retrieve classification result for a specific license
    
    Args:
        license_name: Exact name of the software license
    """
    result = classification_service.get_classification(license_name)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"License '{license_name}' not found"
        )
    
    return result


@router.put(
    "/results/{license_name}",
    response_model=LicenseClassification,
    responses={
        404: {"model": ErrorResponse, "description": "License not found"},
        400: {"model": ErrorResponse, "description": "Invalid category"}
    }
)
async def update_license_classification(
    license_name: str,
    update_data: UpdateLicenseRequest
):
    """
    Manually update the classification of a license
    
    Args:
        license_name: Exact name of the license to update
        update_data: New category and explanation
    
    The explanation will be automatically truncated to 150 characters if needed.
    """
    try:
        updated = classification_service.update_classification(
            license_name,
            update_data
        )
        return updated
        
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    

@router.delete(
    "/results/{license_name}",
    responses={
        404: {"model": ErrorResponse, "description": "License not found"}
    }
)
async def delete_result(license_name: str):
    """
    Delete a classification result
    
    Args:
        license_name: Exact name of the license to delete
    """
    try:
        deleted = classification_service.delete_classification(license_name)
        return {
            "message": f"Classification for '{license_name}' deleted successfully",
            "deleted": deleted
        }
        
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    

@router.get(
    "/stats",
    response_model=StatsResponse
)
async def get_statistics():
    """
    Get statistics about classified licenses
    
    Returns total count, category distribution, and list of all license names.
    """
    stats = classification_service.get_statistics()
    return stats