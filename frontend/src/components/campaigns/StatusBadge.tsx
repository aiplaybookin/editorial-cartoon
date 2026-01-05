import { Badge } from '@/components/ui/badge';
import type { CampaignStatus } from '@/types/campaign.types';

interface StatusBadgeProps {
  status: CampaignStatus;
}

export const StatusBadge = ({ status }: StatusBadgeProps) => {
  const statusConfig: Record<
    CampaignStatus,
    { variant: 'default' | 'secondary' | 'destructive' | 'success' | 'warning' | 'info'; label: string }
  > = {
    draft: { variant: 'secondary', label: 'Draft' },
    generating: { variant: 'info', label: 'Generating' },
    scheduled: { variant: 'warning', label: 'Scheduled' },
    sending: { variant: 'info', label: 'Sending' },
    sent: { variant: 'success', label: 'Sent' },
    paused: { variant: 'warning', label: 'Paused' },
    archived: { variant: 'secondary', label: 'Archived' },
    cancelled: { variant: 'destructive', label: 'Cancelled' },
  };

  const config = statusConfig[status];

  return <Badge variant={config.variant}>{config.label}</Badge>;
};
