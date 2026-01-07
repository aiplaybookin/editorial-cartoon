import { useQuery } from '@tanstack/react-query';
import { aiApi } from '@/api/ai.api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Loader2, FileText, Clock, CheckCircle, XCircle } from 'lucide-react';
import { format } from 'date-fns';

interface CampaignContentReviewProps {
    campaignId: string;
}

export const CampaignContentReview = ({ campaignId }: CampaignContentReviewProps) => {
    const { data: generationJobs, isLoading, error } = useQuery({
        queryKey: ['generation-jobs', campaignId],
        queryFn: () => aiApi.getGenerationJobs(campaignId),
        refetchInterval: (data) => {
            // Continue polling if there are any pending/processing jobs
            const hasActiveJobs = data?.items?.some(
                (job) => job.status === 'pending' || job.status === 'processing'
            );
            return hasActiveJobs ? 3000 : false;
        },
    });

    if (isLoading) {
        return (
            <Card>
                <CardContent className="flex items-center justify-center py-12">
                    <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card>
                <CardContent className="flex flex-col items-center justify-center py-12 text-gray-500">
                    <XCircle className="h-12 w-12 mb-4 text-red-400" />
                    <p>Failed to load generation jobs</p>
                </CardContent>
            </Card>
        );
    }

    if (!generationJobs?.items || generationJobs.items.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Content Review</CardTitle>
                    <CardDescription>Review and approve AI-generated email content.</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                        <FileText className="h-12 w-12 mb-4 opacity-50" />
                        <p className="text-center">
                            No content generated yet.
                            <br />
                            Use the "AI Generation" tab to create email variants.
                        </p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'completed':
                return <CheckCircle className="h-4 w-4 text-green-500" />;
            case 'failed':
                return <XCircle className="h-4 w-4 text-red-500" />;
            case 'pending':
            case 'processing':
                return <Clock className="h-4 w-4 text-blue-500" />;
            default:
                return <Clock className="h-4 w-4 text-gray-500" />;
        }
    };

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case 'completed':
                return 'default';
            case 'failed':
                return 'destructive';
            case 'processing':
                return 'secondary';
            default:
                return 'outline';
        }
    };

    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Generated Content</CardTitle>
                    <CardDescription>
                        Review AI-generated email variants and select the best one for your campaign.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {generationJobs.items.map((job) => (
                            <Card key={job.id} className="overflow-hidden">
                                <CardHeader className="bg-muted/30">
                                    <div className="flex justify-between items-start">
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                {getStatusIcon(job.status)}
                                                <CardTitle className="text-base">
                                                    Generation Job
                                                </CardTitle>
                                                <Badge variant={getStatusBadgeVariant(job.status)}>
                                                    {job.status}
                                                </Badge>
                                            </div>
                                            <CardDescription className="text-xs">
                                                Created {format(new Date(job.created_at), 'MMM d, yyyy h:mm a')}
                                            </CardDescription>
                                        </div>
                                    </div>
                                </CardHeader>

                                {job.status === 'processing' && (
                                    <CardContent className="py-6">
                                        <div className="flex items-center gap-3 text-sm text-muted-foreground">
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                            <span>Generating content with AI...</span>
                                        </div>
                                    </CardContent>
                                )}

                                {job.status === 'failed' && (
                                    <CardContent className="py-6">
                                        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700">
                                            <p className="font-semibold mb-1">Generation Failed</p>
                                            <p>{job.error_message || 'An error occurred during generation'}</p>
                                        </div>
                                    </CardContent>
                                )}

                                {job.status === 'completed' && job.generated_content?.variants && (
                                    <CardContent className="py-6 space-y-6">
                                        {job.generated_content.variants.map((variant: any, index: number) => (
                                            <div key={index} className="border rounded-lg p-4 space-y-4">
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <h4 className="font-medium">Variant {index + 1}</h4>
                                                        {variant.confidence_score && (
                                                            <span className="text-xs text-muted-foreground">
                                                                Confidence: {Math.round(variant.confidence_score * 100)}%
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>

                                                <div className="space-y-3">
                                                    <div className="space-y-1">
                                                        <Label className="text-xs font-medium text-muted-foreground">
                                                            Subject Line
                                                        </Label>
                                                        <div className="font-medium text-sm">
                                                            {variant.subject_line}
                                                        </div>
                                                    </div>

                                                    {variant.preview_text && (
                                                        <div className="space-y-1">
                                                            <Label className="text-xs font-medium text-muted-foreground">
                                                                Preview Text
                                                            </Label>
                                                            <div className="text-sm text-gray-600">
                                                                {variant.preview_text}
                                                            </div>
                                                        </div>
                                                    )}

                                                    <div className="space-y-1">
                                                        <Label className="text-xs font-medium text-muted-foreground">
                                                            Email Content
                                                        </Label>
                                                        <div className="rounded-md bg-muted p-3 text-sm whitespace-pre-wrap max-h-60 overflow-y-auto">
                                                            {variant.plain_text_content || variant.html_content}
                                                        </div>
                                                    </div>

                                                    {variant.reasoning && (
                                                        <div className="rounded-md bg-blue-50 p-3 text-sm text-blue-700">
                                                            <p className="font-semibold text-xs mb-1">AI Reasoning:</p>
                                                            <p className="text-xs">{variant.reasoning}</p>
                                                        </div>
                                                    )}
                                                </div>

                                                <div className="flex justify-end gap-2 pt-2">
                                                    <Button variant="outline" size="sm">
                                                        Copy
                                                    </Button>
                                                    <Button size="sm">
                                                        Use This Variant
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </CardContent>
                                )}
                            </Card>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};
