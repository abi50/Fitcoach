"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, Suspense } from "react";
import { useAuthStore } from "@/store/auth";
import { Nav } from "@/components/layout/Nav";
import { SessionLogger } from "@/components/workouts/SessionLogger";

function SessionContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const planId = searchParams.get("planId") ?? undefined;

  useEffect(() => {
    if (!token) router.push("/login");
  }, [token, router]);

  if (!token) return null;

  return (
    <div className="min-h-screen bg-background">
      <Nav />
      <main className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Log Workout</h1>
        <SessionLogger planId={planId} />
      </main>
    </div>
  );
}

export default function SessionPage() {
  return (
    <Suspense>
      <SessionContent />
    </Suspense>
  );
}
