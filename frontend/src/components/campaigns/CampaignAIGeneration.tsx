import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { aiApi } from '@/api/ai.api';
import { toast } from 'react-hot-toast';
import { Loader2, Wand2 } from 'lucide-react';
import type { GenerateEmailRequest, ToneOption, LengthOption } from '@/types/ai.types';

interface CampaignAIGenerationProps {
    campaignId: string;
}

export const CampaignAIGeneration = ({ campaignId }: CampaignAIGenerationProps) => {
    const [prompt, setPrompt] = useState('');
    const [generatedContent, setGeneratedContent] = useState<any>(null);

    // Generation options state
    const [tone, setTone] = useState<ToneOption>('professional');
    const [length, setLength] = useState<LengthOption>('medium');
    const [variantsCount, setVariantsCount] = useState(2);

    // Poll for job status
    const { data: jobStatus } = useQuery({
        queryKey: ['generation-job', campaignId, generatedContent?.id],
        queryFn: () => aiApi.getGenerationJob(campaignId, generatedContent?.id),
        enabled: !!generatedContent?.id && generatedContent?.status !== 'completed' && generatedContent?.status !== 'failed',
        refetchInterval: (data) => {
            if (data?.state?.data?.status === 'completed' || data?.state?.data?.status === 'failed') {
                return false;
            }
            return 2000; // Poll every 2 seconds
        },
    });

    const generateMutation = useMutation({
        mutationFn: (data: GenerateEmailRequest) => aiApi.generateEmail(campaignId, data),
        onSuccess: (data) => {
            setGeneratedContent({ id: data.job_id, status: 'pending' }); // Store job ID
            toast.success('AI generation started!');
        },
        onError: (error: any) => {
            toast.error(error?.response?.data?.detail || 'Failed to start generation');
        },
    });

    const handleGenerate = () => {
        if (!prompt.trim()) {
            toast.error('Please enter a prompt');
            return;
        }

        generateMutation.mutate({
            user_prompt: prompt,
            generation_options: {
                tone,
                length,
                variants_count: variantsCount,
            },
        });
    };

    const isGenerating = generateMutation.isPending || (jobStatus && jobStatus.status !== 'completed' && jobStatus.status !== 'failed');

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Wand2 className="h-5 w-5 text-purple-600" />
                        AI Content Generator
                    </CardTitle>
                    <CardDescription>
                        Describe your email requirements and let AI generate content variants for you.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="prompt">Prompt</Label>
                        <Textarea
                            id="prompt"
                            placeholder="e.g. Write a product launch email for our new SaaS platform targeting CTOs..."
                            rows={4}
                            value={prompt}
                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setPrompt(e.target.value)}
                            disabled={isGenerating}
                        />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                            <Label>Tone</Label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={tone}
                                onChange={(e) => setTone(e.target.value as ToneOption)}
                                disabled={isGenerating}
                            >
                                <option value="professional">Professional</option>
                                <option value="casual">Casual</option>
                                <option value="friendly">Friendly</option>
                                <option value="formal">Formal</option>
                                <option value="urgent">Urgent</option>
                                <option value="enthusiastic">Enthusiastic</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <Label>Length</Label>
                            <select
                                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                value={length}
                                onChange={(e) => setLength(e.target.value as LengthOption)}
                                disabled={isGenerating}
                            >
                                <option value="short">Short</option>
                                <option value="medium">Medium</option>
                                <option value="long">Long</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <Label>Variants</Label>
                            <Input
                                type="number"
                                min={1}
                                max={5}
                                value={variantsCount}
                                onChange={(e) => setVariantsCount(parseInt(e.target.value))}
                                disabled={isGenerating}
                            />
                        </div>
                    </div>

                    <div className="flex justify-end pt-2">
                        <Button onClick={handleGenerate} disabled={isGenerating}>
                            {isGenerating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Generating...
                                </>
                            ) : (
                                <>
                                    <Wand2 className="mr-2 h-4 w-4" />
                                    Generate Content
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {/* Results Display */}
            {jobStatus && jobStatus.status === 'completed' && jobStatus.generated_content && (
                <div className="space-y-6">
                    <h3 className="text-xl font-semibold">Generated Variants</h3>
                    <div className="grid gap-6">
                        {jobStatus.generated_content.variants.map((variant: any, index: number) => (
                            <Card key={index} className="overflow-hidden">
                                <CardHeader className="bg-muted/50">
                                    <div className="flex justify-between items-start">
                                        <div className="space-y-1">
                                            <CardTitle className="text-base">Variant {index + 1}</CardTitle>
                                            <CardDescription>Targeting: {variant.target_audience || 'General'}</CardDescription>
                                        </div>
                                        {variant.confidence_score && (
                                            <span className="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                                                Score: {Math.round(variant.confidence_score * 100)}%
                                            </span>
                                        )}
                                    </div>
                                </CardHeader>
                                <CardContent className="p-6 space-y-4">
                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-muted-foreground">Subject Line</Label>
                                        <div className="font-medium">{variant.subject_line}</div>
                                    </div>

                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-muted-foreground">Preview Text</Label>
                                        <div className="text-sm">{variant.preview_text}</div>
                                    </div>

                                    <div className="space-y-2">
                                        <Label className="text-sm font-medium text-muted-foreground">Content</Label>
                                        <div className="rounded-md bg-muted p-4 text-sm whitespace-pre-wrap">
                                            {variant.plain_text_content || variant.html_content}
                                        </div>
                                    </div>

                                    {variant.reasoning && (
                                        <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-700">
                                            <p className="font-semibold mb-1">AI Reasoning:</p>
                                            {variant.reasoning}
                                        </div>
                                    )}

                                    <div className="flex justify-end gap-2 pt-2">
                                        <Button variant="outline" size="sm">
                                            Copy
                                        </Button>
                                        <Button size="sm">
                                            Use This Variant
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
