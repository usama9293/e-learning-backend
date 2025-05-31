import requests

def test_login():
    # Login endpoint
    login_url = "https://e-learning-backend-7-57nd.onrender.com/api/v1/auth/login"
    
    # Login data
    login_data = {
        "username": "admin@example.com",
        "password": "admin"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        # Make the request
        response = requests.post(login_url, data=login_data, headers=headers)
        
        # Print status code
        print("Status Code:", response.status_code)
        
        # Print response
        print("Response:", response.json())
        
        # If successful, save the token
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("\nAccess Token:", token)
            return token
            
    except Exception as e:
        print("Error:", str(e))

# Run the test
test_login()