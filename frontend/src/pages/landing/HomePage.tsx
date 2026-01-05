import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export const HomePage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
            AI-Powered Email Marketing That Converts
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Generate high-converting email campaigns in minutes with Claude AI.
            Create, optimize, and send personalized emails at scale.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/signup">
              <Button size="lg">Start Free Trial</Button>
            </Link>
            <Link to="/login">
              <Button size="lg" variant="outline">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div className="mt-20 grid md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="text-4xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI Content Generation</h3>
            <p className="text-gray-600">
              Generate multiple email variants with Claude AI in seconds
            </p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">Campaign Management</h3>
            <p className="text-gray-600">
              Manage your campaigns from draft to delivery with ease
            </p>
          </div>
          <div className="text-center">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Goal Tracking</h3>
            <p className="text-gray-600">
              Set objectives and track KPIs for every campaign
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
