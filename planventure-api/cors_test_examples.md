# CORS Configuration Testing Guide

## Overview
This guide provides examples for testing CORS configuration with React frontend applications.

## Environment Configuration

### Development Environment
```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001
FLASK_ENV=development
```

### Production Environment
```env
CORS_ORIGINS=https://your-react-app.com,https://www.your-react-app.com
FLASK_ENV=production
```

## React Frontend Setup

### 1. Basic Fetch Request
```javascript
// React component example
const apiCall = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/trips', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
      },
      credentials: 'include' // Important for CORS with credentials
    });
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('CORS Error:', error);
  }
};
```

### 2. Axios Configuration
```javascript
// axios setup with CORS
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 3. React Environment Variables
```env
# .env file in React app
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_API_BASE_URL=http://localhost:5000
```

## Testing CORS Configuration

### 1. Preflight Request Test
```bash
# Test OPTIONS request (preflight)
curl -X OPTIONS http://localhost:5000/api/trips \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization" \
  -v
```

### 2. Actual Request Test
```bash
# Test actual request with CORS headers
curl -X GET http://localhost:5000/api/trips \
  -H "Origin: http://localhost:3000" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -v
```

### 3. JavaScript Browser Test
```javascript
// Test in browser console
fetch('http://localhost:5000/api/trips', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN'
  },
  credentials: 'include'
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

## Common CORS Issues and Solutions

### Issue 1: "Access to fetch blocked by CORS policy"
**Solution**: Ensure the React app origin is included in CORS_ORIGINS

### Issue 2: "Credentials flag is 'true', but credentials not supported"
**Solution**: Make sure supports_credentials=True in Flask CORS config

### Issue 3: "Method not allowed in CORS policy"
**Solution**: Add the HTTP method to the allowed methods list

### Issue 4: "Header not allowed in CORS policy"
**Solution**: Add the header to allow_headers list

## React Development Server Proxy (Alternative)

### package.json proxy
```json
{
  "name": "planventure-frontend",
  "proxy": "http://localhost:5000",
  "dependencies": {
    "react": "^18.0.0"
  }
}
```

### Create React App setupProxy.js
```javascript
// src/setupProxy.js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5000',
      changeOrigin: true,
      secure: false
    })
  );
};
```

## Expected CORS Headers

### Successful Response Headers
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Max-Age: 3600
```

### Preflight Response Headers
```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS, PATCH
Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With, Accept, Origin
Access-Control-Max-Age: 3600
```

## Testing Checklist

- [ ] React dev server can make GET requests
- [ ] React dev server can make POST requests with JSON body
- [ ] Authorization headers are properly sent
- [ ] Credentials are included in requests
- [ ] Preflight requests work for complex requests
- [ ] Error responses include proper CORS headers
- [ ] Production origins are configured correctly
