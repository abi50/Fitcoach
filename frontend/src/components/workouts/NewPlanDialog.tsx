"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "sonner";
import { Plus } from "lucide-react";

const GOALS = [
  "strength",
  "hypertrophy",
  "endurance",
  "weight_loss",
  "maintenance",
];

export function NewPlanDialog() {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [goal, setGoal] = useState("strength");
  const [daysPerWeek, setDaysPerWeek] = useState(3);
  const [durationWeeks, setDurationWeeks] = useState<number | "">("");

  const mutation = useMutation({
    mutationFn: (data: {
      name: string;
      goal: string;
      days_per_week: number;
      duration_weeks?: number;
    }) => api.post("/workouts/plans", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plans"] });
      toast.success("Plan created!");
      setOpen(false);
      setName("");
      setGoal("strength");
      setDaysPerWeek(3);
      setDurationWeeks("");
    },
    onError: () => toast.error("Failed to create plan"),
  });

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({
      name,
      goal,
      days_per_week: daysPerWeek,
      ...(durationWeeks !== "" && { duration_weeks: durationWeeks }),
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-1" />
          New Plan
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Workout Plan</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <Label htmlFor="plan-name">Plan Name</Label>
            <Input
              id="plan-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Push Pull Legs"
              required
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="goal">Goal</Label>
            <select
              id="goal"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
            >
              {GOALS.map((g) => (
                <option key={g} value={g}>
                  {g.replace("_", " ")}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="days">Days / week</Label>
              <Input
                id="days"
                type="number"
                min={1}
                max={7}
                value={daysPerWeek}
                onChange={(e) => setDaysPerWeek(Number(e.target.value))}
                required
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="duration">Duration (weeks)</Label>
              <Input
                id="duration"
                type="number"
                min={1}
                value={durationWeeks}
                onChange={(e) =>
                  setDurationWeeks(
                    e.target.value === "" ? "" : Number(e.target.value)
                  )
                }
                placeholder="optional"
              />
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={mutation.isPending}>
            {mutation.isPending ? "Creating…" : "Create Plan"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
