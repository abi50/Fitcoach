"use client";

import { useEffect } from "react";
import api from "@/lib/api";
import { PersonalRecord } from "@/types/workout";
import { toast } from "sonner";

interface Props {
  /** Trigger a PR check whenever this value changes */
  trigger: number;
}

export function PRCelebrationToast({ trigger }: Props) {
  useEffect(() => {
    if (trigger === 0) return;

    let cancelled = false;

    async function checkPRs() {
      try {
        const res = await api.get<PersonalRecord[]>(
          "/personal-records/pending-celebrations"
        );
        const prs = res.data;
        if (cancelled) return;

        for (const pr of prs) {
          toast.success(
            `🏆 New Personal Record! ${pr.exercise_name} — ${pr.weight_kg} kg × ${pr.reps} reps`,
            {
              duration: 6000,
              onDismiss: () => {
                api
                  .post(`/personal-records/${pr.id}/celebrate`)
                  .catch(() => null);
              },
              onAutoClose: () => {
                api
                  .post(`/personal-records/${pr.id}/celebrate`)
                  .catch(() => null);
              },
            }
          );
        }
      } catch {
        // silently ignore — PR celebration is non-critical
      }
    }

    checkPRs();
    return () => {
      cancelled = true;
    };
  }, [trigger]);

  return null;
}
