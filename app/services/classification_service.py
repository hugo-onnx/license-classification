from typing import List, Optional, Dict
from app.models.schemas import LicenseClassification, UpdateLicenseRequest
from app.services.groq_service import groq_service
from app.config.config import settings

class ClassificationService:    
    def __init__(self):
        # In-memory storage (could be replaced with database)
        self._storage: Dict[str, LicenseClassification] = {}
    
    async def classify_license(self, license_name: str) -> LicenseClassification:
        """
        Classify a single license
        
        Args:
            license_name: Name of the software license
            
        Returns:
            LicenseClassification object
        """
        category, explanation = groq_service.classify_license(license_name)
        
        classification = LicenseClassification(
            license_name=license_name,
            category=category,
            explanation=explanation
        )
        
        self._storage[license_name] = classification
        
        return classification
    
    async def classify_multiple(self, license_names: List[str]) -> List[LicenseClassification]:
        """
        Classify multiple licenses
        
        Args:
            license_names: List of license names
            
        Returns:
            List of LicenseClassification objects
        """
        results = []
        for license_name in license_names:
            try:
                classification = await self.classify_license(license_name)
                results.append(classification)
            except Exception as e:
                print(f"Error classifying {license_name}: {str(e)}")
                fallback = LicenseClassification(
                    license_name=license_name,
                    category="Development",
                    explanation=f"Classification error occurred. Default category assigned."
                )
                results.append(fallback)
        
        return results
    
    def get_all_classifications(self) -> List[LicenseClassification]:
        """Get all stored classifications"""
        return list(self._storage.values())
    
    def get_classification(self, license_name: str) -> Optional[LicenseClassification]:
        """Get classification for specific license"""
        return self._storage.get(license_name)
    
    def update_classification(
        self, 
        license_name: str, 
        update_data: UpdateLicenseRequest
    ) -> LicenseClassification:
        """
        Update classification for a license
        
        Args:
            license_name: Name of the license to update
            update_data: New classification data
            
        Returns:
            Updated LicenseClassification
            
        Raises:
            KeyError: If license not found
        """
        if license_name not in self._storage:
            raise KeyError(f"License '{license_name}' not found")
        
        updated = LicenseClassification(
            license_name=license_name,
            category=update_data.category,
            explanation=update_data.explanation
        )
        
        self._storage[license_name] = updated
        return updated
    
    def delete_classification(self, license_name: str) -> LicenseClassification:
        """
        Delete classification for a license
        
        Args:
            license_name: Name of the license to delete
            
        Returns:
            Deleted LicenseClassification
            
        Raises:
            KeyError: If license not found
        """
        if license_name not in self._storage:
            raise KeyError(f"License '{license_name}' not found")
        
        return self._storage.pop(license_name)
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about classifications
        
        Returns:
            Dictionary with statistics
        """
        if not self._storage:
            return {
                "total_licenses": 0,
                "category_distribution": {},
                "licenses": []
            }
        
        category_counts = {}
        for classification in self._storage.values():
            category = classification.category
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return {
            "total_licenses": len(self._storage),
            "category_distribution": category_counts,
            "licenses": list(self._storage.keys())
        }
    
    def clear_all(self):
        """Clear all classifications"""
        self._storage.clear()

classification_service = ClassificationService()