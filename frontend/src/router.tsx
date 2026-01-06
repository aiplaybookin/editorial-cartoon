import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Pages
import { HomePage } from '@/pages/landing/HomePage';
import { LoginPage } from '@/pages/auth/LoginPage';
import { SignupPage } from '@/pages/auth/SignupPage';
import { ForgotPasswordPage } from '@/pages/auth/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/auth/ResetPasswordPage';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
import { CampaignsListPage } from '@/pages/campaigns/CampaignsListPage';
import { CampaignCreatePage } from '@/pages/campaigns/CampaignCreatePage';
import { CampaignDetailPage } from '@/pages/campaigns/CampaignDetailPage';
import { NotFoundPage } from '@/pages/NotFoundPage';

/**
 * Application router configuration
 */
export const router = createBrowserRouter([
  // Public routes
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/signup',
    element: <SignupPage />,
  },
  {
    path: '/forgot-password',
    element: <ForgotPasswordPage />,
  },
  {
    path: '/reset-password',
    element: <ResetPasswordPage />,
  },

  // Protected routes
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/campaigns',
    element: (
      <ProtectedRoute>
        <CampaignsListPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/campaigns/new',
    element: (
      <ProtectedRoute>
        <CampaignCreatePage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/campaigns/:id',
    element: (
      <ProtectedRoute>
        <CampaignDetailPage />
      </ProtectedRoute>
    ),
  },

  // 404
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
