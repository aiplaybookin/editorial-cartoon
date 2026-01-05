/**
 * Campaign status enum
 */
export type CampaignStatus =
  | 'draft'
  | 'generating'
  | 'scheduled'
  | 'sending'
  | 'sent'
  | 'paused'
  | 'archived'
  | 'cancelled';

/**
 * Objective type enum
 */
export type ObjectiveType = 'primary' | 'secondary';

/**
 * Campaign objective
 */
export interface CampaignObjective {
  id: string;
  campaign_id: string;
  objective_type: ObjectiveType;
  description: string;
  kpi_name: string;
  target_value: string;
  priority: number;
  created_at: string;
  updated_at: string;
}

/**
 * Campaign model
 */
export interface Campaign {
  id: string;
  name: string;
  description?: string;
  status: CampaignStatus;
  organization_id: string;
  user_id: string;
  target_audience?: string;
  scheduled_at?: string;
  sent_at?: string;
  created_at: string;
  updated_at: string;
  objectives?: CampaignObjective[];
}

/**
 * Create campaign request
 */
export interface CampaignCreate {
  name: string;
  description?: string;
  target_audience?: string;
  objectives?: CampaignObjectiveCreate[];
}

/**
 * Update campaign request
 */
export interface CampaignUpdate {
  name?: string;
  description?: string;
  target_audience?: string;
}

/**
 * Campaign list response
 */
export interface CampaignListResponse {
  items: Campaign[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

/**
 * Campaign statistics
 */
export interface CampaignStats {
  total_campaigns: number;
  draft_campaigns: number;
  scheduled_campaigns: number;
  sent_campaigns: number;
  active_campaigns: number;
}

/**
 * Create campaign objective
 */
export interface CampaignObjectiveCreate {
  objective_type: ObjectiveType;
  description: string;
  kpi_name: string;
  target_value: string;
  priority?: number;
}

/**
 * Update campaign objective
 */
export interface CampaignObjectiveUpdate {
  objective_type?: ObjectiveType;
  description?: string;
  kpi_name?: string;
  target_value?: string;
  priority?: number;
}

/**
 * Schedule campaign request
 */
export interface ScheduleCampaignRequest {
  scheduled_at: string;
}
