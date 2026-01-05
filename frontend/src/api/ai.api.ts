import apiClient from './client';
import type {
  AIGenerationJob,
  GenerateEmailRequest,
  GenerateEmailResponse,
  RefineEmailRequest,
  GenerateSubjectLinesRequest,
  CreateTemplateRequest,
  GenerationJobsListResponse,
} from '@/types/ai.types';

/**
 * AI Generation API endpoints
 */
export const aiApi = {
  /**
   * Generate email content
   */
  generateEmail: async (campaignId: string, data: GenerateEmailRequest): Promise<GenerateEmailResponse> => {
    const response = await apiClient.post<GenerateEmailResponse>(
      `/api/v1/campaigns/${campaignId}/generate`,
      data
    );
    return response.data;
  },

  /**
   * Get generation job status
   */
  getGenerationJob: async (campaignId: string, jobId: string): Promise<AIGenerationJob> => {
    const response = await apiClient.get<AIGenerationJob>(
      `/api/v1/campaigns/${campaignId}/generate/${jobId}`
    );
    return response.data;
  },

  /**
   * List all generation jobs for campaign
   */
  getGenerationJobs: async (
    campaignId: string,
    params?: { page?: number; per_page?: number }
  ): Promise<GenerationJobsListResponse> => {
    const response = await apiClient.get<GenerationJobsListResponse>(
      `/api/v1/campaigns/${campaignId}/generate`,
      { params }
    );
    return response.data;
  },

  /**
   * Cancel generation job
   */
  cancelGenerationJob: async (campaignId: string, jobId: string): Promise<AIGenerationJob> => {
    const response = await apiClient.post<AIGenerationJob>(
      `/api/v1/campaigns/${campaignId}/generate/${jobId}/cancel`
    );
    return response.data;
  },

  /**
   * Create template from generated variant
   */
  createTemplateFromVariant: async (
    campaignId: string,
    jobId: string,
    data: CreateTemplateRequest
  ): Promise<{ message: string; template_id: string }> => {
    const response = await apiClient.post<{ message: string; template_id: string }>(
      `/api/v1/campaigns/${campaignId}/generate/${jobId}/create-template`,
      data
    );
    return response.data;
  },

  /**
   * Refine existing email
   */
  refineEmail: async (
    campaignId: string,
    templateId: string,
    data: RefineEmailRequest
  ): Promise<GenerateEmailResponse> => {
    const response = await apiClient.post<GenerateEmailResponse>(
      `/api/v1/campaigns/${campaignId}/templates/${templateId}/refine`,
      data
    );
    return response.data;
  },

  /**
   * Generate subject lines
   */
  generateSubjectLines: async (
    campaignId: string,
    data: GenerateSubjectLinesRequest
  ): Promise<GenerateEmailResponse> => {
    const response = await apiClient.post<GenerateEmailResponse>(
      `/api/v1/campaigns/${campaignId}/subject-lines`,
      data
    );
    return response.data;
  },

  /**
   * Regenerate with different options
   */
  regenerateEmail: async (
    campaignId: string,
    data: GenerateEmailRequest
  ): Promise<GenerateEmailResponse> => {
    const response = await apiClient.post<GenerateEmailResponse>(
      `/api/v1/campaigns/${campaignId}/regenerate`,
      data
    );
    return response.data;
  },
};
