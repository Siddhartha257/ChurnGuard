"""
FastAPI routes for Churn Prediction API.
Handles HTTP endpoints for single and batch predictions.
"""
import io
import traceback
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

from utils.model_loader import load_model
from utils.extract import extract_context
from services.prediction_service import predict_single, predict_batch
from services.shap_service import get_top_features
from services.ai_service import (
    get_gemini_explanation,
    generate_shap_explanation_prompt,
    generate_batch_strategy_prompt
)
from services.batch_service import analyze_high_risk_group

load_dotenv()

# Load model at startup
model = load_model('data/best_churn_model.pkl')

# Load company context
context = extract_context('data/policies.txt')

# Initialize FastAPI app
app = FastAPI(title="Churn Prediction API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for latest prediction (used for explainability)
latest_prediction_storage = {}


# --- DATA MODELS ---
class CustomerProfile(BaseModel):
    """Customer profile data model for single prediction."""
    gender: str = "Male"
    SeniorCitizen: int = 0
    Partner: str = "No"
    Dependents: str = "No"
    tenure: int = 12
    PhoneService: str = "Yes"
    MultipleLines: str = "No"
    InternetService: str = "Fiber optic"
    OnlineSecurity: str = "No"
    OnlineBackup: str = "No"
    DeviceProtection: str = "No"
    TechSupport: str = "No"
    StreamingTV: str = "Yes"
    StreamingMovies: str = "Yes"
    Contract: str = "Month-to-month"
    PaperlessBilling: str = "Yes"
    PaymentMethod: str = "Electronic check"
    MonthlyCharges: float = 70.0
    TotalCharges: str = "840.0"


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint."""
    prediction: int
    churn_probability: float
    shap_values: List[float]
    feature_names: List[str]


# --- ENDPOINTS ---
@app.post("/predict", response_model=PredictionResponse)
async def predict_single_endpoint(customer: CustomerProfile):
    """
    Predict churn for a single customer.
    
    Returns prediction, probability, SHAP values, and feature names.
    """
    global latest_prediction_storage
    
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Convert customer profile to dict
        input_data = customer.model_dump()
        
        # Get prediction using service
        result = predict_single(model, input_data)
        
        # Store for explainability endpoint
        latest_prediction_storage = {
            "churn_probability": result["churn_probability"],
            "shap_values": result["shap_values"],
            "feature_names": result["feature_names"]
        }

        return result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict_batch_analysis")
async def predict_batch_analysis_endpoint(file: UploadFile = File(...)):
    """
    Process CSV file and generate batch analysis with strategy report.
    
    Returns:
        - strategy_report: AI-generated retention strategy
        - data: List of customer records with predictions
    """
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")

    try:
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # Get batch predictions (with SHAP for high-risk customers)
        results_df, df_clean, probs, shap_aggregate = predict_batch(model, df, include_shap=True)
        
        # Analyze high-risk group (with SHAP insights)
        summary_stats = analyze_high_risk_group(df_clean, probs, shap_aggregate)
        
        # Generate strategy report prompt
        prompt = generate_batch_strategy_prompt(
            total_customers=len(df),
            summary_stats=summary_stats,
            context=context
        )
        
        # Get AI-generated report
        report = await get_gemini_explanation(prompt)
        
        # Return data + report (Convert DF to dict for JSON response)
        return {
            "strategy_report": report,
            "data": results_df.replace({np.nan: None}).to_dict(orient="records")
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain_shap")
async def explain_shap_endpoint():
    """
    Generate AI explanation for the latest prediction using SHAP values.
    
    Requires a prediction to be made first via /predict endpoint.
    """
    if not latest_prediction_storage:
        raise HTTPException(
            status_code=400,
            detail="No prediction found. Run /predict first."
        )

    try:
        data = latest_prediction_storage
        prob = data["churn_probability"]
        
        # Get top features by SHAP value
        top_5 = get_top_features(
            data["shap_values"],
            data["feature_names"],
            top_n=5
        )
        
        # Generate explanation prompt
        prompt = generate_shap_explanation_prompt(
            churn_probability=prob,
            top_features=top_5,
            context=context
        )
        
        # Get AI explanation
        explanation = await get_gemini_explanation(prompt)
        
        return {"explanation": explanation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
