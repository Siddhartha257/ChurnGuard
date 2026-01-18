"""
SHAP (SHapley Additive exPlanations) service for model interpretability.
Calculates SHAP values to explain model predictions.
"""
import shap
import numpy as np
from typing import List, Tuple


def calculate_shap_values(model, preprocessed_data):
    """
    Calculate SHAP values for model predictions.
    
    Args:
        model: Trained model pipeline
        preprocessed_data: Preprocessed DataFrame ready for prediction
        
    Returns:
        Tuple of (shap_values, feature_names)
    """
    # Extract components from pipeline
    preprocessor = model.named_steps['preprocessor']
    classifier = model.named_steps['classifier']
    
    # Transform using the pipeline's preprocessor
    X_transformed = preprocessor.transform(preprocessed_data)
    
    # Calculate SHAP
    explainer = shap.TreeExplainer(classifier)
    shap_vals = explainer.shap_values(X_transformed)
    
    # Handle SHAP output format (LightGBM binary often returns list of arrays)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]  # Class 1 (Churn)
    
    # Flatten if needed
    if hasattr(shap_vals, 'flatten'):
        shap_vals = shap_vals.flatten().tolist()
    else:
        shap_vals = shap_vals.tolist()
    
    # Get feature names from input data
    feature_names = list(preprocessed_data.columns)
    
    return shap_vals, feature_names


def get_top_features(shap_values: List[float], feature_names: List[str], top_n: int = 5) -> List[Tuple[str, float]]:
    """
    Get top N features by absolute SHAP value.
    
    Args:
        shap_values: List of SHAP values
        feature_names: List of feature names
        top_n: Number of top features to return
        
    Returns:
        List of tuples (feature_name, shap_value) sorted by absolute value
    """
    feats = list(zip(feature_names, shap_values))
    feats.sort(key=lambda x: abs(x[1]), reverse=True)
    return feats[:top_n]


def calculate_batch_shap_aggregate(model, high_risk_data):
    """
    Calculate aggregate SHAP values for a batch of high-risk customers.
    
    Args:
        model: Trained model pipeline
        high_risk_data: DataFrame with high-risk customer data
        
    Returns:
        Dictionary with aggregate SHAP statistics
    """
    if high_risk_data.empty:
        return None
    
    # Extract components from pipeline
    preprocessor = model.named_steps['preprocessor']
    classifier = model.named_steps['classifier']
    
    # Transform using the pipeline's preprocessor
    X_transformed = preprocessor.transform(high_risk_data)
    
    # Calculate SHAP for all high-risk customers
    explainer = shap.TreeExplainer(classifier)
    shap_vals = explainer.shap_values(X_transformed)
    
    # Handle SHAP output format (LightGBM binary often returns list of arrays)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]  # Class 1 (Churn)
    
    # Convert to numpy array if needed
    if not isinstance(shap_vals, np.ndarray):
        shap_vals = np.array(shap_vals)
    
    # Get feature names
    feature_names = list(high_risk_data.columns)
    
    # Calculate mean absolute SHAP values (aggregate importance)
    mean_shap = np.mean(np.abs(shap_vals), axis=0)
    
    # Get top features by average absolute SHAP value
    top_features = list(zip(feature_names, mean_shap))
    top_features.sort(key=lambda x: abs(x[1]), reverse=True)
    
    return {
        'top_features': top_features[:10],  # Top 10 drivers
        'mean_shap_values': mean_shap.tolist(),
        'feature_names': feature_names
    }
