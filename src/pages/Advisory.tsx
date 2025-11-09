import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, CheckCircle, Droplets, Sprout, Eye } from "lucide-react";

const Advisory = () => {
  const recommendations = [
    {
      icon: Sprout,
      title: "Apply Organic Pesticide",
      description: "Use neem-based spray on affected cotton plants",
      priority: "high",
    },
    {
      icon: Droplets,
      title: "Increase Irrigation",
      description: "Water plants early morning for next 3 days",
      priority: "medium",
    },
    {
      icon: Eye,
      title: "Monitor Crop Growth",
      description: "Check leaf health daily for next week",
      priority: "low",
    },
  ];

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-heading font-bold text-primary mb-2">Advisory Details</h1>
          <p className="text-muted-foreground">Personalized recommendations based on your farm data</p>
        </div>

        {/* Main Advisory Card */}
        <Card className="p-6 mb-6 shadow-hover bg-gradient-card">
          <div className="flex items-start justify-between mb-4">
            <div>
              <Badge variant="destructive" className="mb-2">High Priority</Badge>
              <h2 className="text-2xl font-heading font-bold mb-2">Pest Warning - Cotton Crop</h2>
              <p className="text-muted-foreground">
                Detected on March 15, 2024 • Confidence: 87%
              </p>
            </div>
          </div>

          <div className="prose prose-sm max-w-none mb-6">
            <h3 className="font-semibold text-lg mb-2">Analysis</h3>
            <p className="text-muted-foreground mb-4">
              Based on NDVI analysis and recent humidity patterns, there's a high probability of aphid
              infestation in your cotton field. Early intervention is crucial to prevent crop damage.
            </p>

            <h3 className="font-semibold text-lg mb-2">Recommended Actions</h3>
          </div>

          <div className="space-y-4 mb-6">
            {recommendations.map((rec, idx) => (
              <div
                key={idx}
                className="flex items-start gap-4 p-4 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <rec.icon className="h-5 w-5 text-primary" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-semibold">{rec.title}</h4>
                    <Badge
                      variant={
                        rec.priority === "high"
                          ? "destructive"
                          : rec.priority === "medium"
                          ? "default"
                          : "secondary"
                      }
                      className="text-xs"
                    >
                      {rec.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{rec.description}</p>
                </div>
                <Button size="sm" variant="ghost">
                  <CheckCircle className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button className="flex-1 bg-primary hover:bg-primary/90">
              <CheckCircle className="h-4 w-4 mr-2" />
              Mark as Done
            </Button>
            <Button variant="outline" className="flex-1">
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
            <Button variant="outline">Translate to मराठी</Button>
          </div>
        </Card>

        {/* Explainability Note */}
        <Card className="p-4 bg-info/10 border-info/20">
          <p className="text-sm text-foreground">
            <strong>How we determined this:</strong> This advisory is based on a combination of satellite
            NDVI data showing decreased vegetation health, high humidity levels (65%+) in your region, and
            historical pest patterns in similar conditions.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default Advisory;
