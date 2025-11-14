import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Heart, MessageCircle, Share2, Plus, TrendingUp, Loader2 } from "lucide-react";
import { useTranslation } from "react-i18next";
import { getCommunityPosts, togglePostLike, createPost, type Post, type CreatePostData } from "@/services/api";
import { toast } from "sonner";

const Community = () => {
  const { t } = useTranslation();
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [likingPostId, setLikingPostId] = useState<number | null>(null);
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const [postContent, setPostContent] = useState("");
  const [isCreatingPost, setIsCreatingPost] = useState(false);

  // Fetch posts on component mount
  useEffect(() => {
    const fetchPosts = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getCommunityPosts();
        setPosts(data);
      } catch (err: any) {
        setError(err.message || "Failed to load posts");
        toast.error(err.message || "Failed to load community posts");
      } finally {
        setIsLoading(false);
      }
    };
    fetchPosts();
  }, []);

  // Handle post creation
  const handleCreatePost = async () => {
    if (!postContent.trim()) {
      toast.error(t("community.post_content_required"));
      return;
    }

    setIsCreatingPost(true);
    try {
      const postData: CreatePostData = {
        content: postContent.trim(),
      };
      const newPost = await createPost(postData);
      
      // Add the new post to the beginning of the list
      setPosts([newPost, ...posts]);
      
      // Reset form and close modal
      setPostContent("");
      setIsPostModalOpen(false);
      toast.success(t("community.post_created_success"));
    } catch (err: any) {
      toast.error(err.message || t("community.post_create_error"));
    } finally {
      setIsCreatingPost(false);
    }
  };

  // Handle like toggle
  const handleLike = async (postId: number) => {
    if (likingPostId) return; // Prevent multiple simultaneous likes
    
    setLikingPostId(postId);
    try {
      const result = await togglePostLike(postId);
      // Update the post in the list
      setPosts(posts.map(post => 
        post.id === postId 
          ? { ...post, likes_count: result.likes_count, is_liked: result.is_liked }
          : post
      ));
    } catch (err: any) {
      toast.error(err.message || "Failed to like post");
    } finally {
      setLikingPostId(null);
    }
  };

  // Format timestamp
  const formatTimestamp = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return t("community.just_now");
    if (diffMins < 60) return t("community.minutes_ago", { count: diffMins });
    if (diffHours < 24) return t("community.hours_ago", { count: diffHours });
    if (diffDays < 7) return t("community.days_ago", { count: diffDays });
    
    return date.toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const topContributors = [
    { name: "Rajesh K.", posts: 24 },
    { name: "Priya S.", posts: 18 },
    { name: "Anil P.", posts: 15 },
  ];

  // Loading skeleton
  const LoadingSkeleton = () => (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <Card key={i} className="p-6">
          <div className="flex items-start gap-4">
            <Skeleton className="w-12 h-12 rounded-full" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-24" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Feed */}
          <div className="flex-1">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-heading font-bold text-primary mb-2">{t("community.title")}</h1>
                <p className="text-muted-foreground">{t("community.subtitle")}</p>
              </div>
              <Button 
                className="bg-primary hover:bg-primary/90 gap-2"
                onClick={() => setIsPostModalOpen(true)}
              >
                <Plus className="h-4 w-4" />
                {t("community.post_update")}
              </Button>
            </div>

            {isLoading ? (
              <LoadingSkeleton />
            ) : error ? (
              <Card className="p-6 text-center">
                <p className="text-destructive mb-4">{error}</p>
                <Button onClick={() => window.location.reload()} variant="outline">
                  {t("community.retry")}
                </Button>
              </Card>
            ) : posts.length === 0 ? (
              <Card className="p-6 text-center">
                <p className="text-muted-foreground mb-4">{t("community.no_posts")}</p>
              </Card>
            ) : (
              <div className="space-y-4">
                {posts.map((post) => (
                  <Card key={post.id} className="p-6 hover:shadow-hover transition-all bg-gradient-card">
                    <div className="flex items-start gap-4">
                      <Avatar className="w-12 h-12">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          {(post.author_name || post.author?.name || "U").charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold">{post.author_name || post.author?.name || "Unknown"}</h3>
                          <span className="text-sm text-muted-foreground">• {post.region || "Unknown"}</span>
                          <span className="text-xs text-muted-foreground">• {formatTimestamp(post.created_at)}</span>
                        </div>
                        <p className="text-foreground mb-4 whitespace-pre-wrap">{post.content}</p>

                        {/* Actions */}
                        <div className="flex items-center gap-6 text-sm text-muted-foreground">
                          <button 
                            onClick={() => handleLike(post.id)}
                            disabled={likingPostId === post.id}
                            className={`flex items-center gap-2 transition-colors ${
                              post.is_liked 
                                ? "text-destructive" 
                                : "hover:text-destructive"
                            } ${likingPostId === post.id ? "opacity-50 cursor-not-allowed" : ""}`}
                          >
                            {likingPostId === post.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Heart className={`h-4 w-4 ${post.is_liked ? "fill-current" : ""}`} />
                            )}
                            <span>{post.likes_count}</span>
                          </button>
                          <button className="flex items-center gap-2 hover:text-primary transition-colors">
                            <MessageCircle className="h-4 w-4" />
                            <span>{post.comments_count}</span>
                          </button>
                          <button className="flex items-center gap-2 hover:text-secondary transition-colors">
                            <Share2 className="h-4 w-4" />
                            <span>{t("community.share")}</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:w-80 space-y-6">
            {/* Top Contributors */}
            <Card className="p-6 bg-gradient-card">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="h-5 w-5 text-primary" />
                <h3 className="font-heading font-bold">{t("community.top_contributors")}</h3>
              </div>
              <div className="space-y-3">
                {topContributors.map((contributor, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-lg text-muted-foreground">#{idx + 1}</span>
                      <Avatar className="w-8 h-8">
                        <AvatarFallback className="bg-muted text-foreground">
                          {contributor.name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-medium">{contributor.name}</span>
                    </div>
                    <Badge variant="secondary">{t("community.posts_count", { count: contributor.posts })}</Badge>
                  </div>
                ))}
              </div>
            </Card>

            {/* Trending Topics */}
            <Card className="p-6 bg-gradient-card">
              <h3 className="font-heading font-bold mb-4">{t("community.trending_topics")}</h3>
              <div className="space-y-2">
                {["#OrganicFarming", "#PestControl", "#IrrigationTips", "#WeatherUpdate"].map((tag) => (
                  <button
                    key={tag}
                    className="block w-full text-left px-3 py-2 rounded-md bg-muted hover:bg-muted/70 transition-colors text-sm font-medium text-primary"
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>

      {/* Post Creation Modal */}
      <Dialog open={isPostModalOpen} onOpenChange={setIsPostModalOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>{t("community.create_post")}</DialogTitle>
            <DialogDescription>
              {t("community.create_post_description")}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Textarea
              placeholder={t("community.post_placeholder")}
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              className="min-h-[150px] resize-none"
              disabled={isCreatingPost}
            />
            <p className="text-xs text-muted-foreground">
              {t("community.post_hint")}
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsPostModalOpen(false);
                setPostContent("");
              }}
              disabled={isCreatingPost}
            >
              {t("community.cancel")}
            </Button>
            <Button
              onClick={handleCreatePost}
              disabled={isCreatingPost || !postContent.trim()}
              className="bg-primary hover:bg-primary/90"
            >
              {isCreatingPost ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {t("community.posting")}
                </>
              ) : (
                t("community.post")
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Community;
