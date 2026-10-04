import { PageHeader } from '@/components/ui/typography';
import { EmptyState } from '@/components/ui/feedback';

export default function CourtFeaturePage({ params }: { params: { slug: string[] } }) {
  const featureName = params.slug.join(' ').replace(/-/g, ' ');
  const capitalized = featureName.charAt(0).toUpperCase() + featureName.slice(1);

  return (
    <div className="space-y-6">
      <PageHeader 
        title={capitalized} 
        description={`Manage ${capitalized} and court proceedings.`}
      />
      <EmptyState 
        title="No records found." 
        description={`There are currently no ${capitalized} records in your jurisdiction. The backend schema is ready, and this view will populate when new records are added.`}
      />
    </div>
  );
}
