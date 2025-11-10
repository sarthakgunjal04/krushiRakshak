import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MapPin, Upload, Wifi, WifiOff } from "lucide-react";
import { toast } from "sonner";
import { submitReport } from "../services/api";


const Report = () => {
  const [isOnline] = useState(true);
  const [formData, setFormData] = useState({
    crop: "",
    issueType: "",
    severity: "",
    notes: "",
    location: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isOnline) {
      toast.success("Issue reported successfully!");
    } else {
      toast.info("Saved locally. Will sync when online.");
    }
  };

  const detectLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
          setFormData({ ...formData, location: coords });
          toast.success("Location detected!");
        },
        () => {
          toast.error("Unable to detect location");
        }
      );
    }
  };

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-3xl font-heading font-bold text-primary">Report an Issue</h1>
            <div className="flex items-center gap-2 text-sm">
              {isOnline ? (
                <span className="flex items-center gap-1 text-success">
                  <Wifi className="h-4 w-4" />
                  Online
                </span>
              ) : (
                <span className="flex items-center gap-1 text-warning">
                  <WifiOff className="h-4 w-4" />
                  Offline
                </span>
              )}
            </div>
          </div>
          <p className="text-muted-foreground">
            Help us identify and solve issues in your farm
          </p>
        </div>

        <Card className="p-6 shadow-hover bg-gradient-card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="crop">Crop Type *</Label>
              <Select
                value={formData.crop}
                onValueChange={(value) => setFormData({ ...formData, crop: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select crop" />
                </SelectTrigger>
                <SelectContent className="bg-popover">
                  <SelectItem value="wheat">Wheat</SelectItem>
                  <SelectItem value="rice">Rice</SelectItem>
                  <SelectItem value="cotton">Cotton</SelectItem>
                  <SelectItem value="sugarcane">Sugarcane</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="issueType">Issue Type *</Label>
              <Select
                value={formData.issueType}
                onValueChange={(value) => setFormData({ ...formData, issueType: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select issue type" />
                </SelectTrigger>
                <SelectContent className="bg-popover">
                  <SelectItem value="pest">Pest Infestation</SelectItem>
                  <SelectItem value="disease">Crop Disease</SelectItem>
                  <SelectItem value="weather">Weather Damage</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="severity">Severity *</Label>
              <Select
                value={formData.severity}
                onValueChange={(value) => setFormData({ ...formData, severity: value })}
                required
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select severity" />
                </SelectTrigger>
                <SelectContent className="bg-popover">
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="location">GPS Coordinates</Label>
              <div className="flex gap-2">
                <Input
                  id="location"
                  type="text"
                  placeholder="Auto-detected coordinates"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  readOnly
                />
                <Button type="button" variant="outline" onClick={detectLocation}>
                  <MapPin className="h-4 w-4" />
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Additional Notes</Label>
              <Textarea
                id="notes"
                placeholder="Describe the issue in detail..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="photo">Upload Photo (Optional)</Label>
              <div className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary transition-colors cursor-pointer">
                <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-sm text-muted-foreground">
                  Click to upload or drag and drop
                </p>
                <input type="file" id="photo" accept="image/*" className="hidden" />
              </div>
            </div>

            <Button type="submit" className="w-full bg-primary hover:bg-primary/90">
              Submit Report
            </Button>
          </form>
        </Card>

        {/* Offline Queue (shown when offline) */}
        {!isOnline && (
          <Card className="mt-6 p-4 bg-warning/10 border-warning/20">
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <WifiOff className="h-4 w-4" />
              Offline Queue
            </h3>
            <p className="text-sm text-muted-foreground">
              Your reports will be automatically synced when you're back online.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Report;
