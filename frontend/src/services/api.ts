import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 10000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API request failed:', error.message);
    return Promise.reject(error);
  }
);
