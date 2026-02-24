import Link from "next/link";
import { Dumbbell } from "lucide-react";

export function Footer() {
  return (
    <footer className="bg-zinc-950 border-t border-white/5 py-10 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 font-black text-sm hover:opacity-80 transition-opacity"
        >
          <div className="flex h-7 w-7 items-center justify-center rounded bg-orange-500">
            <Dumbbell className="h-3.5 w-3.5 text-white" />
          </div>
          <span className="text-white">FitCoach</span>
          <span className="text-orange-500">AI</span>
        </Link>

        {/* Links */}
        <nav className="flex items-center gap-6 text-[10px] text-white/35 font-black uppercase tracking-widest">
          <Link
            href="/workout-builder"
            className="hover:text-white transition-colors"
          >
            Workout Builder
          </Link>
          <Link
            href="/meal-builder"
            className="hover:text-white transition-colors"
          >
            Meal Builder
          </Link>
          <Link href="/login" className="hover:text-white transition-colors">
            Sign In
          </Link>
          <Link href="/register" className="hover:text-white transition-colors">
            Register
          </Link>
        </nav>

        {/* Copyright */}
        <p className="text-[10px] text-white/25 font-semibold uppercase tracking-widest">
          © {new Date().getFullYear()} FitCoach AI
        </p>
      </div>
    </footer>
  );
}
