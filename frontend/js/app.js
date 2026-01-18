/**
 * Main application logic
 * Handles navigation and initialization
 */

// Navigation
function navigateTo(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    const targetPage = document.getElementById(`${pageName}-page`);
    if (targetPage) {
        targetPage.classList.add('active');
    }
    
    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === pageName) {
            link.classList.add('active');
        }
    });
}

// Initialize navigation listeners
document.addEventListener('DOMContentLoaded', () => {
    // Set up nav link clicks
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navigateTo(link.dataset.page);
        });
    });
    
    console.log('ChurnGuard initialized');
});

// Helper to show error messages
function showError(message) {
    alert(message);
}

// Helper to format currency
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// Helper to format percentage
function formatPercent(value) {
    return `${(value * 100).toFixed(1)}%`;
}
