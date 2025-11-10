import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Camera } from "lucide-react";
import { toast } from "sonner";
import { getCurrentUser, getUser, isAuthenticated, User } from "../services/api";


const Profile = () => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    name: "",
    phone: "",
    email: "",
    userType: "",
    region: "",
    crop: "",
    farmSize: "",
    address: "",
  });
  const navigate = useNavigate();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated()) {
      navigate("/login");
      return;
    }

    // Load user data
    const loadUserData = async () => {
      try {
        setLoading(true);
        // Try to get from backend, fallback to localStorage
        const userData = await getCurrentUser();
        setUser(userData);
        setFormData({
          name: userData.name || "",
          phone: userData.phone || "",
          email: userData.email || "",
          userType: userData.userType || "",
          region: "",
          crop: "",
          farmSize: "",
          address: "",
        });
      } catch (error: any) {
        // Fallback to stored user data
        const storedUser = getUser();
        if (storedUser) {
          setUser(storedUser);
          setFormData({
            name: storedUser.name || "",
            phone: storedUser.phone || "",
            email: storedUser.email || "",
            userType: storedUser.userType || "",
            region: "",
            crop: "",
            farmSize: "",
            address: "",
          });
        } else {
          toast.error("Failed to load user data");
          navigate("/login");
        }
      } finally {
        setLoading(false);
      }
    };

    loadUserData();
  }, [navigate]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement profile update API call
    toast.success("Profile updated successfully!");
  };

  if (loading) {
    return (
      <div className="min-h-screen py-8 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg text-muted-foreground">Loading profile...</div>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  // Get first letter of name for avatar
  const initials = user.name ? user.name.charAt(0).toUpperCase() : "U";

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-heading font-bold text-primary mb-8">Profile Settings</h1>

        <Card className="p-6 shadow-hover bg-gradient-card">
          {/* Profile Picture */}
          <div className="flex flex-col items-center mb-8">
            <div className="relative">
              <Avatar className="w-24 h-24">
                <AvatarFallback className="bg-primary text-primary-foreground text-3xl">
                  {initials}
                </AvatarFallback>
              </Avatar>
              <button className="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-secondary text-white flex items-center justify-center hover:bg-secondary/90 transition-colors">
                <Camera className="h-4 w-4" />
              </button>
            </div>
            <h2 className="mt-4 text-xl font-semibold">{user.name}</h2>
            <p className="text-muted-foreground capitalize">{user.userType || "User"}</p>
          </div>

          {/* Profile Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input 
                  id="name" 
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Phone Number</Label>
                <Input 
                  id="phone" 
                  type="tel" 
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input 
                  id="email" 
                  type="email" 
                  value={formData.email}
                  disabled
                  className="bg-muted"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="region">Farm Region</Label>
                <Input 
                  id="region" 
                  value={formData.region}
                  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                  placeholder="Enter your farm region"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="crop">Primary Crop</Label>
                <Input 
                  id="crop" 
                  value={formData.crop}
                  onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
                  placeholder="Enter primary crop"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="farmSize">Farm Size (acres)</Label>
                <Input 
                  id="farmSize" 
                  type="number" 
                  value={formData.farmSize}
                  onChange={(e) => setFormData({ ...formData, farmSize: e.target.value })}
                  placeholder="Enter farm size"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Farm Address</Label>
              <Input 
                id="address" 
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="Enter farm address"
              />
            </div>

            <div className="flex gap-4">
              <Button type="submit" className="bg-primary hover:bg-primary/90">
                Save Changes
              </Button>
              <Button type="button" variant="outline" onClick={() => navigate(-1)}>
                Cancel
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default Profile;
