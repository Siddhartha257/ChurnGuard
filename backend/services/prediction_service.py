"""
Prediction service for churn prediction.
Handles single and batch predictions.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from utils.data_preprocessing import clean_data
from services.shap_service import calculate_shap_values


def predict_single(model, customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predict churn for a single customer.
    
    Args:
        model: Trained model pipeline
        customer_data: Dictionary of customer features
        
    Returns:
        Dictionary with prediction, probability, SHAP values, and feature names
    """
    # Convert to DataFrame
    df = pd.DataFrame([customer_data])
    
    # Clean data
    df_clean = clean_data(df)
    
    # Predict
    pred = model.predict(df_clean)[0]
    prob = model.predict_proba(df_clean)[0][1]
    
    # Calculate SHAP values
    shap_vals, feature_names = calculate_shap_values(model, df_clean)
    
    return {
        "prediction": int(pred),
        "churn_probability": float(prob),
        "shap_values": shap_vals,
        "feature_names": feature_names
    }


def predict_batch(model, df: pd.DataFrame, include_shap: bool = True):
    """
    Predict churn for a batch of customers.
    
    Args:
        model: Trained model pipeline
        df: DataFrame with customer data
        include_shap: Whether to calculate SHAP values for high-risk customers
        
    Returns:
        Tuple of (results_df, df_clean, probs, shap_aggregate)
        - results_df: DataFrame with added Churn_Probability and Risk_Level columns
        - df_clean: Cleaned DataFrame
        - probs: Array of churn probabilities
        - shap_aggregate: Dictionary with aggregate SHAP statistics (or None)
    """
    # Clean data
    df_clean = clean_data(df)
    
    # Predict
    probs = model.predict_proba(df_clean)[:, 1]
    preds = model.predict(df_clean)
    
    # Attach results
    results_df = df.copy()
    results_df['Churn_Probability'] = probs
    results_df['Risk_Level'] = np.where(probs > 0.6, 'High', 'Low')
    
    # Calculate SHAP for high-risk customers if requested
    shap_aggregate = None
    if include_shap:
        from services.shap_service import calculate_batch_shap_aggregate
        high_risk_mask = probs > 0.6
        if high_risk_mask.any():
            high_risk_data = df_clean[high_risk_mask]
            shap_aggregate = calculate_batch_shap_aggregate(model, high_risk_data)
    
    return results_df, df_clean, probs, shap_aggregate
