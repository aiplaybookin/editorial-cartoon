/**
 * Application constants and configuration
 */

export const APP_CONFIG = {
  name: import.meta.env.VITE_APP_NAME || 'Arrakis Marketeer',
  version: import.meta.env.VITE_APP_VERSION || '1.0.0',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true',
  enableDevTools: import.meta.env.VITE_ENABLE_DEV_TOOLS === 'true',
} as const;

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  SIGNUP: '/signup',
  FORGOT_PASSWORD: '/forgot-password',
  RESET_PASSWORD: '/reset-password',
  DASHBOARD: '/dashboard',
  CAMPAIGNS: '/campaigns',
  CAMPAIGN_NEW: '/campaigns/new',
  CAMPAIGN_DETAIL: (id: string) => `/campaigns/${id}`,
  CAMPAIGN_EDIT: (id: string) => `/campaigns/${id}/edit`,
  CAMPAIGN_GENERATE: (id: string) => `/campaigns/${id}/generate`,
  PROFILE: '/profile',
  SETTINGS: '/settings',
} as const;

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  MAX_PAGE_SIZE: 100,
} as const;

export const QUERY_KEYS = {
  // Auth
  CURRENT_USER: ['current-user'],

  // Campaigns
  CAMPAIGNS: (params?: Record<string, unknown>) => ['campaigns', params],
  CAMPAIGN: (id: string) => ['campaign', id],
  CAMPAIGN_STATS: ['campaign-stats'],
  CAMPAIGN_OBJECTIVES: (campaignId: string) => ['campaign-objectives', campaignId],

  // AI Generation
  GENERATION_JOBS: (campaignId: string) => ['generation-jobs', campaignId],
  GENERATION_JOB: (jobId: string) => ['generation-job', jobId],
} as const;

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'accessToken',
  REFRESH_TOKEN: 'refreshToken',
  USER: 'user',
} as const;
