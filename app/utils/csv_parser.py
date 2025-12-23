import io
import csv
from typing import List

class CSVParser:
    """Utility for parsing CSV files"""
    
    @staticmethod
    def parse_licenses(file_content: bytes) -> List[str]:
        """
        Parse CSV file and extract license names
        
        Args:
            file_content: Raw bytes from uploaded CSV file
            
        Returns:
            List of license names
            
        Raises:
            ValueError: If CSV is invalid or empty
        """
        try:
            content_str = file_content.decode('utf-8')
            csv_file = io.StringIO(content_str)
            csv_reader = csv.reader(csv_file)
            
            licenses = []
            header_keywords = ['name', 'license', 'software', 'product', 'title']
            
            for i, row in enumerate(csv_reader):
                if not row or not row[0].strip():
                    continue
                
                if i == 0:
                    first_cell = row[0].lower().strip()
                    if any(keyword in first_cell for keyword in header_keywords):
                        continue
                
                license_name = row[0].strip()
                if license_name:
                    licenses.append(license_name)
            
            if not licenses:
                raise ValueError("No valid licenses found in CSV file")
            
            return licenses
            
        except UnicodeDecodeError:
            raise ValueError("Invalid CSV file encoding. Please use UTF-8.")
        except csv.Error as e:
            raise ValueError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    @staticmethod
    def validate_csv_format(filename: str) -> bool:
        """
        Validate that file is a CSV
        
        Args:
            filename: Name of uploaded file
            
        Returns:
            True if valid CSV extension
        """
        return filename.lower().endswith('.csv')