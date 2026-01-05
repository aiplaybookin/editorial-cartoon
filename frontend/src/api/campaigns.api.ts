import apiClient from './client';
import type {
  Campaign,
  CampaignCreate,
  CampaignUpdate,
  CampaignListResponse,
  CampaignStats,
  CampaignObjective,
  CampaignObjectiveCreate,
  CampaignObjectiveUpdate,
  ScheduleCampaignRequest,
} from '@/types/campaign.types';

/**
 * Campaign API endpoints
 */
export const campaignsApi = {
  /**
   * Get all campaigns with pagination and filters
   */
  getCampaigns: async (params?: {
    page?: number;
    per_page?: number;
    search?: string;
    status?: string;
  }): Promise<CampaignListResponse> => {
    const response = await apiClient.get<CampaignListResponse>('/api/v1/campaigns', { params });
    return response.data;
  },

  /**
   * Get campaign statistics
   */
  getCampaignStats: async (): Promise<CampaignStats> => {
    const response = await apiClient.get<CampaignStats>('/api/v1/campaigns/stats');
    return response.data;
  },

  /**
   * Get campaign by ID
   */
  getCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.get<Campaign>(`/api/v1/campaigns/${id}`);
    return response.data;
  },

  /**
   * Create new campaign
   */
  createCampaign: async (data: CampaignCreate): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>('/api/v1/campaigns', data);
    return response.data;
  },

  /**
   * Update campaign
   */
  updateCampaign: async (id: string, data: CampaignUpdate): Promise<Campaign> => {
    const response = await apiClient.patch<Campaign>(`/api/v1/campaigns/${id}`, data);
    return response.data;
  },

  /**
   * Delete campaign
   */
  deleteCampaign: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/campaigns/${id}`);
  },

  /**
   * Duplicate campaign
   */
  duplicateCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/duplicate`);
    return response.data;
  },

  /**
   * Archive campaign
   */
  archiveCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/archive`);
    return response.data;
  },

  /**
   * Schedule campaign
   */
  scheduleCampaign: async (id: string, data: ScheduleCampaignRequest): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/schedule`, data);
    return response.data;
  },

  /**
   * Send campaign immediately
   */
  sendCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/send`);
    return response.data;
  },

  /**
   * Pause campaign
   */
  pauseCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/pause`);
    return response.data;
  },

  /**
   * Resume campaign
   */
  resumeCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/resume`);
    return response.data;
  },

  /**
   * Cancel campaign
   */
  cancelCampaign: async (id: string): Promise<Campaign> => {
    const response = await apiClient.post<Campaign>(`/api/v1/campaigns/${id}/cancel`);
    return response.data;
  },

  // Objectives
  /**
   * Get campaign objectives
   */
  getObjectives: async (campaignId: string): Promise<CampaignObjective[]> => {
    const response = await apiClient.get<CampaignObjective[]>(`/api/v1/campaigns/${campaignId}/objectives`);
    return response.data;
  },

  /**
   * Create campaign objective
   */
  createObjective: async (campaignId: string, data: CampaignObjectiveCreate): Promise<CampaignObjective> => {
    const response = await apiClient.post<CampaignObjective>(`/api/v1/campaigns/${campaignId}/objectives`, data);
    return response.data;
  },

  /**
   * Update campaign objective
   */
  updateObjective: async (
    campaignId: string,
    objectiveId: string,
    data: CampaignObjectiveUpdate
  ): Promise<CampaignObjective> => {
    const response = await apiClient.patch<CampaignObjective>(
      `/api/v1/campaigns/${campaignId}/objectives/${objectiveId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete campaign objective
   */
  deleteObjective: async (campaignId: string, objectiveId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/campaigns/${campaignId}/objectives/${objectiveId}`);
  },
};
