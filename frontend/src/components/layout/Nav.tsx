"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { Button } from "@/components/ui/button";
import { Dumbbell } from "lucide-react";

export function Nav() {
  const router = useRouter();
  const clearToken = useAuthStore((s) => s.clearToken);

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <header className="border-b">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/workouts" className="flex items-center gap-2 font-semibold text-lg">
          <Dumbbell className="h-5 w-5" />
          FitCoach AI
        </Link>
        <nav className="flex items-center gap-4">
          <Link
            href="/workouts"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Workouts
          </Link>
          <Button variant="outline" size="sm" onClick={handleLogout}>
            Logout
          </Button>
        </nav>
      </div>
    </header>
  );
}
