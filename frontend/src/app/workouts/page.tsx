"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import api from "@/lib/api";
import { useAuthStore } from "@/store/auth";
import { WorkoutPlan, WorkoutSession } from "@/types/workout";
import { Nav } from "@/components/layout/Nav";
import { PlanCard } from "@/components/workouts/PlanCard";
import { NewPlanDialog } from "@/components/workouts/NewPlanDialog";
import { Separator } from "@/components/ui/separator";
import { format } from "date-fns";

function formatDuration(minutes: number | null) {
  if (!minutes) return "—";
  if (minutes < 60) return `${minutes} min`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export default function WorkoutsPage() {
  const router = useRouter();
  const token = useAuthStore((s) => s.token);

  useEffect(() => {
    if (!token) router.push("/login");
  }, [token, router]);

  const plans = useQuery({
    queryKey: ["plans"],
    queryFn: () =>
      api.get<WorkoutPlan[]>("/workouts/plans").then((r) => r.data),
    enabled: !!token,
  });

  const sessions = useQuery({
    queryKey: ["sessions"],
    queryFn: () =>
      api
        .get<WorkoutSession[]>("/workouts/sessions?page=1&page_size=5")
        .then((r) => r.data),
    enabled: !!token,
  });

  if (!token) return null;

  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        {/* Plans section */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold">Workout Plans</h1>
            <NewPlanDialog />
          </div>
          {plans.isLoading ? (
            <p className="text-muted-foreground text-sm">Loading plans…</p>
          ) : plans.data?.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              No plans yet — create one to get started.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {plans.data?.map((plan) => (
                <PlanCard key={plan.id} plan={plan} />
              ))}
            </div>
          )}
        </section>

        <Separator />

        {/* Recent sessions */}
        <section>
          <h2 className="text-xl font-semibold mb-4">Recent Sessions</h2>
          {sessions.isLoading ? (
            <p className="text-muted-foreground text-sm">Loading sessions…</p>
          ) : sessions.data?.length === 0 ? (
            <p className="text-muted-foreground text-sm">
              No sessions yet — start one from a plan above.
            </p>
          ) : (
            <div className="space-y-2">
              {sessions.data?.map((s) => (
                <div
                  key={s.id}
                  className="flex items-center justify-between rounded-lg border px-4 py-3 text-sm"
                >
                  <span className="font-medium">
                    {format(new Date(s.started_at), "MMM d, yyyy")}
                  </span>
                  <div className="flex gap-4 text-muted-foreground">
                    {s.total_volume_kg !== null && (
                      <span>{s.total_volume_kg} kg total</span>
                    )}
                    <span>{formatDuration(s.duration_minutes)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
