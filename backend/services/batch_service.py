"""
Batch analysis service for processing multiple customers and generating insights.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional


def analyze_high_risk_group(df_clean: pd.DataFrame, probs: np.ndarray, shap_aggregate: Optional[Dict] = None) -> str:
    """
    Analyze high-risk customer group and generate summary statistics.
    
    Args:
        df_clean: Cleaned DataFrame
        probs: Array of churn probabilities
        shap_aggregate: Optional dictionary with aggregate SHAP statistics
        
    Returns:
        Summary statistics string for LLM
    """
    high_risk_df = df_clean[probs > 0.6]
    total_customers = len(df_clean)
    churn_rate = (len(high_risk_df) / total_customers) * 100 if total_customers > 0 else 0
    
    if high_risk_df.empty:
        return "Great news! Very few high-risk customers detected."
    
    # Get top categorical frequent values in high risk group
    cat_summary = []
    for col in ['Contract', 'InternetService', 'PaymentMethod', 'TechSupport']:
        if col in high_risk_df.columns:
            mode_result = high_risk_df[col].mode()
            if not mode_result.empty:
                top_val = mode_result[0]
                cat_summary.append(f"{col}: {top_val}")
    
    avg_tenure = high_risk_df['tenure'].mean() if 'tenure' in high_risk_df.columns else 0
    avg_charge = high_risk_df['MonthlyCharges'].mean() if 'MonthlyCharges' in high_risk_df.columns else 0
    
    # Build summary stats
    summary_stats = f"""
    - High Risk Customers: {len(high_risk_df)} ({churn_rate:.1f}% of total)
    - Average Tenure of Risk Group: {avg_tenure:.1f} months
    - Average Monthly Charge: ${avg_charge:.2f}
    - Common Patterns: {', '.join(cat_summary)}
    """
    
    # Add SHAP insights if available
    if shap_aggregate and shap_aggregate.get('top_features'):
        top_features = shap_aggregate['top_features'][:5]  # Top 5 drivers
        shap_insights = "\n    - Top Churn Drivers (Feature Importance):"
        for i, (feature, importance) in enumerate(top_features, 1):
            shap_insights += f"\n      {i}. {feature}: {importance:.3f} (avg impact)"
        summary_stats += shap_insights
    
    return summary_stats
