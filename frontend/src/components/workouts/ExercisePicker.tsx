"use client";

import { useState, useEffect, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "@/lib/api";
import { Exercise } from "@/types/workout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Plus } from "lucide-react";

interface Props {
  onSelect: (exercise: Exercise) => void;
}

export function ExercisePicker({ onSelect }: Props) {
  const queryClient = useQueryClient();
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const { data } = useQuery({
    queryKey: ["exercises", query],
    queryFn: () =>
      api
        .get<{ data: Exercise[] }>(`/workouts/exercises?q=${encodeURIComponent(query)}`)
        .then((r) => r.data.data),
    enabled: query.length > 0,
  });

  const createMutation = useMutation({
    mutationFn: (name: string) =>
      api.post<Exercise>("/workouts/exercises", { name }).then((r) => r.data),
    onSuccess: (exercise) => {
      queryClient.invalidateQueries({ queryKey: ["exercises"] });
      onSelect(exercise);
      setQuery("");
      setOpen(false);
    },
  });

  // Close dropdown on outside click
  useEffect(() => {
    function handler(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const exercises = data ?? [];

  return (
    <div ref={containerRef} className="relative">
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          className="pl-8"
          placeholder="Search exercises…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
        />
      </div>
      {open && query.length > 0 && (
        <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
          {exercises.length > 0 ? (
            <ul>
              {exercises.map((ex) => (
                <li key={ex.id}>
                  <button
                    type="button"
                    className="w-full px-3 py-2 text-sm text-left hover:bg-accent transition-colors"
                    onClick={() => {
                      onSelect(ex);
                      setQuery("");
                      setOpen(false);
                    }}
                  >
                    {ex.name}
                    {ex.category && (
                      <span className="ml-2 text-xs text-muted-foreground">
                        {ex.category}
                      </span>
                    )}
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
          <div className="border-t p-2">
            <Button
              size="sm"
              variant="ghost"
              className="w-full justify-start text-sm"
              disabled={createMutation.isPending}
              onClick={() => createMutation.mutate(query)}
            >
              <Plus className="h-3.5 w-3.5 mr-1" />
              Create &quot;{query}&quot;
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
