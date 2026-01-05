import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

// Pages
import { HomePage } from '@/pages/landing/HomePage';
import { LoginPage } from '@/pages/auth/LoginPage';
import { SignupPage } from '@/pages/auth/SignupPage';
import { DashboardPage } from '@/pages/dashboard/DashboardPage';
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

  // Protected routes
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },

  // 404
  {
    path: '*',
    element: <NotFoundPage />,
  },
]);
