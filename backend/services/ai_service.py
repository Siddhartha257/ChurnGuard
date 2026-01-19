"""
AI service for generating explanations and strategy reports using Gemini.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-3-flash-preview")


async def get_gemini_explanation(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text


def generate_shap_explanation_prompt(
    churn_probability: float,  
    top_features: list,
    context: str
) -> str:
    """
    Generate prompt for SHAP-based explanation.
    
    Args:
        churn_probability: Probability of churn
        top_features: List of tuples (feature_name, shap_value)
        context: Company context
        
    Returns:
        Formatted prompt string
    """
    risk_level = 'High' if churn_probability > 0.5 else 'Low'
    
    top_drivers = "\n".join([f"- {f[0]}: {f[1]:.3f}" for f in top_features])
    
    prompt = f"""
    Act as a Retention Manager. Analyze this customer and company context:
    Churn Risk: {churn_probability:.1%} ({risk_level})
    company context: {context}
    
    Top Drivers:
    {top_drivers}
    
    Briefly explain why they might leave and suggest 1 retention action.
    """
    
    return prompt


def generate_batch_strategy_prompt(
    total_customers: int,
    summary_stats: str,
    context: str
) -> str:
    """
    Generate prompt for batch strategy report.
    
    Args:
        total_customers: Total number of customers analyzed
        summary_stats: Summary statistics of high-risk group (includes SHAP insights if available)
        context: Company context
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""
    You are a generic Strategy Consultant. 
    I have analyzed a batch of {total_customers} customers. Here is the summary of the "At Risk" segment:
    
    {summary_stats}
    company context: {context}
    
    Based on these stats, feature importance data (SHAP values), and company context, provide a brief "Retention Strategy Report" with:
    1. **Executive Summary**: What is the main problem? Focus on the top churn drivers identified.
    2. **3 Actionable Strategies**: Specific things to do, prioritized by the feature importance data. For example:
       - If "Contract" is a top driver, suggest contract upgrade incentives
       - If "Tenure" is important, focus on early-stage retention programs
       - If "PaymentMethod" matters, offer payment plan options
    
    Keep it professional, concise, and use markdown formatting. Prioritize strategies based on the feature importance rankings.
    """
    
    return prompt
