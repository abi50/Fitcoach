"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import api from "@/lib/api";
import { Exercise, SessionSet, WorkoutSession } from "@/types/workout";
import { ExercisePicker } from "./ExercisePicker";
import { PRCelebrationToast } from "./PRCelebrationToast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { Trophy, CheckCircle } from "lucide-react";

interface Props {
  planId?: string;
  onFinish?: (session: WorkoutSession) => void;
}

interface SetRow {
  exercise: Exercise;
  weight: string;
  reps: string;
  logged: SessionSet | null;
}

export function SessionLogger({ planId, onFinish }: Props) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [rows, setRows] = useState<SetRow[]>([]);
  const [prTrigger, setPrTrigger] = useState(0);
  const [finished, setFinished] = useState<WorkoutSession | null>(null);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);

  // Start session on first set log
  const startSession = useMutation({
    mutationFn: () =>
      api
        .post<WorkoutSession>("/workouts/sessions", {
          plan_id: planId ?? null,
          started_at: new Date().toISOString(),
        })
        .then((r) => r.data),
  });

  const logSet = useMutation({
    mutationFn: ({
      sid,
      exercise_id,
      weight_kg,
      reps,
      set_number,
    }: {
      sid: string;
      exercise_id: string;
      weight_kg: number;
      reps: number;
      set_number: number;
    }) =>
      api
        .post<SessionSet>(`/workouts/sessions/${sid}/sets`, {
          exercise_id,
          weight_kg,
          reps,
          set_number,
        })
        .then((r) => r.data),
  });

  const completeSession = useMutation({
    mutationFn: (sid: string) =>
      api
        .post<WorkoutSession>(`/workouts/sessions/${sid}/complete`)
        .then((r) => r.data),
    onSuccess: (session) => {
      setFinished(session);
      // Final PR check
      setPrTrigger((t) => t + 1);
      onFinish?.(session);
    },
  });

  async function handleAddExercise(exercise: Exercise) {
    setSelectedExercise(exercise);
    setRows((prev) => [
      ...prev,
      { exercise, weight: "", reps: "", logged: null },
    ]);
    setSelectedExercise(null);
  }

  async function handleLogSet(index: number) {
    const row = rows[index];
    const weight = parseFloat(row.weight);
    const reps = parseInt(row.reps, 10);

    if (isNaN(weight) || isNaN(reps) || weight <= 0 || reps <= 0) {
      toast.error("Enter valid weight and reps");
      return;
    }

    try {
      let sid = sessionId;
      if (!sid) {
        const session = await startSession.mutateAsync();
        sid = session.id;
        setSessionId(sid);
      }

      const setNumber =
        rows
          .slice(0, index + 1)
          .filter((r) => r.exercise.id === row.exercise.id && r.logged !== null)
          .length + 1;

      const logged = await logSet.mutateAsync({
        sid,
        exercise_id: row.exercise.id,
        weight_kg: weight,
        reps,
        set_number: setNumber,
      });

      setRows((prev) =>
        prev.map((r, i) => (i === index ? { ...r, logged } : r))
      );

      if (logged.is_pr) {
        setPrTrigger((t) => t + 1);
      }
    } catch {
      toast.error("Failed to log set");
    }
  }

  async function handleFinish() {
    if (!sessionId) {
      toast.error("No sets logged yet");
      return;
    }
    try {
      await completeSession.mutateAsync(sessionId);
    } catch {
      toast.error("Failed to finish session");
    }
  }

  if (finished) {
    return (
      <Card className="max-w-md mx-auto mt-8">
        <CardHeader className="text-center">
          <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-2" />
          <CardTitle>Workout Complete!</CardTitle>
        </CardHeader>
        <CardContent className="text-center space-y-2">
          {finished.duration_minutes !== null && (
            <p className="text-muted-foreground">
              Duration: <strong>{finished.duration_minutes} min</strong>
            </p>
          )}
          {finished.total_volume_kg !== null && (
            <p className="text-muted-foreground">
              Total volume: <strong>{finished.total_volume_kg} kg</strong>
            </p>
          )}
          <Button className="mt-4 w-full" onClick={() => window.location.href = "/workouts"}>
            Back to Plans
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <PRCelebrationToast trigger={prTrigger} />

      {/* Logged sets */}
      {rows.length > 0 && (
        <div className="space-y-2">
          {rows.map((row, i) => (
            <Card key={i}>
              <CardContent className="pt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-sm">{row.exercise.name}</span>
                  {row.logged?.is_pr && (
                    <Badge className="gap-1">
                      <Trophy className="h-3 w-3" /> PR
                    </Badge>
                  )}
                </div>
                {row.logged ? (
                  <p className="text-sm text-muted-foreground">
                    {row.logged.weight_kg} kg × {row.logged.reps} reps — logged
                  </p>
                ) : (
                  <div className="flex gap-2">
                    <Input
                      type="number"
                      placeholder="Weight (kg)"
                      value={row.weight}
                      onChange={(e) =>
                        setRows((prev) =>
                          prev.map((r, idx) =>
                            idx === i ? { ...r, weight: e.target.value } : r
                          )
                        )
                      }
                      className="w-32"
                      min={0}
                      step={0.5}
                    />
                    <Input
                      type="number"
                      placeholder="Reps"
                      value={row.reps}
                      onChange={(e) =>
                        setRows((prev) =>
                          prev.map((r, idx) =>
                            idx === i ? { ...r, reps: e.target.value } : r
                          )
                        )
                      }
                      className="w-24"
                      min={1}
                    />
                    <Button
                      size="sm"
                      onClick={() => handleLogSet(i)}
                      disabled={logSet.isPending || startSession.isPending}
                    >
                      Log Set
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Separator />

      {/* Add exercise */}
      <div className="space-y-2">
        <p className="text-sm font-medium">Add Exercise</p>
        <ExercisePicker onSelect={handleAddExercise} />
      </div>

      {/* Finish button */}
      {sessionId && (
        <Button
          variant="default"
          className="w-full"
          onClick={handleFinish}
          disabled={completeSession.isPending}
        >
          {completeSession.isPending ? "Finishing…" : "Finish Workout"}
        </Button>
      )}

      {/* Suppress unused var warning */}
      {selectedExercise && null}
    </div>
  );
}
