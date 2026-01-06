import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCreateCampaign } from '@/hooks/useCampaigns';
import { ArrowLeft, Plus, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';
import type { CampaignObjectiveCreate } from '@/types/campaign.types';

const campaignSchema = z.object({
  name: z.string().min(3, 'Campaign name must be at least 3 characters').max(200),
  description: z.string().optional(),
  target_audience: z.string().optional(),
});

type CampaignFormData = z.infer<typeof campaignSchema>;

export const CampaignCreatePage = () => {
  const { mutate: createCampaign, isPending } = useCreateCampaign();
  const [objectives, setObjectives] = useState<CampaignObjectiveCreate[]>([
    {
      objective_type: 'primary',
      description: '',
      kpi_name: '',
      target_value: '',
      priority: 1,
    },
  ]);

  const form = useForm<CampaignFormData>({
    resolver: zodResolver(campaignSchema),
    defaultValues: {
      name: '',
      description: '',
      target_audience: '',
    },
  });

  const addObjective = () => {
    setObjectives([
      ...objectives,
      {
        objective_type: 'secondary',
        description: '',
        kpi_name: '',
        target_value: '',
        priority: objectives.length + 1,
      },
    ]);
  };

  const removeObjective = (index: number) => {
    setObjectives(objectives.filter((_, i) => i !== index));
  };

  const updateObjective = (index: number, field: keyof CampaignObjectiveCreate, value: string | number) => {
    const updated = [...objectives];
    updated[index] = { ...updated[index], [field]: value };
    setObjectives(updated);
  };

  const onSubmit = (data: CampaignFormData) => {
    // Validate objectives
    const validObjectives = objectives.filter(
      (obj) => obj.description && obj.kpi_name && obj.target_value
    );

    if (validObjectives.length === 0) {
      alert('Please add at least one objective');
      return;
    }

    createCampaign({
      ...data,
      objectives: validObjectives,
    });
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to={ROUTES.CAMPAIGNS}>
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Campaign</h1>
            <p className="text-gray-600 mt-1">
              Set up a new email marketing campaign
            </p>
          </div>
        </div>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <FormField
                  control={form.control}
                  name="name"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Campaign Name *</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Q1 Product Launch Email"
                          disabled={isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="description"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Description</FormLabel>
                      <FormControl>
                        <textarea
                          placeholder="Brief description of this campaign..."
                          className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                          disabled={isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="target_audience"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Target Audience</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="e.g., Tech professionals, age 25-45"
                          disabled={isPending}
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </CardContent>
            </Card>

            {/* Objectives */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle>Campaign Objectives</CardTitle>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={addObjective}
                  disabled={isPending}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Objective
                </Button>
              </CardHeader>
              <CardContent className="space-y-4">
                {objectives.map((objective, index) => (
                  <div
                    key={index}
                    className="p-4 border rounded-lg space-y-3 relative"
                  >
                    {objectives.length > 1 && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute top-2 right-2"
                        onClick={() => removeObjective(index)}
                        disabled={isPending}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">Type *</label>
                        <select
                          value={objective.objective_type}
                          onChange={(e) =>
                            updateObjective(index, 'objective_type', e.target.value)
                          }
                          className="mt-1 w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                          disabled={isPending}
                        >
                          <option value="primary">Primary</option>
                          <option value="secondary">Secondary</option>
                        </select>
                      </div>

                      <div>
                        <label className="text-sm font-medium">Priority</label>
                        <Input
                          type="number"
                          min="1"
                          max="5"
                          value={objective.priority || 1}
                          onChange={(e) =>
                            updateObjective(index, 'priority', parseInt(e.target.value))
                          }
                          disabled={isPending}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Description *</label>
                      <Input
                        value={objective.description}
                        onChange={(e) =>
                          updateObjective(index, 'description', e.target.value)
                        }
                        placeholder="e.g., Increase product awareness"
                        disabled={isPending}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">KPI Name *</label>
                        <Input
                          value={objective.kpi_name}
                          onChange={(e) =>
                            updateObjective(index, 'kpi_name', e.target.value)
                          }
                          placeholder="e.g., Click-through rate"
                          disabled={isPending}
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium">Target Value *</label>
                        <Input
                          value={objective.target_value}
                          onChange={(e) =>
                            updateObjective(index, 'target_value', e.target.value)
                          }
                          placeholder="e.g., 5%"
                          disabled={isPending}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex gap-3 justify-end">
              <Link to={ROUTES.CAMPAIGNS}>
                <Button type="button" variant="outline" disabled={isPending}>
                  Cancel
                </Button>
              </Link>
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Creating...' : 'Create Campaign'}
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </DashboardLayout>
  );
};
