"use client";

import { useRouter } from "next/navigation";
import { WorkoutPlan } from "@/types/workout";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Calendar, Target } from "lucide-react";

interface Props {
  plan: WorkoutPlan;
}

export function PlanCard({ plan }: Props) {
  const router = useRouter();

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{plan.name}</CardTitle>
          {plan.is_active && <Badge variant="default">Active</Badge>}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <span className="flex items-center gap-1">
            <Target className="h-3.5 w-3.5" />
            {plan.goal}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="h-3.5 w-3.5" />
            {plan.days_per_week}x / week
          </span>
        </div>
        <Button
          size="sm"
          className="w-full"
          onClick={() => router.push(`/workouts/session?planId=${plan.id}`)}
        >
          Start Session
        </Button>
      </CardContent>
    </Card>
  );
}
