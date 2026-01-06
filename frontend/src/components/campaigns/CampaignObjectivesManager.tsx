import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { campaignsApi } from '@/api/campaigns.api';
import { toast } from 'react-hot-toast';
import { AxiosError } from 'axios';
import { Plus, Pencil, Trash2, Target } from 'lucide-react';
import type { CampaignObjective, CampaignObjectiveCreate } from '@/types/campaign.types';

interface CampaignObjectivesManagerProps {
    campaignId: string;
    objectives: CampaignObjective[];
    isEditable?: boolean;
}

export const CampaignObjectivesManager = ({
    campaignId,
    objectives,
    isEditable = true
}: CampaignObjectivesManagerProps) => {
    const queryClient = useQueryClient();
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [editingObjective, setEditingObjective] = useState<CampaignObjective | null>(null);

    // Form state
    const [formData, setFormData] = useState<CampaignObjectiveCreate>({
        objective_type: 'secondary',
        description: '',
        kpi_name: '',
        target_value: '',
        priority: 1,
    });

    // Reset form when dialog opens/closes
    const handleOpenChange = (open: boolean) => {
        setIsDialogOpen(open);
        if (!open) {
            setEditingObjective(null);
            setFormData({
                objective_type: 'secondary',
                description: '',
                kpi_name: '',
                target_value: '',
                priority: 1,
            });
        }
    };

    const openEditDialog = (objective: CampaignObjective) => {
        setEditingObjective(objective);
        setFormData({
            objective_type: objective.objective_type,
            description: objective.description,
            kpi_name: objective.kpi_name,
            target_value: objective.target_value,
            priority: objective.priority,
        });
        setIsDialogOpen(true);
    };

    // Mutations
    const createMutation = useMutation({
        mutationFn: (data: CampaignObjectiveCreate) => campaignsApi.createObjective(campaignId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', campaignId] });
            toast.success('Objective created successfully');
            handleOpenChange(false);
        },
        onError: (error: AxiosError<any>) => {
            toast.error(error?.response?.data?.detail || 'Failed to create objective');
        },
    });

    const updateMutation = useMutation({
        mutationFn: (data: CampaignObjectiveCreate) => campaignsApi.updateObjective(campaignId, editingObjective!.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', campaignId] });
            toast.success('Objective updated successfully');
            handleOpenChange(false);
        },
        onError: (error: AxiosError<any>) => {
            toast.error(error?.response?.data?.detail || 'Failed to update objective');
        },
    });

    const deleteMutation = useMutation({
        mutationFn: (objectiveId: string) => campaignsApi.deleteObjective(campaignId, objectiveId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['campaign', campaignId] });
            toast.success('Objective deleted successfully');
        },
        onError: (error: AxiosError<any>) => {
            toast.error(error?.response?.data?.detail || 'Failed to delete objective');
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (editingObjective) {
            updateMutation.mutate(formData);
        } else {
            createMutation.mutate(formData);
        }
    };

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between">
                <div>
                    <CardTitle className="flex items-center gap-2">
                        <Target className="h-5 w-5" />
                        Objectives
                    </CardTitle>
                    <CardDescription>Metrics and goals for this campaign</CardDescription>
                </div>
                {isEditable && (
                    <Dialog open={isDialogOpen} onOpenChange={handleOpenChange}>
                        <DialogTrigger asChild>
                            <Button size="sm">
                                <Plus className="mr-2 h-4 w-4" />
                                Add Objective
                            </Button>
                        </DialogTrigger>
                        <DialogContent>
                            <DialogHeader>
                                <DialogTitle>{editingObjective ? 'Edit Objective' : 'New Objective'}</DialogTitle>
                                <DialogDescription>
                                    Define what you want to achieve with this campaign.
                                </DialogDescription>
                            </DialogHeader>
                            <form onSubmit={handleSubmit} className="space-y-4 py-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>Type</Label>
                                        <Select
                                            value={formData.objective_type}
                                            onValueChange={(value: 'primary' | 'secondary') => setFormData({ ...formData, objective_type: value })}
                                        >
                                            <SelectTrigger>
                                                <SelectValue />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="primary">Primary</SelectItem>
                                                <SelectItem value="secondary">Secondary</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Priority</Label>
                                        <Input
                                            type="number"
                                            min={1}
                                            max={5}
                                            value={formData.priority}
                                            onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <Label>Description</Label>
                                    <Input
                                        placeholder="e.g. Generate qualified leads"
                                        value={formData.description}
                                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                        required
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-2">
                                        <Label>KPI Name</Label>
                                        <Input
                                            placeholder="e.g. Conversion Rate"
                                            value={formData.kpi_name}
                                            onChange={(e) => setFormData({ ...formData, kpi_name: e.target.value })}
                                            required
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <Label>Target Value</Label>
                                        <Input
                                            placeholder="e.g. 5%"
                                            value={formData.target_value}
                                            onChange={(e) => setFormData({ ...formData, target_value: e.target.value })}
                                            required
                                        />
                                    </div>
                                </div>

                                <DialogFooter>
                                    <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
                                        Cancel
                                    </Button>
                                    <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                                        {createMutation.isPending || updateMutation.isPending ? 'Saving...' : 'Save'}
                                    </Button>
                                </DialogFooter>
                            </form>
                        </DialogContent>
                    </Dialog>
                )}
            </CardHeader>
            <CardContent className="space-y-4">
                {objectives.length === 0 ? (
                    <div className="text-center py-6 text-gray-500 text-sm">
                        No objectives defined yet.
                    </div>
                ) : (
                    objectives.map((obj) => (
                        <div key={obj.id} className="flex items-start justify-between border-b pb-4 last:border-0 last:pb-0">
                            <div>
                                <p className="font-medium flex items-center gap-2">
                                    {obj.description}
                                    {obj.objective_type === 'primary' && (
                                        <span className="text-[10px] bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded capitalize">
                                            Primary
                                        </span>
                                    )}
                                </p>
                                <p className="text-sm text-gray-500">
                                    Priority: {obj.priority} • {obj.objective_type !== 'primary' && 'Secondary'}
                                </p>
                            </div>
                            <div className="flex items-center gap-4">
                                <div className="text-right mr-2">
                                    <p className="font-bold text-lg">{obj.target_value}</p>
                                    <p className="text-xs text-gray-500 uppercase">{obj.kpi_name}</p>
                                </div>
                                {isEditable && (
                                    <div className="flex gap-1">
                                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => openEditDialog(obj)}>
                                            <Pencil className="h-4 w-4" />
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="icon"
                                            className="h-8 w-8 text-destructive hover:text-destructive"
                                            onClick={() => {
                                                if (confirm('Are you sure you want to delete this objective?')) {
                                                    deleteMutation.mutate(obj.id);
                                                }
                                            }}
                                        >
                                            <Trash2 className="h-4 w-4" />
                                        </Button>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
};
