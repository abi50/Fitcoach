export interface Exercise {
  id: string;
  name: string;
  category: string | null;
  muscle_groups: string[] | null;
  equipment: string[] | null;
}

export interface WorkoutPlan {
  id: string;
  name: string;
  goal: string;
  days_per_week: number;
  duration_weeks: number | null;
  is_active: boolean;
  created_at: string;
}

export interface WorkoutSession {
  id: string;
  plan_id: string | null;
  started_at: string;
  completed_at: string | null;
  notes: string | null;
  total_volume_kg: number | null;
  duration_minutes: number | null;
}

export interface SessionSet {
  id: string;
  exercise_id: string;
  set_number: number;
  weight_kg: number | null;
  reps: number | null;
  rpe: number | null;
  is_pr: boolean;
  notes: string | null;
}

export interface PersonalRecord {
  id: string;
  exercise_id: string;
  exercise_name: string;
  weight_kg: number;
  reps: number;
  achieved_at: string;
  celebrated: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
