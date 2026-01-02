"""
Prompt templates for AI content generation
"""
from typing import Dict, Any, Optional


def build_system_prompt(company_profile: Optional[Dict[str, Any]] = None) -> str:
    """
    Build system prompt with company context
    
    Args:
        company_profile: Company profile data
        
    Returns:
        System prompt string
    """
    base_prompt = """You are an expert email marketing copywriter specializing in B2B campaigns.
Your goal is to create compelling, professional email content that drives engagement and conversions.

Key principles:
- Write clear, benefit-driven copy
- Use active voice and strong verbs
- Create compelling subject lines that improve open rates
- Include clear calls-to-action
- Personalize content based on audience
- Follow email best practices (avoid spam triggers, keep mobile-friendly)
- Respect brand voice and compliance requirements"""

    if company_profile:
        brand_context = f"""

Company Context:
- Brand Voice: {company_profile.get('brand_voice', 'Professional and trustworthy')}
- Value Propositions: {', '.join(company_profile.get('value_propositions', []))}
- Target Audience: {company_profile.get('target_audience', {})}
- Competitive Advantages: {', '.join(company_profile.get('competitive_advantages', []))}"""
        
        if company_profile.get('compliance_requirements'):
            brand_context += f"""
- Compliance Requirements: {', '.join(company_profile.get('compliance_requirements', []))}"""
        
        if company_profile.get('brand_guidelines', {}).get('forbidden_words'):
            brand_context += f"""
- Forbidden Words/Phrases: {', '.join(company_profile.get('brand_guidelines', {}).get('forbidden_words', []))}"""
        
        base_prompt += brand_context
    
    return base_prompt


