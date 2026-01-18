"""
Model loading utility.
Handles loading and initialization of the trained churn prediction model.
"""
import joblib
import os


def load_model(model_path: str = 'data/best_churn_model.pkl'):
    """
    Load the trained churn prediction model.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        Loaded model or None if loading fails
    """
    try:
        model = joblib.load(model_path)
        return model
    except Exception as e:
        print(f"WARNING: Model file not found. Please ensure '{model_path}' exists. Error: {e}")
        return None
