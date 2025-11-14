import axios from "axios";
import type { DashboardResponse, AdvisoryResponse } from "../types/fusion";

// ============================================================================
// Community/Post Types
// ============================================================================

export interface Post {
  id: number;
  content: string;
  author_id: number;
  author?: {
    id: number;
    name: string | null;
    email: string;
  };
  author_name?: string | null;
  region?: string | null;
  likes_count: number;
  comments_count: number;
  image_url?: string | null;
  created_at: string;
  is_liked: boolean;
}

export interface CreatePostData {
  content: string;
  region?: string;
  image_url?: string;
}

export interface Comment {
  id: number;
  post_id: number;
  user_id: number;
  author_name?: string | null;
  content: string;
  created_at: string;
}

export interface CreateCommentData {
  content: string;
}

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
    // Don't add Authorization header to public/auth endpoints
    const url = config.url || "";
    const isPublicEndpoint = 
      url.includes("/auth/signup") ||
      url.includes("/auth/login") ||
      url.includes("/admin/login");
    
    // Only add token for protected endpoints
    if (!isPublicEndpoint) {
      const token = localStorage.getItem("access_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
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
    const status = error.response?.status;
    const url: string = error.config?.url || "";

    // Don't redirect on auth routes (login/signup) - let them handle errors
    const isAuthRoute =
      url.includes("/auth/login") ||
      url.includes("/auth/signup") ||
      url.includes("/admin/login");

    if (status === 401 && !isAuthRoute) {
      // Unauthorized during app usage - clear token and redirect to login
      localStorage.removeItem("access_token");
      localStorage.removeItem("user_data");
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
  latitude?: number;
  longitude?: number;
}

export interface User {
  name: string;
  email: string;
  phone?: string;
  userType: string;
  crop?: string;
  location?: string;
  state?: string;
  district?: string;
  village?: string;
}

export interface UserUpdate {
  name?: string;
  phone?: string;
  crop?: string;
  location?: string;
  state?: string;
  district?: string;
  village?: string;
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
    // Handle different error scenarios with specific messages
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;

      if (status === 401) {
        throw new Error("Invalid email or password. Please check your credentials and try again.");
      } else if (status === 400) {
        throw new Error(detail || "Invalid request. Please check your input.");
      } else if (status === 500) {
        throw new Error("Server error. Please try again later.");
      } else if (status === 404) {
        throw new Error("Service not found. Please contact support.");
      } else {
        throw new Error(detail || "Login failed. Please try again.");
      }
    } else if (error.request) {
      // Request was made but no response received
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      // Something else happened
      throw new Error(error.message || "An unexpected error occurred. Please try again.");
    }
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
    // Handle different error scenarios with specific messages
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;

      if (status === 409) {
        throw new Error("This email is already registered. Please try logging in instead.");
      } else if (status === 400) {
        throw new Error(detail || "Invalid information provided. Please check your input.");
      } else if (status === 401) {
        throw new Error("Unauthorized. Please try again.");
      } else if (status === 500) {
        throw new Error("Server error. Please try again later.");
      } else if (status === 404) {
        throw new Error("Service not found. Please contact support.");
      } else {
        throw new Error(detail || "Failed to create account. Please try again.");
      }
    } else if (error.request) {
      // Request was made but no response received
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      // Something else happened
      throw new Error(error.message || "An unexpected error occurred. Please try again.");
    }
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
    // Use /auth/me endpoint which requires authentication
    const response = await api.get<User>("/auth/me");
    
    // Update localStorage with fresh data
    if (response.data) {
      localStorage.setItem("user_data", JSON.stringify(response.data));
    }
    
    return response.data;
  } catch (error: any) {
    // Fallback to stored user data if backend call fails
    const storedUser = getUser();
    if (storedUser) {
      return storedUser;
    }
    // If no stored user, throw the error
    if (error.response) {
      const detail = error.response.data?.detail || error.response.data?.message;
      throw new Error(detail || "Failed to get user information.");
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your connection.");
    } else {
      throw new Error(error.message || "Failed to get user information.");
    }
  }
};

// Update user profile
export const updateProfile = async (userData: UserUpdate): Promise<User> => {
  try {
    const response = await api.patch<User>("/auth/profile", userData);
    
    // Update localStorage with fresh data
    if (response.data) {
      localStorage.setItem("user_data", JSON.stringify(response.data));
    }
    
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 401) {
        throw new Error("Unauthorized. Please log in again.");
      } else if (status === 404) {
        throw new Error("User not found.");
      } else if (status === 500) {
        throw new Error("Server error. Please try again later.");
      } else {
        throw new Error(detail || "Failed to update profile. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while updating profile.");
    }
  }
};

