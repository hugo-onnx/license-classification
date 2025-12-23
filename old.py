import os
import io
import csv

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Software License Classifier")

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

classifications_db = {}

class LicenseClassification(BaseModel):
    license_name: str
    category: str
    explanation: str

class UpdateRequest(BaseModel):
    license_name: str
    category: str
    explanation: str

def classify_license(license_name: str) -> dict:
    """Classify a single license using Groq API"""
    
    prompt = f"""Classify the following software license into ONE of these categories:
- Productivity
- Design
- Communication
- Development
- Finance
- Marketing

Software License: {license_name}

Provide your response in the following format:
Category: [category name]
Explanation: [150-character explanation]

Be concise and keep the explanation under 150 characters."""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a software categorization expert. Classify software licenses accurately and provide brief explanations under 150 characters."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_completion_tokens=200
        )
        
        response_text = chat_completion.choices[0].message.content.strip()
        
        # Parse the response
        lines = response_text.split('\n')
        category = ""
        explanation = ""
        
        for line in lines:
            if line.startswith("Category:"):
                category = line.replace("Category:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
        
        # Truncate explanation to 150 characters
        if len(explanation) > 150:
            explanation = explanation[:147] + "..."
        
        return {
            "license_name": license_name,
            "category": category,
            "explanation": explanation
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error classifying license: {str(e)}")
    

@app.post("/classify", response_model=List[LicenseClassification])
async def classify_licenses(file: UploadFile = File(...)):
    """
    Upload a CSV file with software licenses and classify them.
    CSV should have a column with license names (first column will be used).
    """
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    
    try:
        # Read CSV file
        contents = await file.read()
        csv_file = io.StringIO(contents.decode('utf-8'))
        csv_reader = csv.reader(csv_file)
        
        # Skip header if present
        licenses = []
        for i, row in enumerate(csv_reader):
            if row and row[0].strip():
                # Skip header row if it contains common header keywords
                if i == 0 and any(keyword in row[0].lower() for keyword in ['name', 'license', 'software', 'product']):
                    continue
                licenses.append(row[0].strip())
        
        if not licenses:
            raise HTTPException(status_code=400, detail="No licenses found in CSV file")
        
        # Classify all licenses
        results = []
        for license_name in licenses:
            classification = classify_license(license_name)
            results.append(classification)
            # Store in database
            classifications_db[license_name] = classification
        
        return results
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    

@app.get("/results", response_model=List[LicenseClassification])
async def get_results():
    """
    Retrieve all classification results.
    """
    
    if not classifications_db:
        return JSONResponse(
            status_code=404,
            content={"message": "No classifications found. Please upload a CSV file first."}
        )
    
    return list(classifications_db.values())


@app.get("/results/{license_name}", response_model=LicenseClassification)
async def get_result_by_name(license_name: str):
    """
    Retrieve classification result for a specific license.
    """
    
    if license_name not in classifications_db:
        raise HTTPException(status_code=404, detail=f"License '{license_name}' not found")
    
    return classifications_db[license_name]


@app.put("/update/{license_name}", response_model=LicenseClassification)
async def update_license(license_name: str, update_data: UpdateRequest):
    """
    Manually update the classification of a license.
    """
    
    if license_name not in classifications_db:
        raise HTTPException(status_code=404, detail=f"License '{license_name}' not found")
    
    # Validate category
    valid_categories = ["Productivity", "Design", "Communication", "Development", "Finance", "Marketing"]
    if update_data.category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Truncate explanation to 150 characters
    explanation = update_data.explanation
    if len(explanation) > 150:
        explanation = explanation[:147] + "..."
    
    # Update the classification
    classifications_db[license_name] = {
        "license_name": license_name,
        "category": update_data.category,
        "explanation": explanation
    }
    
    return classifications_db[license_name]


@app.delete("/results/{license_name}")
async def delete_result(license_name: str):
    """
    Delete a classification result.
    """
    
    if license_name not in classifications_db:
        raise HTTPException(status_code=404, detail=f"License '{license_name}' not found")
    
    deleted = classifications_db.pop(license_name)
    return {"message": f"Classification for '{license_name}' deleted successfully", "deleted": deleted}
    

@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Software License Classification API",
        "endpoints": {
            "POST /classify": "Upload CSV file to classify licenses",
            "GET /results": "View all classification results",
            "GET /results/{license_name}": "View specific license classification",
            "PUT /update/{license_name}": "Update a license classification manually",
            "DELETE /results/{license_name}": "Delete a classification result"
        },
        "categories": ["Productivity", "Design", "Communication", "Development", "Finance", "Marketing"]
    }


@app.get("/stats")
async def get_statistics():
    """
    Get statistics about classified licenses.
    """
    
    if not classifications_db:
        return {"message": "No classifications available"}
    
    category_counts = {}
    for classification in classifications_db.values():
        category = classification["category"]
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return {
        "total_licenses": len(classifications_db),
        "category_distribution": category_counts,
        "licenses": list(classifications_db.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)