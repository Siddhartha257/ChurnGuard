"""
Data preprocessing utilities for churn prediction.
Applies the same preprocessing steps as the training script.
"""
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the same preprocessing steps as the training script.
    
    Args:
        df: Raw DataFrame with customer data
        
    Returns:
        Cleaned DataFrame ready for model prediction
    """
    df = df.copy()
    
    # Drop ID if present
    if 'customerID' in df.columns:
        df = df.drop(columns=['customerID'])
    
    # Drop target column if present (for prediction, we don't need the actual churn value)
    if 'Churn' in df.columns:
        df = df.drop(columns=['Churn'])

    # Handle TotalCharges (Convert to numeric, coerce errors to NaN, fill with 0)
    # Remove any empty spaces or strange characters
    if 'TotalCharges' in df.columns:
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)

    # Normalize Categorical Values (Match Training Logic)
    # The training script replaced 'No internet service' with 'No'
    replace_cols = [
        'MultipleLines', 'OnlineSecurity', 'OnlineBackup', 
        'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies'
    ]
    
    for col in replace_cols:
        if col in df.columns:
            df[col] = df[col].replace('No internet service', 'No')
            df[col] = df[col].replace('No phone service', 'No')

    return df