// ============================================================================
// Fusion Engine API Functions
// ============================================================================

/**
 * Fetch dashboard data from Fusion Engine
 * @param crop - Optional crop name to filter/highlight
 * Returns weather, market prices, alerts, and crop health data
 */
export const getDashboardData = async (crop?: string): Promise<DashboardResponse> => {
  try {
    const url = crop ? `/fusion/dashboard?crop=${encodeURIComponent(crop)}` : "/fusion/dashboard";
    const response = await api.get<DashboardResponse>(url);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 500) {
        throw new Error("Server error while loading dashboard data. Please try again later.");
      } else if (status === 404) {
        throw new Error("Dashboard service not found. Please contact support.");
      } else {
        throw new Error(detail || "Failed to load dashboard data. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while loading dashboard data.");
    }
  }
};

/**
 * Fetch advisory data for a specific crop from Fusion Engine
 * @param cropName - Name of the crop (e.g., "cotton", "wheat", "rice")
 */
export const getAdvisory = async (cropName: string): Promise<AdvisoryResponse> => {
  try {
    const response = await api.get<AdvisoryResponse>(`/fusion/advisory/${cropName.toLowerCase()}`);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 404) {
        throw new Error(`Advisory not found for ${cropName}. Please try a different crop.`);
      } else if (status === 500) {
        throw new Error("Server error while loading advisory. Please try again later.");
      } else {
        throw new Error(detail || "Failed to load advisory. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while loading advisory.");
    }
  }
};

// ============================================================================
// Community API Functions
// ============================================================================

/**
 * Fetch all community posts
 */
export const getCommunityPosts = async (): Promise<Post[]> => {
  try {
    const response = await api.get<Post[]>("/community/posts");
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 401) {
        throw new Error("Please login to view community posts.");
      } else if (status === 500) {
        throw new Error("Server error while loading posts. Please try again later.");
      } else {
        throw new Error(detail || "Failed to load posts. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while loading posts.");
    }
  }
};

/**
 * Create a new post
 */
export const createPost = async (postData: CreatePostData): Promise<Post> => {
  try {
    const response = await api.post<Post>("/community/posts", postData);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 401) {
        throw new Error("Please login to create a post.");
      } else if (status === 400) {
        throw new Error(detail || "Invalid post data. Please check your input.");
      } else if (status === 500) {
        throw new Error("Server error while creating post. Please try again later.");
      } else {
        throw new Error(detail || "Failed to create post. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while creating post.");
    }
  }
};

/**
 * Like or unlike a post
 */
export const togglePostLike = async (postId: number): Promise<{ post_id: number; likes_count: number; is_liked: boolean }> => {
  try {
    const response = await api.post<{ post_id: number; likes_count: number; is_liked: boolean }>(`/community/posts/${postId}/like`);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 401) {
        throw new Error("Please login to like posts.");
      } else if (status === 404) {
        throw new Error("Post not found.");
      } else if (status === 500) {
        throw new Error("Server error while liking post. Please try again later.");
      } else {
        throw new Error(detail || "Failed to like post. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while liking post.");
    }
  }
};

/**
 * Get comments for a post
 */
export const getPostComments = async (postId: number): Promise<Comment[]> => {
  try {
    const response = await api.get<Comment[]>(`/community/posts/${postId}/comments`);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 401) {
        throw new Error("Please login to view comments.");
      } else if (status === 404) {
        throw new Error("Post not found.");
      } else if (status === 500) {
        throw new Error("Server error while loading comments. Please try again later.");
      } else {
        throw new Error(detail || "Failed to load comments. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while loading comments.");
    }
  }
};

/**
 * Add a comment to a post
 */
export const createComment = async (postId: number, commentData: CreateCommentData): Promise<Comment> => {
  try {
    const response = await api.post<Comment>(`/community/posts/${postId}/comments`, commentData);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || error.response.data?.message;
      
      if (status === 401) {
        throw new Error("Please login to comment.");
      } else if (status === 404) {
        throw new Error("Post not found.");
      } else if (status === 400) {
        throw new Error(detail || "Invalid comment data. Please check your input.");
      } else if (status === 500) {
        throw new Error("Server error while creating comment. Please try again later.");
      } else {
        throw new Error(detail || "Failed to create comment. Please try again.");
      }
    } else if (error.request) {
      throw new Error("Unable to reach server. Please check your internet connection and try again.");
    } else {
      throw new Error(error.message || "An unexpected error occurred while creating comment.");
    }
  }
};

