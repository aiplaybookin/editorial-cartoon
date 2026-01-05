/**
 * User model
 */
export interface User {
  id: string;
  email: string;
  full_name: string;
  organization_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * Login request
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * Login response
 */
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

/**
 * Register request
 */
export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}

/**
 * Register response
 */
export interface RegisterResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

/**
 * Forgot password request
 */
export interface ForgotPasswordRequest {
  email: string;
}

/**
 * Reset password request
 */
export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

/**
 * Change password request
 */
export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}
