export type AuthResponse = {
  access_token: string;
  token_type: string;
};

export type Profile = {
  id: string;
  user_id: string;
  name: string;
  budget_min: number | null;
  budget_max: number | null;
  preferred_brands: string[];
  avoid_brands: string[];
  shipping_speed_preference: "fastest" | "balanced" | "cheapest";
  use_case_tags: string[];
  created_at: string;
};

export type AgentEvent = {
  run_id: string;
  event_type: "started" | "progress" | "finished" | "error";
  agent_name: string;
  message: string;
  payload: Record<string, unknown>;
  timestamp: string;
};

export type RankedProduct = {
  provider: string;
  product_id: string;
  title: string;
  brand: string | null;
  price: number;
  rating: number;
  review_count: number;
  eta_days: number;
  shipping_cost: number;
  pros: string[];
  cons: string[];
  why_recommended: string;
  tradeoffs: string;
  confidence: number;
  total_score: number;
};

export type RunResponse = {
  id: string;
  user_id: string;
  profile_id: string;
  user_query: string;
  status: string;
  final_output: {
    top_recommendations: RankedProduct[];
  } | null;
  created_at: string;
  updated_at: string;
};
