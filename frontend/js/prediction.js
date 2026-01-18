/**
 * Single customer prediction logic
 */

let currentPredictionData = null;

// Handle form submission
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('customerForm');
    if (form) {
        form.addEventListener('submit', handlePrediction);
    }
});

async function handlePrediction(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const resultsSection = document.getElementById('singleResults');
    
    // Show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner"></span> Analyzing...';
    resultsSection.innerHTML = '<div class="insights-loading">Analyzing customer data...</div>';
    
    try {
        // Gather form data
        const formData = new FormData(form);
        const customerData = {};
        
        formData.forEach((value, key) => {
            if (key === 'SeniorCitizen') {
                customerData[key] = parseInt(value);
            } else if (key === 'tenure') {
                customerData[key] = parseInt(value);
            } else if (key === 'MonthlyCharges' || key === 'TotalCharges') {
                customerData[key] = key === 'TotalCharges' ? String(value) : parseFloat(value);
            } else {
                customerData[key] = value;
            }
        });
        
        // Make prediction request
        const response = await fetch(`${CONFIG.API_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(customerData)
        });
        
        if (!response.ok) {
            throw new Error('Prediction failed');
        }
        
        const result = await response.json();
        currentPredictionData = result;
        
        // Display results
        displayPredictionResults(result);
        
    } catch (error) {
        console.error('Prediction error:', error);
        showError('Failed to analyze customer. Please try again.');
        resultsSection.innerHTML = '<div class="empty-state"><div class="empty-icon">❌</div><p>Analysis failed. Please try again.</p></div>';
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Analyze Customer';
    }
}

function displayPredictionResults(data) {
    const resultsSection = document.getElementById('singleResults');
    
    const isHighRisk = data.prediction === 1;
    const riskClass = isHighRisk ? 'risk-high' : 'risk-low';
    const riskLabel = isHighRisk ? 'High Risk' : 'Low Risk';
    const probability = data.churn_probability;
    
    resultsSection.innerHTML = `
        <div class="prediction-summary">
            <h3>Churn Prediction</h3>
            <div class="risk-badge ${riskClass}">${riskLabel}</div>
            
            <div class="probability-gauge">
                <div class="gauge-circle">
                    <svg width="160" height="160" style="transform: rotate(-90deg)">
                        <circle cx="80" cy="80" r="70" fill="none" stroke="#e1e8ed" stroke-width="12"/>
                        <circle cx="80" cy="80" r="70" fill="none" 
                                stroke="${isHighRisk ? '#ef4444' : '#10b981'}" 
                                stroke-width="12" 
                                stroke-dasharray="${2 * Math.PI * 70}" 
                                stroke-dashoffset="${2 * Math.PI * 70 * (1 - probability)}"
                                stroke-linecap="round"/>
                    </svg>
                    <div class="gauge-value">${Math.round(probability * 100)}%</div>
                </div>
                <p style="color: #64748b; font-size: 14px;">Churn Probability</p>
            </div>
        </div>
        
        <div class="shap-chart">
            <h4>Key Factors</h4>
            <div class="chart-container">
                <canvas id="shapChart"></canvas>
            </div>
        </div>
        
        <button class="btn btn-secondary btn-full" onclick="getAIInsights()" id="aiButton">
            Get AI Insights
        </button>
        
        <div id="aiInsightsContainer"></div>
    `;
    
    // Render SHAP chart
    renderShapChart(data.feature_names, data.shap_values);
}

async function getAIInsights() {
    const button = document.getElementById('aiButton');
    const container = document.getElementById('aiInsightsContainer');
    
    button.disabled = true;
    button.innerHTML = '<span class="spinner"></span> Generating insights...';
    container.innerHTML = '<div class="insights-loading">Analyzing with AI...</div>';
    
    try {
        const response = await fetch(`${CONFIG.API_URL}/explain_shap`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to get AI insights');
        }
        
        const result = await response.json();
        
        container.innerHTML = `
            <div class="ai-insights">
                <h4>💡 AI Insights</h4>
                <p>${result.explanation.replace(/\n/g, '<br>')}</p>
            </div>
        `;
        
        button.style.display = 'none';
        
    } catch (error) {
        console.error('AI insights error:', error);
        container.innerHTML = '<div class="ai-insights"><p>Failed to generate insights. Please try again.</p></div>';
        button.disabled = false;
        button.textContent = 'Get AI Insights';
    }
}