def build_generation_prompt(
    user_prompt: str,
    campaign_data: Dict[str, Any],
    generation_options: Dict[str, Any],
    company_profile: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build complete generation prompt
    
    Args:
        user_prompt: User's instructions
        campaign_data: Campaign information
        generation_options: Generation options
        company_profile: Company profile data
        
    Returns:
        Complete prompt string
    """
    prompt = f"""Generate a professional email campaign with the following requirements:

USER INSTRUCTIONS:
{user_prompt}

CAMPAIGN DETAILS:
- Campaign Name: {campaign_data.get('name')}
- Primary Goal: {campaign_data.get('primary_goal')}
- Target Audience: {campaign_data.get('target_audience_description')}
- Success Criteria: {campaign_data.get('success_criteria', 'Not specified')}"""
    
    # Add objectives
    if campaign_data.get('objectives'):
        prompt += "\n- Campaign Objectives:"
        for obj in campaign_data['objectives']:
            prompt += f"\n  * {obj.get('description')} (KPI: {obj.get('kpi_name')}, Target: {obj.get('target_value')})"
    
    # Add generation options
    prompt += f"""

GENERATION REQUIREMENTS:
- Tone: {generation_options.get('tone', 'professional')}
- Length: {generation_options.get('length', 'medium')} (~{get_word_count_for_length(generation_options.get('length', 'medium'))} words)
- Personalization Level: {generation_options.get('personalization_level', 'high')}
- Include CTA: {generation_options.get('include_cta', True)}"""
    
    if generation_options.get('cta_text'):
        prompt += f"\n- CTA Text: {generation_options.get('cta_text')}"
    
    if generation_options.get('focus_areas'):
        prompt += f"\n- Focus Areas: {', '.join(generation_options.get('focus_areas'))}"
    
    # Add variant count
    variants_count = generation_options.get('variants_count', 1)
    if variants_count > 1:
        prompt += f"""

Generate {variants_count} different variants with varying approaches:
- Variant 1: Lead with the main benefit
- Variant 2: Start with a compelling question or statistic
- Variant 3: Use social proof or case study approach"""
        if variants_count > 3:
            prompt += "\n- Additional variants: Try different angles and messaging"
    
    prompt += """

OUTPUT FORMAT:
For each variant, provide:
1. Subject Line (compelling, under 50 characters)
2. Preview Text / Preheader (complementary to subject, under 100 characters)
3. HTML Email Content (properly structured with header, body, CTA, footer)
4. Plain Text Version (formatted for readability)
5. Confidence Score (0-1, how confident you are this will perform well)
6. Brief Reasoning (why this approach should work)

Return the response as a JSON object with this structure:
{
  "variants": [
    {
      "variant_id": 1,
      "subject_line": "...",
      "preview_text": "...",
      "html_content": "...",
      "plain_text_content": "...",
      "confidence_score": 0.92,
      "reasoning": "..."
    }
  ]
}

HTML Content Guidelines:
- Use semantic HTML with proper structure
- Include responsive design (mobile-friendly)
- Use inline CSS for email client compatibility
- Include proper alt text for images
- Ensure CTA button is prominent and clickable
- Include unsubscribe link in footer
- Keep total width to 600px max for email clients

Plain Text Guidelines:
- Well-formatted with proper line breaks
- Include all links as full URLs
- Maintain clear hierarchy
- Easy to scan and read"""
    
    return prompt


def build_refinement_prompt(
    original_content: Dict[str, Any],
    refinement_instructions: str,
    sections_to_change: Optional[list] = None
) -> str:
    """
    Build prompt for content refinement
    
    Args:
        original_content: Original email content
        refinement_instructions: User's refinement instructions
        sections_to_change: Specific sections to modify
        
    Returns:
        Refinement prompt
    """
    prompt = f"""Refine the following email content based on these instructions:

REFINEMENT INSTRUCTIONS:
{refinement_instructions}

ORIGINAL EMAIL:
Subject: {original_content.get('subject_line')}
Preview Text: {original_content.get('preview_text', 'N/A')}

HTML Content:
{original_content.get('html_content')}

Plain Text Content:
{original_content.get('plain_text_content')}"""
    
    if sections_to_change:
        prompt += f"""

SECTIONS TO MODIFY:
Focus your changes on: {', '.join(sections_to_change)}
Keep other sections unchanged unless necessary for flow."""
    
    prompt += """

OUTPUT FORMAT:
Return the refined email as a JSON object:
{
  "subject_line": "...",
  "preview_text": "...",
  "html_content": "...",
  "plain_text_content": "...",
  "changes_made": "Brief description of what was changed and why",
  "confidence_score": 0.95
}

Maintain the same email structure and formatting standards."""
    
    return prompt


def build_subject_line_prompt(
    email_content: Optional[str] = None,
    campaign_context: Optional[Dict[str, Any]] = None,
    count: int = 5,
    style: Optional[str] = None
) -> str:
    """
    Build prompt for subject line generation
    
    Args:
        email_content: Email body content
        campaign_context: Campaign information
        count: Number of variants
        style: Preferred style
        
    Returns:
        Subject line generation prompt
    """
    prompt = f"""Generate {count} compelling email subject lines"""
    
    if style:
        prompt += f" with a {style} approach"
    
    prompt += ".\n\n"
    
    if email_content:
        prompt += f"""EMAIL CONTENT:
{email_content[:1000]}...

Generate subject lines that accurately represent this email content."""
    
    if campaign_context:
        prompt += f"""

CAMPAIGN CONTEXT:
- Goal: {campaign_context.get('primary_goal')}
- Target Audience: {campaign_context.get('target_audience_description')}"""
    
    prompt += f"""

SUBJECT LINE BEST PRACTICES:
- Keep under 50 characters (ideal: 30-40)
- Front-load important information
- Create curiosity or urgency
- Be specific and clear
- Avoid spam trigger words
- Use personalization when appropriate
- A/B test different approaches

GENERATE {count} VARIANTS WITH DIFFERENT APPROACHES:
1. Benefit-focused: Lead with the main value proposition
2. Question-based: Engage with a compelling question
3. Urgency/Scarcity: Create time-sensitive motivation
4. Social proof: Reference success or popularity
5. Curiosity: Tease valuable information"""
    
    if count > 5:
        prompt += "\n6+ Additional creative approaches"
    
    prompt += """

OUTPUT FORMAT:
{
  "variants": [
    {
      "variant_id": 1,
      "subject_line": "...",
      "preview_text": "...",
      "confidence_score": 0.92,
      "reasoning": "Why this should work"
    }
  ]
}"""
    
    return prompt


def build_optimization_prompt(
    email_content: Dict[str, Any],
    optimization_goals: list
) -> str:
    """
    Build prompt for email optimization
    
    Args:
        email_content: Current email content
        optimization_goals: List of goals (e.g., 'increase_clicks', 'improve_clarity')
        
    Returns:
        Optimization prompt
    """
    prompt = f"""Optimize the following email to achieve these goals: {', '.join(optimization_goals)}

CURRENT EMAIL:
Subject: {email_content.get('subject_line')}
Preview Text: {email_content.get('preview_text', 'N/A')}

Content:
{email_content.get('html_content')}

OPTIMIZATION GOALS:"""
    
    goal_descriptions = {
        'increase_clicks': 'Improve click-through rate with stronger CTAs and more compelling copy',
        'improve_clarity': 'Make the message clearer and easier to understand',
        'strengthen_cta': 'Make the call-to-action more prominent and persuasive',
        'add_urgency': 'Create time-sensitive motivation to act',
        'personalize': 'Increase personalization and relevance',
        'improve_mobile': 'Optimize for mobile reading experience',
        'reduce_length': 'Make more concise without losing key information',
        'add_social_proof': 'Include testimonials or trust signals'
    }
    
    for goal in optimization_goals:
        desc = goal_descriptions.get(goal, goal.replace('_', ' ').title())
        prompt += f"\n- {desc}"
    
    prompt += """

Provide:
1. Optimized email content
2. Specific changes made and why
3. Expected impact on each goal
4. Confidence score

OUTPUT FORMAT:
{
  "optimized_content": {
    "subject_line": "...",
    "preview_text": "...",
    "html_content": "...",
    "plain_text_content": "..."
  },
  "changes": [
    {
      "section": "CTA",
      "change": "Strengthened button copy from 'Learn More' to 'Get Started Today'",
      "expected_impact": "Should increase clicks by creating more action-oriented language"
    }
  ],
  "confidence_score": 0.88
}"""
    
    return prompt


def get_word_count_for_length(length: str) -> str:
    """Get approximate word count for length option"""
    word_counts = {
        'short': '100-150',
        'medium': '200-300',
        'long': '400-500'
    }
    return word_counts.get(length, '200-300')