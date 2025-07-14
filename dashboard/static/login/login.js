// Login Page JavaScript

// DOM Elements
const loginForm = document.getElementById('login-form');
const usernameInput = document.getElementById('username');
const passwordInput = document.getElementById('password');
const loginBtn = document.getElementById('login-btn');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');

// Initialize login page
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    checkExistingSession();
    
    // Add form submit handler
    loginForm.addEventListener('submit', handleLogin);
    
    // Add input handlers to clear errors
    usernameInput.addEventListener('input', clearError);
    passwordInput.addEventListener('input', clearError);
    
    // Focus on username field
    usernameInput.focus();
});

// Check if user already has a valid session
async function checkExistingSession() {
    try {
        const response = await fetch('/api/auth/verify', {
            credentials: 'include'
        });
        
        if (response.ok) {
            // User is already logged in, redirect to dashboard
            window.location.href = '/';
        }
    } catch (error) {
        // No existing session, stay on login page
        console.log('No existing session');
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const username = usernameInput.value.trim();
    const password = passwordInput.value.trim();
    
    // Basic validation
    if (!username || !password) {
        showError('Please enter both username and password');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    clearError();
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // Success - redirect to dashboard
            console.log('Login successful:', result);
            window.location.href = '/';
            
        } else {
            const error = await response.json();
            showError(error.detail || 'Invalid username or password');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showError('Connection error. Please try again.');
    } finally {
        setLoadingState(false);
    }
}

// Show loading state on login button
function setLoadingState(loading) {
    const buttonText = loginBtn.querySelector('.button-text');
    const buttonSpinner = loginBtn.querySelector('.button-spinner');
    
    if (loading) {
        buttonText.textContent = 'Signing In...';
        buttonSpinner.classList.remove('hidden');
        loginBtn.disabled = true;
    } else {
        buttonText.textContent = 'Sign In';
        buttonSpinner.classList.add('hidden');
        loginBtn.disabled = false;
    }
}

// Show error message
function showError(message) {
    errorText.textContent = message;
    errorMessage.classList.remove('hidden');
    
    // Focus on username field for retry
    usernameInput.focus();
    usernameInput.select();
}

// Clear error message
function clearError() {
    errorMessage.classList.add('hidden');
    errorText.textContent = '';
}

// Handle Enter key on password field
passwordInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        handleLogin(event);
    }
});