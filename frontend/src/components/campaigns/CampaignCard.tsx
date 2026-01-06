import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StatusBadge } from './StatusBadge';
import { ROUTES } from '@/utils/constants';
import type { Campaign } from '@/types/campaign.types';
import { Calendar, Target } from 'lucide-react';
import { format } from 'date-fns';

interface CampaignCardProps {
  campaign: Campaign;
}

export const CampaignCard = ({ campaign }: CampaignCardProps) => {
  return (
    <Link to={ROUTES.CAMPAIGN_DETAIL(campaign.id)}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle className="text-lg">{campaign.name}</CardTitle>
            <StatusBadge status={campaign.status} />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {campaign.description && (
            <p className="text-sm text-gray-600 line-clamp-2">
              {campaign.description}
            </p>
          )}

          <div className="flex items-center gap-4 text-sm text-gray-500">
            {campaign.scheduled_at && (
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>
                  {format(new Date(campaign.scheduled_at), 'MMM d, yyyy')}
                </span>
              </div>
            )}

            {campaign.objectives && campaign.objectives.length > 0 && (
              <div className="flex items-center gap-1">
                <Target className="h-4 w-4" />
                <span>{campaign.objectives.length} objectives</span>
              </div>
            )}
          </div>

          <div className="text-xs text-gray-400">
            Created {format(new Date(campaign.created_at), 'MMM d, yyyy')}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};
