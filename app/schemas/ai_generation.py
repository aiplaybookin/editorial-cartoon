"""
AI Generation schemas for email content creation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID


# ============================================
# ENUMS
# ============================================

class AIJobStatus(str, Enum):
    """AI generation job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIJobType(str, Enum):
    """AI generation job type"""
    INITIAL_GENERATION = "initial_generation"
    REVISION = "revision"
    REFINEMENT = "refinement"
    AB_VARIANT = "ab_variant"
    SUBJECT_LINE_TEST = "subject_line_test"
    OPTIMIZATION = "optimization"


class ToneEnum(str, Enum):
    """Email tone options"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    FORMAL = "formal"
    CASUAL = "casual"
    URGENT = "urgent"
    ENTHUSIASTIC = "enthusiastic"


class LengthEnum(str, Enum):
    """Email length options"""
    SHORT = "short"  # ~100-150 words
    MEDIUM = "medium"  # ~200-300 words
    LONG = "long"  # ~400-500 words


class PersonalizationLevel(str, Enum):
    """Personalization level"""
    LOW = "low"  # Basic personalization (name, company)
    MEDIUM = "medium"  # Industry-specific content
    HIGH = "high"  # Highly targeted, persona-specific


# ============================================
# GENERATION OPTIONS
# ============================================

class AIGenerationOptions(BaseModel):
    """Options for AI content generation"""
    tone: ToneEnum = Field(
        default=ToneEnum.PROFESSIONAL,
        description="Tone of the email"
    )
    length: LengthEnum = Field(
        default=LengthEnum.MEDIUM,
        description="Email length"
    )
    include_cta: bool = Field(
        default=True,
        description="Include call-to-action"
    )
    cta_text: Optional[str] = Field(
        None,
        max_length=100,
        description="Custom CTA text"
    )
    personalization_level: PersonalizationLevel = Field(
        default=PersonalizationLevel.HIGH,
        description="Level of personalization"
    )
    variants_count: int = Field(
        default=1,
        ge=1,
        le=5,
        description="Number of variants to generate"
    )
    include_preview_text: bool = Field(
        default=True,
        description="Generate preview/preheader text"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="AI creativity level (0=conservative, 1=creative)"
    )
    focus_areas: Optional[List[str]] = Field(
        None,
        description="Specific areas to focus on (e.g., 'cost savings', 'compliance')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "tone": "professional",
                "length": "medium",
                "include_cta": True,
                "cta_text": "Schedule a Demo",
                "personalization_level": "high",
                "variants_count": 3,
                "include_preview_text": True,
                "temperature": 0.7,
                "focus_areas": ["cost savings", "compliance", "efficiency"]
            }
        }


# ============================================
# GENERATION REQUESTS
# ============================================

class AIGenerationRequest(BaseModel):
    """Request for AI content generation"""
    user_prompt: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="User's instructions for content generation"
    )
    generation_options: AIGenerationOptions = Field(
        default_factory=AIGenerationOptions,
        description="Generation options"
    )
    context_override: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context to override or supplement"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_prompt": "Create an email announcing our new AI-powered clinical documentation platform. Focus on how it reduces FDA submission preparation time by 60%. Target audience is clinical research managers at pharmaceutical companies.",
                "generation_options": {
                    "tone": "professional",
                    "length": "medium",
                    "include_cta": True,
                    "cta_text": "Schedule a Demo",
                    "personalization_level": "high",
                    "variants_count": 3
                },
                "context_override": {
                    "additional_context": "Emphasize compliance and security features"
                }
            }
        }


class AIRefinementRequest(BaseModel):
    """Request for refining existing content"""
    template_id: str = Field(
        ...,
        description="ID of template to refine"
    )
    refinement_instructions: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Instructions for refinement"
    )
    sections_to_change: Optional[List[str]] = Field(
        None,
        description="Specific sections to modify (e.g., 'opening', 'cta', 'body')"
    )
    generation_options: Optional[AIGenerationOptions] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "550e8400-e29b-41d4-a716-446655440000",
                "refinement_instructions": "Make the tone more urgent, add social proof with a customer testimonial, and strengthen the CTA",
                "sections_to_change": ["opening", "cta"],
                "generation_options": {
                    "tone": "urgent",
                    "temperature": 0.8
                }
            }
        }


class SubjectLineVariantsRequest(BaseModel):
    """Request for subject line variants"""
    template_id: Optional[str] = Field(
        None,
        description="ID of existing template (optional)"
    )
    email_content: Optional[str] = Field(
        None,
        description="Email content to base subject lines on"
    )
    count: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of subject line variants"
    )
    style: Optional[str] = Field(
        None,
        description="Style preference (e.g., 'question', 'benefit-driven', 'curiosity')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "template_id": "550e8400-e29b-41d4-a716-446655440000",
                "count": 5,
                "style": "benefit-driven"
            }
        }


# ============================================
# GENERATION RESPONSES
# ============================================

class EmailVariant(BaseModel):
    """Single email content variant"""
    variant_id: int = Field(..., description="Variant number")
    subject_line: str = Field(..., description="Email subject line")
    preview_text: Optional[str] = Field(None, description="Preview/preheader text")
    html_content: str = Field(..., description="HTML email content")
    plain_text_content: str = Field(..., description="Plain text version")
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence in this variant"
    )
    reasoning: Optional[str] = Field(
        None,
        description="AI reasoning for this variant"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "variant_id": 1,
                "subject_line": "Transform Your FDA Submissions: 60% Faster Documentation",
                "preview_text": "AI-powered clinical documentation that regulatory teams trust",
                "html_content": "<html>...</html>",
                "plain_text_content": "Plain text version...",
                "confidence_score": 0.92,
                "reasoning": "This variant emphasizes the key benefit (60% faster) and builds trust"
            }
        }


class AIGenerationResponse(BaseModel):
    """Response for AI generation job"""
    id: UUID = Field(..., description="Job ID")
    campaign_id: UUID = Field(..., description="Campaign ID")
    status: AIJobStatus = Field(..., description="Job status")
    job_type: AIJobType = Field(..., description="Job type")
    generated_content: Optional[Dict[str, Any]] = Field(
        None,
        description="Generated content (available when completed)"
    )
    ai_model: Optional[str] = Field(None, description="AI model used")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    estimated_completion_seconds: Optional[int] = Field(
        None,
        description="Estimated time to completion"
    )
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation time")
    started_at: Optional[datetime] = Field(None, description="Job start time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "campaign_id": "660e8400-e29b-41d4-a716-446655440001",
                "status": "completed",
                "job_type": "initial_generation",
                "generated_content": {
                    "variants": [
                        {
                            "variant_id": 1,
                            "subject_line": "Transform Your FDA Submissions",
                            "preview_text": "AI-powered clinical documentation",
                            "html_content": "<html>...</html>",
                            "plain_text_content": "Plain text...",
                            "confidence_score": 0.92
                        }
                    ]
                },
                "ai_model": "claude-sonnet-4-5",
                "tokens_used": 2450,
                "created_at": "2024-12-28T10:00:00Z",
                "completed_at": "2024-12-28T10:00:30Z"
            }
        }


class SubjectLineVariant(BaseModel):
    """Single subject line variant"""
    variant_id: int
    subject_line: str
    preview_text: Optional[str] = None
    confidence_score: float
    reasoning: Optional[str] = None


class SubjectLineVariantsResponse(BaseModel):
    """Response for subject line variants"""
    variants: List[SubjectLineVariant]
    id: UUID
    status: AIJobStatus
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "variants": [
                    {
                        "variant_id": 1,
                        "subject_line": "60% Faster FDA Submissions Start Here",
                        "preview_text": "Transform your clinical documentation process",
                        "confidence_score": 0.94,
                        "reasoning": "Emphasizes quantifiable benefit"
                    }
                ]
            }
        }


class AIGenerationJobList(BaseModel):
    """List of AI generation jobs"""
    jobs: List[AIGenerationResponse]
    total: int
    page: int
    per_page: int
    pages: int