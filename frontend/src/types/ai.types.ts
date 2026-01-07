/**
 * Job status enum
 */
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';

/**
 * Tone options
 */
export type ToneOption =
  | 'professional'
  | 'friendly'
  | 'formal'
  | 'casual'
  | 'urgent'
  | 'enthusiastic';

/**
 * Length options
 */
export type LengthOption = 'short' | 'medium' | 'long';

/**
 * Personalization level
 */
export type PersonalizationLevel = 'low' | 'medium' | 'high';

/**
 * Subject line style
 */
export type SubjectLineStyle =
  | 'benefit-driven'
  | 'question'
  | 'urgency'
  | 'curiosity'
  | 'social-proof'
  | 'personalized';

/**
 * Email variant
 */
export interface EmailVariant {
  subject_line: string;
  preview_text: string;
  html_content: string;
  plain_text_content: string;
  confidence_score: number;
  reasoning: string;
}

/**
 * Generated content
 */
export interface GeneratedContent {
  variants: EmailVariant[];
}

/**
 * Generation options
 */
export interface GenerationOptions {
  tone?: ToneOption;
  length?: LengthOption;
  personalization_level?: PersonalizationLevel;
  variants_count?: number;
  temperature?: number;
}

/**
 * AI Generation job
 */
export interface AIGenerationJob {
  id: string;
  campaign_id: string;
  user_id: string;
  status: JobStatus;
  job_type: string;
  user_prompt: string;
  generation_options?: GenerationOptions;
  context_override?: string;
  model_used?: string;
  tokens_used?: number;
  generated_content?: GeneratedContent;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Generate email request
 */
export interface GenerateEmailRequest {
  user_prompt: string;
  generation_options?: GenerationOptions;
  context_override?: string;
}

/**
 * Generate email response
 */
export interface GenerateEmailResponse {
  id: string;
  campaign_id: string;
  status: JobStatus;
  job_type: string;
  estimated_completion_seconds?: number;
  created_at: string;
}

/**
 * Refine email request
 */
export interface RefineEmailRequest {
  refinement_instructions: string;
  generation_options?: GenerationOptions;
}

/**
 * Generate subject lines request
 */
export interface GenerateSubjectLinesRequest {
  email_content: string;
  styles?: SubjectLineStyle[];
  count?: number;
}

/**
 * Create template request
 */
export interface CreateTemplateRequest {
  variant_index: number;
  template_name?: string;
}

/**
 * Generation jobs list response
 */
export interface GenerationJobsListResponse {
  items: AIGenerationJob[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
