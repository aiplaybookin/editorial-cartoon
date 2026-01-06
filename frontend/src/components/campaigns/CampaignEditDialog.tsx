import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { campaignsApi } from '@/api/campaigns.api';
import { toast } from 'react-hot-toast';
import { AxiosError } from 'axios';
import type { Campaign, CampaignUpdate } from '@/types/campaign.types';

interface CampaignEditDialogProps {
    campaign: Campaign;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export const CampaignEditDialog = ({
    campaign,
    open,
    onOpenChange
}: CampaignEditDialogProps) => {
    const queryClient = useQueryClient();
    const [formData, setFormData] = useState<CampaignUpdate>({
        name: '',
        description: '',
        target_audience: '',
    });

    useEffect(() => {
        if (open && campaign) {
            setFormData({
                name: campaign.name,
                description: campaign.description || '',
                target_audience: campaign.target_audience || '',
            });
        }
    }, [open, campaign]);

    const updateMutation = useMutation({
        mutationFn: (data: CampaignUpdate) => campaignsApi.updateCampaign(campaign.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', campaign.id] });
            toast.success('Campaign updated successfully');
            onOpenChange(false);
        },
        onError: (error: AxiosError<any>) => {
            toast.error(error?.response?.data?.detail || 'Failed to update campaign');
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateMutation.mutate(formData);
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Edit Campaign</DialogTitle>
                    <DialogDescription>
                        Update the basic details of your campaign.
                    </DialogDescription>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="name">Campaign Name</Label>
                        <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            required
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="description">Description</Label>
                        <Textarea
                            id="description"
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="target_audience">Target Audience</Label>
                        <Input
                            id="target_audience"
                            value={formData.target_audience}
                            onChange={(e) => setFormData({ ...formData, target_audience: e.target.value })}
                        />
                    </div>

                    <DialogFooter>
                        <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" disabled={updateMutation.isPending}>
                            {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    );
};
