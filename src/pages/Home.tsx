import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CloudRain, TrendingUp, Users, FileText } from "lucide-react";
import { isAuthenticated } from "@/services/api";
import heroImage from "@/assets/hero-farmland.jpg";

const Home = () => {
  const authenticated = isAuthenticated();
  const features = [
    {
      icon: CloudRain,
      title: "Weather Insights",
      description: "Real-time weather forecasts and alerts tailored to your farm location",
    },
    {
      icon: FileText,
      title: "Smart Advisory",
      description: "AI-powered crop recommendations and pest management solutions",
    },
    {
      icon: Users,
      title: "Community",
      description: "Connect with fellow farmers, share experiences, and learn together",
    },
    {
      icon: TrendingUp,
      title: "Market Prices",
      description: "Live crop market prices and trends to help you make informed decisions",
    },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[600px] flex items-center justify-center overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url(${heroImage})`,
            filter: "brightness(0.7)",
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-b from-primary/20 to-transparent" />

        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto animate-slide-up">
          <h1 className="text-4xl md:text-6xl font-heading font-bold text-white mb-6 drop-shadow-lg">
            Empowering Farmers Through Smart Insights
          </h1>
          <p className="text-xl md:text-2xl text-white/90 mb-8 drop-shadow">
            Your intelligent farming companion for weather, advisory, and community support
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 shadow-hover">
              <Link to="/dashboard">Get Started</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="bg-white/10 backdrop-blur text-white border-white hover:bg-white/20">
              <Link to="/install">Install App</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="bg-white/10 backdrop-blur text-white border-white hover:bg-white/20">
              <Link to="/about">Learn More</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-gradient-to-b from-background to-muted/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-heading font-bold mb-4 text-primary">
              How AgriSense Helps You
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Everything you need to make informed farming decisions in one place
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, idx) => (
              <Card
                key={idx}
                className="p-6 text-center hover:shadow-hover transition-all duration-300 hover:-translate-y-1 bg-gradient-card border-border/50"
              >
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-hero text-white mb-4 animate-float">
                  <feature.icon className="h-8 w-8" />
                </div>
                <h3 className="font-heading font-bold text-xl mb-3">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-hero text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-heading font-bold mb-6">
            Ready to Transform Your Farming?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            {authenticated 
              ? "Continue to your dashboard to access all features"
              : "Join thousands of farmers already using AgriSense"
            }
          </p>
          <Button asChild size="lg" className="bg-white text-primary hover:bg-white/90 shadow-hover">
            {authenticated ? (
              <Link to="/dashboard">Go to Dashboard</Link>
            ) : (
              <Link to="/signup">Create Free Account</Link>
            )}
          </Button>
        </div>
      </section>
    </div>
  );
};

export default Home;
