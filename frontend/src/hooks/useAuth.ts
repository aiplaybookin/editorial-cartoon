import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { authApi } from '@/api/auth.api';
import { useAuthStore } from '@/store/authStore';
import { QUERY_KEYS, ROUTES } from '@/utils/constants';
import type {
  LoginRequest,
  RegisterRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
  ChangePasswordRequest,
} from '@/types/auth.types';

/**
 * Hook for user login
 */
export const useLogin = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  return useMutation({
    mutationFn: (data: LoginRequest) => authApi.login(data),
    onSuccess: (response) => {
      // Store tokens and user in auth store
      login(
        {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
        },
        response.user
      );

      toast.success(`Welcome back, ${response.user.full_name}!`);

      // Redirect to dashboard
      navigate(ROUTES.DASHBOARD);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Login failed. Please check your credentials.';
      toast.error(message);
    },
  });
};

/**
 * Hook for user registration
 */
export const useRegister = () => {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  return useMutation({
    mutationFn: (data: RegisterRequest) => authApi.register(data),
    onSuccess: (response) => {
      // Auto-login after successful registration
      login(
        {
          access_token: response.access_token,
          refresh_token: response.refresh_token,
        },
        response.user
      );

      toast.success(`Welcome, ${response.user.full_name}! Your account has been created.`);

      // Redirect to dashboard
      navigate(ROUTES.DASHBOARD);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(message);
    },
  });
};

/**
 * Hook for user logout
 */
export const useLogout = () => {
  const navigate = useNavigate();
  const logout = useAuthStore((state) => state.logout);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      // Clear auth store
      logout();

      // Clear all cached queries
      queryClient.clear();

      toast.success('Logged out successfully');

      // Redirect to home
      navigate(ROUTES.HOME);
    },
    onError: (error: any) => {
      // Even if API call fails, logout locally
      logout();
      queryClient.clear();

      const message = error?.response?.data?.detail || 'Logged out';
      toast.success(message);

      navigate(ROUTES.HOME);
    },
  });
};

/**
 * Hook for getting current user
 */
export const useCurrentUser = () => {
  const { isAuthenticated } = useAuthStore();

  return useQuery({
    queryKey: QUERY_KEYS.CURRENT_USER,
    queryFn: () => authApi.getCurrentUser(),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

/**
 * Hook for forgot password
 */
export const useForgotPassword = () => {
  return useMutation({
    mutationFn: (data: ForgotPasswordRequest) => authApi.forgotPassword(data),
    onSuccess: (response) => {
      toast.success(response.message || 'Password reset link sent to your email');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to send reset link. Please try again.';
      toast.error(message);
    },
  });
};

/**
 * Hook for reset password
 */
export const useResetPassword = () => {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (data: ResetPasswordRequest) => authApi.resetPassword(data),
    onSuccess: (response) => {
      toast.success(response.message || 'Password reset successful! Please login with your new password.');

      // Redirect to login page
      navigate(ROUTES.LOGIN);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to reset password. The link may have expired.';
      toast.error(message);
    },
  });
};

/**
 * Hook for change password
 */
export const useChangePassword = () => {
  return useMutation({
    mutationFn: (data: ChangePasswordRequest) => authApi.changePassword(data),
    onSuccess: (response) => {
      toast.success(response.message || 'Password changed successfully');
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to change password. Please try again.';
      toast.error(message);
    },
  });
};
