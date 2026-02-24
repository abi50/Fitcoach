"use client";

import Link from "next/link";
import { Dumbbell } from "lucide-react";
import { Button } from "@/components/ui/button";

export function LandingNav() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-zinc-950/95 backdrop-blur-md border-b border-white/5">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2.5 font-black text-xl tracking-tight"
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-500">
            <Dumbbell className="h-5 w-5 text-white" />
          </div>
          <span className="text-white">FitCoach</span>
          <span className="text-orange-500">AI</span>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-sm font-semibold text-white/50 hover:text-white transition-colors hidden sm:block uppercase tracking-wide"
          >
            Sign In
          </Link>
          <Button
            asChild
            size="sm"
            className="bg-orange-500 hover:bg-orange-400 text-white font-black uppercase tracking-wide text-xs px-5 h-9 rounded-lg shadow-lg shadow-orange-500/20"
          >
            <Link href="/register">Get Started Free</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
