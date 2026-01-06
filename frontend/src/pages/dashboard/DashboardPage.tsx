import { Link } from 'react-router-dom';
import { DashboardLayout } from '@/layouts/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useCampaignStats, useCampaigns } from '@/hooks/useCampaigns';
import { ROUTES } from '@/utils/constants';
import {
  Mail,
  Send,
  Calendar,
  CheckCircle,
  Plus,
  Sparkles,
} from 'lucide-react';

export const DashboardPage = () => {
  const { data: stats, isLoading: statsLoading } = useCampaignStats();
  const { data: recentCampaigns, isLoading: campaignsLoading } = useCampaigns({
    page: 1,
    per_page: 5,
  });

  const statsCards = [
    {
      title: 'Total Campaigns',
      value: stats?.total_campaigns || 0,
      icon: Mail,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Draft Campaigns',
      value: stats?.draft_campaigns || 0,
      icon: Calendar,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
    },
    {
      title: 'Scheduled',
      value: stats?.scheduled_campaigns || 0,
      icon: Send,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
    {
      title: 'Sent',
      value: stats?.sent_campaigns || 0,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">
              Welcome back! Here's what's happening with your campaigns.
            </p>
          </div>
          <div className="flex gap-3">
            <Link to={ROUTES.CAMPAIGN_NEW}>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                New Campaign
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statsCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card key={stat.title}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">
                    {stat.title}
                  </CardTitle>
                  <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  {statsLoading ? (
                    <div className="h-8 bg-gray-200 rounded animate-pulse" />
                  ) : (
                    <div className="text-2xl font-bold">{stat.value}</div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Recent Campaigns */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Campaigns</CardTitle>
            </CardHeader>
            <CardContent>
              {campaignsLoading ? (
                <div className="space-y-3">
                  {[...Array(3)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded animate-pulse" />
                  ))}
                </div>
              ) : recentCampaigns && recentCampaigns.campaigns.length > 0 ? (
                <div className="space-y-3">
                  {recentCampaigns.campaigns.map((campaign) => (
                    <Link
                      key={campaign.id}
                      to={ROUTES.CAMPAIGN_DETAIL(campaign.id)}
                      className="block p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="font-medium text-gray-900">
                            {campaign.name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {campaign.description || 'No description'}
                          </p>
                        </div>
                        <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 text-gray-800">
                          {campaign.status}
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Mail className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500 mb-4">No campaigns yet</p>
                  <Link to={ROUTES.CAMPAIGN_NEW}>
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Create Campaign
                    </Button>
                  </Link>
                </div>
              )}

              {recentCampaigns && recentCampaigns.campaigns.length > 0 && (
                <Link to={ROUTES.CAMPAIGNS}>
                  <Button variant="outline" className="w-full mt-4">
                    View All Campaigns
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>

          {/* Quick Start Guide */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Start</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <div className="h-6 w-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-medium">
                    1
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    Create a Campaign
                  </h4>
                  <p className="text-sm text-gray-600">
                    Set up your campaign with objectives and target audience
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <div className="h-6 w-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-medium">
                    2
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    Generate Email with AI
                  </h4>
                  <p className="text-sm text-gray-600">
                    Use Claude AI to create personalized email content
                  </p>
                </div>
              </div>

              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  <div className="h-6 w-6 rounded-full bg-primary text-white flex items-center justify-center text-xs font-medium">
                    3
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-1">
                    Review & Send
                  </h4>
                  <p className="text-sm text-gray-600">
                    Schedule or send your campaign immediately
                  </p>
                </div>
              </div>

              <Button variant="outline" className="w-full">
                <Sparkles className="h-4 w-4 mr-2" />
                Learn More
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
};
