/**
 * Batch analysis logic
 */

let batchResultsData = null;

// Handle file upload
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('csvFile');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileSelect);
    }
});

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Show file name
    const fileNameDisplay = document.getElementById('fileName');
    fileNameDisplay.textContent = `Selected: ${file.name}`;
    
    // Process file
    processBatchFile(file);
}

async function processBatchFile(file) {
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('batchResults');
    
    // Show loading state
    uploadSection.innerHTML = `
        <div class="upload-card">
            <div class="insights-loading">
                <div class="spinner" style="border-color: #0ea5e9; border-top-color: transparent; width: 48px; height: 48px; margin: 0 auto 16px;"></div>
                <p>Processing ${file.name}...</p>
            </div>
        </div>
    `;
    
    try {
        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Upload and analyze
        const response = await fetch(`${CONFIG.API_URL}/predict_batch_analysis`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Batch analysis failed');
        }
        
        const result = await response.json();
        batchResultsData = result.data;
        
        // Display results
        displayBatchResults(result);
        
    } catch (error) {
        console.error('Batch analysis error:', error);
        showError('Failed to process file. Please check the format and try again.');
        resetBatch();
    }
}

function displayBatchResults(result) {
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('batchResults');
    const reportContainer = document.getElementById('strategyReport');
    const dataPreview = document.getElementById('dataPreview');
    
    // Hide upload, show results
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Format and display strategy report
    const formattedReport = formatMarkdown(result.strategy_report);
    reportContainer.innerHTML = formattedReport;
    
    // Show data summary
    const highRiskCount = result.data.filter(c => c.Risk_Level === 'High').length;
    const totalCount = result.data.length;
    const highRiskPercent = ((highRiskCount / totalCount) * 100).toFixed(1);
    
    dataPreview.innerHTML = `
        <h4>Analysis Summary</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-top: 16px;">
            <div style="background: #f1f5f9; padding: 20px; border-radius: 8px;">
                <div style="font-size: 32px; font-weight: 700; color: #0ea5e9;">${totalCount}</div>
                <div style="font-size: 14px; color: #64748b;">Total Customers</div>
            </div>
            <div style="background: #fee2e2; padding: 20px; border-radius: 8px;">
                <div style="font-size: 32px; font-weight: 700; color: #991b1b;">${highRiskCount}</div>
                <div style="font-size: 14px; color: #64748b;">High Risk</div>
            </div>
            <div style="background: #d1fae5; padding: 20px; border-radius: 8px;">
                <div style="font-size: 32px; font-weight: 700; color: #065f46;">${totalCount - highRiskCount}</div>
                <div style="font-size: 14px; color: #64748b;">Low Risk</div>
            </div>
            <div style="background: #f1f5f9; padding: 20px; border-radius: 8px;">
                <div style="font-size: 32px; font-weight: 700; color: #ef4444;">${highRiskPercent}%</div>
                <div style="font-size: 14px; color: #64748b;">Risk Rate</div>
            </div>
        </div>
    `;
}

function formatMarkdown(text) {
    // Simple markdown formatting
    return text
        .replace(/^### (.*$)/gim, '<h4>$1</h4>')
        .replace(/^## (.*$)/gim, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
}

function downloadResults() {
    if (!batchResultsData) return;
    
    // Convert to CSV
    const headers = Object.keys(batchResultsData[0]);
    const csvRows = [headers.join(',')];
    
    for (const row of batchResultsData) {
        const values = headers.map(header => {
            const value = row[header] || '';
            // Escape quotes and wrap in quotes
            return `"${String(value).replace(/"/g, '""')}"`;
        });
        csvRows.push(values.join(','));
    }
    
    const csvContent = csvRows.join('\n');
    
    // Download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'churn_analysis_results.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function resetBatch() {
    const uploadSection = document.getElementById('uploadSection');
    const resultsSection = document.getElementById('batchResults');
    const fileInput = document.getElementById('csvFile');
    
    // Reset upload section
    uploadSection.innerHTML = `
        <div class="upload-card">
            <div class="upload-icon">📁</div>
            <h3>Upload Customer Data</h3>
            <p>Select a CSV file containing customer information</p>
            <input type="file" id="csvFile" accept=".csv" style="display: none;">
            <button class="btn btn-primary" onclick="document.getElementById('csvFile').click()">
                Choose File
            </button>
            <div id="fileName" class="file-name"></div>
        </div>
    `;
    
    uploadSection.style.display = 'flex';
    resultsSection.style.display = 'none';
    
    // Re-attach event listener
    const newFileInput = document.getElementById('csvFile');
    newFileInput.addEventListener('change', handleFileSelect);
    
    // Clear data
    batchResultsData = null;
    fileInput.value = '';
}
