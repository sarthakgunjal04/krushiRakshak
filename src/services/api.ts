import axios from "axios";

// Backend API base URL - adjust this if your backend runs on a different port
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupData {
  name: string;
  phone?: string;
  email: string;
  password: string;
  userType: string;
}

export interface User {
  name: string;
  email: string;
  phone?: string;
  userType: string;
}

export interface AuthResponse {
  access_token: string;
  message: string;
  user?: User;
}

// Login function
export const loginUser = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>("/auth/login", credentials);
    
    // Store token and user data in localStorage
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
    }
    if (response.data.user) {
      localStorage.setItem("user_data", JSON.stringify(response.data.user));
    }
    
    return response.data;
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message || "Login failed";
      throw new Error(message);
    }
    throw error;
  }
};

// Signup function
export const signupUser = async (userData: SignupData): Promise<AuthResponse> => {
  try {
    const response = await api.post<AuthResponse>("/auth/signup", userData);
    
    // Store token and user data in localStorage
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
    }
    if (response.data.user) {
      localStorage.setItem("user_data", JSON.stringify(response.data.user));
    }
    
    return response.data;
  } catch (error: any) {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message || "Signup failed";
      throw new Error(message);
    }
    throw error;
  }
};

// Logout function
export const logoutUser = (): void => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("user_data");
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!localStorage.getItem("access_token");
};

// Get stored token
export const getToken = (): string | null => {
  return localStorage.getItem("access_token");
};

// Get stored user data
export const getUser = (): User | null => {
  const userData = localStorage.getItem("user_data");
  if (userData) {
    try {
      return JSON.parse(userData);
    } catch {
      return null;
    }
  }
  return null;
};

// Get current user profile from backend
export const getCurrentUser = async (): Promise<User> => {
  try {
    const user = getUser();
    if (!user) {
      throw new Error("No user data found");
    }
    
    // Try to get user from backend by email
    const response = await api.get<User>(`/auth/user?email=${encodeURIComponent(user.email)}`);
    return response.data;
  } catch (error: any) {
    // Fallback to stored user data if backend call fails
    const storedUser = getUser();
    if (storedUser) {
      return storedUser;
    }
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.detail || error.message || "Failed to get user";
      throw new Error(message);
    }
    throw error;
  }
};

