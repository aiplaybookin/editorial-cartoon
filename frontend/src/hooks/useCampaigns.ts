import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { campaignsApi } from '@/api/campaigns.api';
import { QUERY_KEYS, ROUTES } from '@/utils/constants';
import type {
  CampaignCreate,
  CampaignUpdate,
  ScheduleCampaignRequest,
} from '@/types/campaign.types';

/**
 * Hook for fetching campaigns list with pagination and filters
 */
export const useCampaigns = (params?: {
  page?: number;
  per_page?: number;
  search?: string;
  status?: string;
}) => {
  return useQuery({
    queryKey: QUERY_KEYS.CAMPAIGNS(params),
    queryFn: () => campaignsApi.getCampaigns(params),
    staleTime: 30 * 1000, // 30 seconds
  });
};

/**
 * Hook for fetching campaign statistics
 */
export const useCampaignStats = () => {
  return useQuery({
    queryKey: QUERY_KEYS.CAMPAIGN_STATS,
    queryFn: () => campaignsApi.getCampaignStats(),
    staleTime: 60 * 1000, // 1 minute
  });
};

/**
 * Hook for fetching a single campaign
 */
export const useCampaign = (id: string) => {
  return useQuery({
    queryKey: QUERY_KEYS.CAMPAIGN(id),
    queryFn: () => campaignsApi.getCampaign(id),
    enabled: !!id,
    staleTime: 30 * 1000,
  });
};

/**
 * Hook for creating a campaign
 */
export const useCreateCampaign = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CampaignCreate) => campaignsApi.createCampaign(data),
    onSuccess: (campaign) => {
      toast.success('Campaign created successfully!');

      // Invalidate campaigns list
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });

      // Redirect to campaign detail page
      navigate(ROUTES.CAMPAIGN_DETAIL(campaign.id));
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to create campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for updating a campaign
 */
export const useUpdateCampaign = (id: string) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CampaignUpdate) => campaignsApi.updateCampaign(id, data),
    onSuccess: () => {
      toast.success('Campaign updated successfully!');

      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN(id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to update campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for deleting a campaign
 */
export const useDeleteCampaign = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.deleteCampaign(id),
    onSuccess: () => {
      toast.success('Campaign deleted successfully!');

      // Invalidate campaigns list
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });

      // Navigate to campaigns list
      navigate(ROUTES.CAMPAIGNS);
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to delete campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for duplicating a campaign
 */
export const useDuplicateCampaign = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.duplicateCampaign(id),
    onSuccess: (campaign) => {
      toast.success('Campaign duplicated successfully!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });

      navigate(ROUTES.CAMPAIGN_DETAIL(campaign.id));
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to duplicate campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for archiving a campaign
 */
export const useArchiveCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.archiveCampaign(id),
    onSuccess: () => {
      toast.success('Campaign archived!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to archive campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for scheduling a campaign
 */
export const useScheduleCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ScheduleCampaignRequest }) =>
      campaignsApi.scheduleCampaign(id, data),
    onSuccess: (campaign) => {
      toast.success('Campaign scheduled successfully!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN(campaign.id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to schedule campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for sending a campaign immediately
 */
export const useSendCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.sendCampaign(id),
    onSuccess: (campaign) => {
      toast.success('Campaign is being sent!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN(campaign.id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to send campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for pausing a campaign
 */
export const usePauseCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.pauseCampaign(id),
    onSuccess: (campaign) => {
      toast.success('Campaign paused!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN(campaign.id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to pause campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for resuming a campaign
 */
export const useResumeCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.resumeCampaign(id),
    onSuccess: (campaign) => {
      toast.success('Campaign resumed!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN(campaign.id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to resume campaign';
      toast.error(message);
    },
  });
};

/**
 * Hook for cancelling a scheduled campaign
 */
export const useCancelCampaign = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => campaignsApi.cancelCampaign(id),
    onSuccess: (campaign) => {
      toast.success('Campaign cancelled!');

      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN(campaign.id) });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGNS() });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.CAMPAIGN_STATS });
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || 'Failed to cancel campaign';
      toast.error(message);
    },
  });
};
