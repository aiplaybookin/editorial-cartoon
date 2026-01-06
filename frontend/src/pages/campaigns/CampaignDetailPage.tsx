import { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignsApi } from '@/api/campaigns.api';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
    DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import { ArrowLeft, Calendar, FileText, BarChart, MoreVertical, Play, Pause, Send, Copy, Archive, Trash2, Edit } from 'lucide-react';
import { ROUTES } from '@/utils/constants';
import { CampaignAIGeneration } from '@/components/campaigns/CampaignAIGeneration';
import { CampaignObjectivesManager } from '@/components/campaigns/CampaignObjectivesManager';
import { CampaignEditDialog } from '@/components/campaigns/CampaignEditDialog';
import { format } from 'date-fns';
import { toast } from 'react-hot-toast';
import { AxiosError } from 'axios';

export const CampaignDetailPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [editDialogOpen, setEditDialogOpen] = useState(false);

    const { data: campaign, isLoading, error } = useQuery({
        queryKey: ['campaign', id],
        queryFn: () => campaignsApi.getCampaign(id!),
        enabled: !!id,
    });

    // Action Mutations
    const sendMutation = useMutation({
        mutationFn: () => campaignsApi.sendCampaign(id!),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] });
            toast.success('Campaign sending started!');
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: AxiosError<any>) => toast.error(err?.response?.data?.detail || 'Failed to send campaign'),
    });

    const pauseMutation = useMutation({
        mutationFn: () => campaignsApi.pauseCampaign(id!),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] });
            toast.success('Campaign paused');
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: AxiosError<any>) => toast.error(err?.response?.data?.detail || 'Failed to pause campaign'),
    });

    const resumeMutation = useMutation({
        mutationFn: () => campaignsApi.resumeCampaign(id!),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] });
            toast.success('Campaign resumed');
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: AxiosError<any>) => toast.error(err?.response?.data?.detail || 'Failed to resume campaign'),
    });

    const duplicateMutation = useMutation({
        mutationFn: () => campaignsApi.duplicateCampaign(id!),
        onSuccess: (newCampaign) => {
            toast.success('Campaign duplicated');
            navigate(ROUTES.CAMPAIGN_DETAIL(newCampaign.id));
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: AxiosError<any>) => toast.error(err?.response?.data?.detail || 'Failed to duplicate campaign'),
    });

    const archiveMutation = useMutation({
        mutationFn: () => campaignsApi.archiveCampaign(id!),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', id] });
            toast.success('Campaign archived');
            navigate(ROUTES.CAMPAIGNS);
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: AxiosError<any>) => toast.error(err?.response?.data?.detail || 'Failed to archive campaign'),
    });

    const deleteMutation = useMutation({
        mutationFn: () => campaignsApi.deleteCampaign(id!),
        onSuccess: () => {
            toast.success('Campaign deleted');
            navigate(ROUTES.CAMPAIGNS);
        },
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        onError: (err: AxiosError<any>) => toast.error(err?.response?.data?.detail || 'Failed to delete campaign'),
    });

    if (isLoading) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center h-[50vh]">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                </div>
            </DashboardLayout>
        );
    }

    if (error || !campaign) {
        return (
            <DashboardLayout>
                <div className="text-center py-10">
                    <h2 className="text-2xl font-bold text-gray-900">Campaign Not Found</h2>
                    <p className="text-gray-600 mt-2">The campaign you are looking for does not exist.</p>
                    <Link to={ROUTES.CAMPAIGNS}>
                        <Button className="mt-4" variant="outline">Back to Campaigns</Button>
                    </Link>
                </div>
            </DashboardLayout>
        );
    }

    const isActionPending = sendMutation.isPending || pauseMutation.isPending || resumeMutation.isPending || duplicateMutation.isPending || archiveMutation.isPending || deleteMutation.isPending;

    return (
        <DashboardLayout>
            <div className="max-w-5xl mx-auto space-y-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <Link to={ROUTES.CAMPAIGNS} className="hover:text-gray-900 flex items-center gap-1">
                                <ArrowLeft className="h-3 w-3" /> Campaigns
                            </Link>
                            <span>/</span>
                            <span>{campaign.name}</span>
                        </div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            {campaign.name}
                            <Badge variant={
                                campaign.status === 'sent' ? 'default' :
                                    campaign.status === 'scheduled' ? 'secondary' : 'outline'
                            }>
                                {campaign.status}
                            </Badge>
                        </h1>
                    </div>
                    <div className="flex gap-2">
                        {/* Primary Actions based on status */}
                        {campaign.status === 'draft' && (
                            <Button onClick={() => sendMutation.mutate()} disabled={isActionPending}>
                                <Send className="mr-2 h-4 w-4" /> Send Now
                            </Button>
                        )}
                        {campaign.status === 'scheduled' && (
                            <Button variant="outline" onClick={() => pauseMutation.mutate()} disabled={isActionPending}>
                                <Pause className="mr-2 h-4 w-4" /> Pause
                            </Button>
                        )}
                        {campaign.status === 'paused' && (
                            <Button variant="outline" onClick={() => resumeMutation.mutate()} disabled={isActionPending}>
                                <Play className="mr-2 h-4 w-4" /> Resume
                            </Button>
                        )}

                        <Button variant="outline" onClick={() => setEditDialogOpen(true)} disabled={isActionPending}>
                            <Edit className="mr-2 h-4 w-4" /> Edit
                        </Button>

                        <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon" disabled={isActionPending}>
                                    <MoreVertical className="h-4 w-4" />
                                </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => duplicateMutation.mutate()}>
                                    <Copy className="mr-2 h-4 w-4" /> Duplicate
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => archiveMutation.mutate()}>
                                    <Archive className="mr-2 h-4 w-4" /> Archive
                                </DropdownMenuItem>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                    className="text-destructive focus:text-destructive"
                                    onClick={() => {
                                        if (confirm('Are you sure you want to delete this campaign?')) {
                                            deleteMutation.mutate();
                                        }
                                    }}
                                >
                                    <Trash2 className="mr-2 h-4 w-4" /> Delete
                                </DropdownMenuItem>
                            </DropdownMenuContent>
                        </DropdownMenu>
                    </div>
                </div>

                {/* Tabs */}
                <Tabs defaultValue="overview" className="w-full">
                    <TabsList>
                        <TabsTrigger value="overview">Overview</TabsTrigger>
                        <TabsTrigger value="generation">AI Generation</TabsTrigger>
                        <TabsTrigger value="content">Content Review</TabsTrigger>
                        <TabsTrigger value="analytics">Analytics</TabsTrigger>
                    </TabsList>

                    {/* Overview Tab */}
                    <TabsContent value="overview" className="space-y-6 mt-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Primary Goal</CardTitle>
                                    <BarChart className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold capitalize">{campaign.primary_goal?.replace('_', ' ') || 'Not Set'}</div>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {campaign.success_criteria || 'No success criteria set'}
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Audience</CardTitle>
                                    <FileText className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-lg font-medium truncate" title={campaign.target_audience_description}>
                                        {campaign.target_audience_description || 'Not defined'}
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {campaign.estimated_recipients ? `~${campaign.estimated_recipients} recipients` : 'Size unknown'}
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-sm font-medium">Schedule</CardTitle>
                                    <Calendar className="h-4 w-4 text-muted-foreground" />
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold">
                                        {campaign.scheduled_at
                                            ? format(new Date(campaign.scheduled_at), 'MMM d, yyyy')
                                            : 'Not scheduled'}
                                    </div>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {campaign.scheduled_at
                                            ? format(new Date(campaign.scheduled_at), 'h:mm a')
                                            : 'Set a date to send'}
                                    </p>
                                </CardContent>
                            </Card>
                        </div>

                        <Card>
                            <CardHeader>
                                <CardTitle>Campaign Description</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-700">{campaign.description || 'No description provided.'}</p>
                            </CardContent>
                        </Card>

                        {/* Objectives Manager */}
                        <CampaignObjectivesManager
                            campaignId={id!}
                            objectives={campaign.objectives || []}
                            isEditable={campaign.status === 'draft'}
                        />
                    </TabsContent>

                    {/* AI Generation Tab */}
                    <TabsContent value="generation" className="mt-6">
                        <CampaignAIGeneration campaignId={id!} />
                    </TabsContent>

                    <TabsContent value="content" className="mt-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Content Review</CardTitle>
                                <CardDescription>Review and approve selected email content.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-gray-500 italic">Select a generated variant to enable content review.</p>
                            </CardContent>
                        </Card>
                    </TabsContent>

                    <TabsContent value="analytics" className="mt-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Performance Analytics</CardTitle>
                                <CardDescription>Campaign performance metrics will appear here after sending.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-col items-center justify-center py-12 text-gray-500">
                                    <BarChart className="h-12 w-12 mb-4 opacity-50" />
                                    <p>No analytics data available yet.</p>
                                </div>
                            </CardContent>
                        </Card>
                    </TabsContent>
                </Tabs>
            </div>

            <CampaignEditDialog
                campaign={campaign}
                open={editDialogOpen}
                onOpenChange={setEditDialogOpen}
            />
        </DashboardLayout>
    );
};
