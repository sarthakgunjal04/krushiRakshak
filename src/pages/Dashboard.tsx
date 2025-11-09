import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CloudRain, TrendingUp, Satellite, AlertTriangle, RefreshCw, Sprout } from "lucide-react";

const Dashboard = () => {
  const riskAlerts = [
    { title: "Pest Warning - Cotton", level: "high", confidence: 87, color: "destructive" },
    { title: "Irrigation Required", level: "medium", confidence: 72, color: "warning" },
    { title: "Weather Alert - Rain", level: "low", confidence: 65, color: "info" },
  ];

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-heading font-bold text-primary mb-2">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's your farm overview</p>
          </div>
          <Button variant="outline" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Refresh Data
          </Button>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Weather Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Weather Summary</p>
                <h3 className="text-2xl font-bold">28°C</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <CloudRain className="h-6 w-6 text-secondary" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Humidity</span>
                <span className="font-medium">65%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Wind Speed</span>
                <span className="font-medium">12 km/h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rainfall</span>
                <span className="font-medium">5mm</span>
              </div>
            </div>
          </Card>

          {/* Market Prices Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Market Prices</p>
                <h3 className="text-2xl font-bold">₹2,450</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Wheat</span>
                <span className="font-medium text-success">↑ ₹2,100</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rice</span>
                <span className="font-medium text-success">↑ ₹3,200</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Cotton</span>
                <span className="font-medium text-destructive">↓ ₹5,800</span>
              </div>
            </div>
          </Card>

          {/* NDVI Health Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Crop Health (NDVI)</p>
                <h3 className="text-2xl font-bold">Good</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <Satellite className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div className="relative pt-1">
              <div className="overflow-hidden h-3 text-xs flex rounded-full bg-muted">
                <div
                  style={{ width: "78%" }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-success"
                ></div>
              </div>
              <p className="text-sm text-muted-foreground mt-2">Health Score: 78%</p>
            </div>
          </Card>
        </div>

        {/* Risk Alerts Section */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <AlertTriangle className="h-5 w-5 text-warning" />
            <h2 className="text-xl font-heading font-bold">Risk Alerts</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {riskAlerts.map((alert, idx) => (
              <Card
                key={idx}
                className={`p-4 border-l-4 hover:shadow-hover transition-all ${
                  alert.color === "destructive"
                    ? "border-l-destructive"
                    : alert.color === "warning"
                    ? "border-l-warning"
                    : "border-l-info"
                }`}
              >
                <h4 className="font-semibold mb-2">{alert.title}</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Risk Level</span>
                    <span
                      className={`font-medium ${
                        alert.color === "destructive"
                          ? "text-destructive"
                          : alert.color === "warning"
                          ? "text-warning"
                          : "text-info"
                      }`}
                    >
                      {alert.level.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Confidence</span>
                    <span className="font-medium">{alert.confidence}%</span>
                  </div>
                  <Button variant="outline" size="sm" className="w-full mt-2">
                    View Advisory
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Motivational Banner */}
        <Card className="p-6 bg-gradient-hero text-white text-center">
          <Sprout className="h-8 w-8 mx-auto mb-3 animate-float" />
          <p className="text-lg font-medium">"Healthy soil, happy harvest 🌾"</p>
          <p className="text-sm opacity-90 mt-2">Keep nurturing your land with smart decisions</p>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
