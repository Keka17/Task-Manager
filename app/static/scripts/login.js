
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value.trim();
        const errorDiv = document.getElementById('errorMessage');
        const successDiv = document.getElementById('successMessage');
        const submitBtn = document.getElementById('submitBtn');
        const loadingDiv = document.getElementById('loading');

        // Clear messages
        errorDiv.style.display = 'none';
        errorDiv.textContent = '';
        successDiv.style.display = 'none';
        successDiv.textContent = '';
        submitBtn.disabled = true;
        loadingDiv.style.display = 'block';

        try {
            console.log('Attempting login for:', email);

            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    'email': email,
                    'password': password
                })
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));

            const responseText = await response.text();
            console.log('Raw response:', responseText);

            let data;
            try {
                data = JSON.parse(responseText);
            } catch (parseError) {
                console.error('Failed to parse JSON:', parseError);

                // If an HTML page
                if (responseText.includes('<html') || responseText.includes('<!DOCTYPE')) {
                    throw new Error('Server returned HTML instead of JSON. Check your endpoint.');
                }

                throw new Error(`Server returned invalid JSON: ${responseText.substring(0, 100)}`);
            }

            if (response.ok) {
                console.log('Login successful! Response:', data);

                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);

                    if (data.refresh_token) {
                        localStorage.setItem('refresh_token', data.refresh_token);
                    }

                    successDiv.style.display = 'block';

                    // Redirect immediately
                    window.location.href = '/ws/enter';

                } else {
                    throw new Error('No access token in response');
                }
            } else {
                // Server error handling
                let errorMsg = 'Ошибка входа';

                if (data.detail) {
                    errorMsg = Array.isArray(data.detail) ?
                        data.detail.map(d => d.msg || d).join(', ') :
                        data.detail;
                } else if (data.message) {
                    errorMsg = data.message;
                }

                throw new Error(errorMsg);
            }

        } catch (error) {
            console.error('Login error:', error);
            errorDiv.textContent = error.message;
            errorDiv.style.display = 'block';
        } finally {
            submitBtn.disabled = false;
            loadingDiv.style.display = 'none';
        }
    });

// Automatic redirection if already logged in
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');
    if (token) {
        console.log('Already logged in, redirecting...');
        window.location.href = '/ws/board/enter';
    }
});
