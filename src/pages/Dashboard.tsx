import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CloudRain, TrendingUp, Satellite, AlertTriangle, RefreshCw, Sprout, Loader2 } from "lucide-react";
import { getDashboardData } from "@/services/api";
import type { DashboardResponse, Alert } from "@/types/fusion";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getDashboardData();
      setDashboardData(data);
    } catch (err: any) {
      setError(err.message || "Unable to load dashboard data");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleRefresh = () => {
    fetchDashboardData();
  };

  const handleViewAdvisory = (crop?: string) => {
    if (crop) {
      navigate(`/advisory/${crop.toLowerCase()}`);
    } else {
      navigate("/advisory/cotton"); // Default to cotton if no crop specified
    }
  };

  // Format price with trend indicator
  const formatPrice = (price: number, changePercent: number) => {
    const trend = changePercent >= 0 ? "↑" : "↓";
    const color = changePercent >= 0 ? "text-success" : "text-destructive";
    return (
      <span className={`font-medium ${color}`}>
        {trend} ₹{price.toLocaleString("en-IN")}
      </span>
    );
  };

  // Get alert color based on level
  const getAlertColor = (level: string) => {
    switch (level) {
      case "high":
        return "destructive";
      case "medium":
        return "warning";
      case "low":
        return "info";
      default:
        return "default";
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading Dashboard...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center max-w-md">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-destructive" />
          <h2 className="text-2xl font-bold mb-2">Unable to Load Dashboard</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={handleRefresh} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // Default values if data is missing
  const weather = dashboardData?.weather || {
    temperature: 28,
    humidity: 65,
    rainfall: 5,
    wind_speed: 12,
  };

  const market = dashboardData?.market || {};
  const alerts = dashboardData?.alerts || [];
  const cropHealth = dashboardData?.crop_health || {};

  // Calculate average health score
  const healthScores = Object.values(cropHealth).map((crop: any) => crop.health_score || 0);
  const avgHealthScore = healthScores.length > 0
    ? Math.round(healthScores.reduce((a, b) => a + b, 0) / healthScores.length)
    : 78;

  // Get health status text
  const getHealthStatus = (score: number) => {
    if (score >= 80) return "Excellent";
    if (score >= 60) return "Good";
    if (score >= 40) return "Fair";
    return "Poor";
  };

  // Get average market price for display
  const marketPrices = Object.values(market);
  const avgMarketPrice = marketPrices.length > 0
    ? Math.round(marketPrices.reduce((sum: number, crop: any) => sum + (crop.price || 0), 0) / marketPrices.length)
    : 2450;

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-heading font-bold text-primary mb-2">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back! Here's your farm overview</p>
          </div>
          <Button variant="outline" className="gap-2" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
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
                <h3 className="text-2xl font-bold">{weather.temperature}°C</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                <CloudRain className="h-6 w-6 text-secondary" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Humidity</span>
                <span className="font-medium">{weather.humidity}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Wind Speed</span>
                <span className="font-medium">{weather.wind_speed} km/h</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rainfall</span>
                <span className="font-medium">{weather.rainfall}mm</span>
              </div>
            </div>
          </Card>

          {/* Market Prices Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Market Prices</p>
                <h3 className="text-2xl font-bold">₹{avgMarketPrice.toLocaleString("en-IN")}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-success/20 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-success" />
              </div>
            </div>
            <div className="space-y-2 text-sm">
              {market.wheat && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Wheat</span>
                  {formatPrice(market.wheat.price, market.wheat.change_percent)}
                </div>
              )}
              {market.rice && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Rice</span>
                  {formatPrice(market.rice.price, market.rice.change_percent)}
                </div>
              )}
              {market.cotton && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Cotton</span>
                  {formatPrice(market.cotton.price, market.cotton.change_percent)}
                </div>
              )}
              {Object.keys(market).length === 0 && (
                <p className="text-sm text-muted-foreground">No market data available</p>
              )}
            </div>
          </Card>

          {/* NDVI Health Card */}
          <Card className="p-6 hover:shadow-hover transition-all bg-gradient-card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Crop Health (NDVI)</p>
                <h3 className="text-2xl font-bold">{getHealthStatus(avgHealthScore)}</h3>
              </div>
              <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                <Satellite className="h-6 w-6 text-primary" />
              </div>
            </div>
            <div className="relative pt-1">
              <div className="overflow-hidden h-3 text-xs flex rounded-full bg-muted">
                <div
                  style={{ width: `${avgHealthScore}%` }}
                  className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-success"
                ></div>
              </div>
              <p className="text-sm text-muted-foreground mt-2">Health Score: {avgHealthScore}%</p>
            </div>
          </Card>
        </div>

        {/* Risk Alerts Section */}
        {alerts.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="h-5 w-5 text-warning" />
              <h2 className="text-xl font-heading font-bold">Risk Alerts</h2>
              <span className="text-sm text-muted-foreground">
                ({dashboardData?.summary?.high_priority_count || 0} high priority)
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {alerts.map((alert: Alert) => (
                <Card
                  key={alert.id}
                  className={`p-4 border-l-4 hover:shadow-hover transition-all ${
                    alert.level === "high"
                      ? "border-l-destructive"
                      : alert.level === "medium"
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
                          alert.level === "high"
                            ? "text-destructive"
                            : alert.level === "medium"
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
                    {alert.description && (
                      <p className="text-xs text-muted-foreground mt-2">{alert.description}</p>
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2"
                      onClick={() => handleViewAdvisory(alert.crop)}
                    >
                      View Advisory
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

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
