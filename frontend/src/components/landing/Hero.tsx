"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

const stats = [
  { value: "30s", label: "Plan generation" },
  { value: "GPT-4o", label: "AI engine" },
  { value: "Free", label: "No card needed" },
];

export function Hero() {
  return (
    <section
      className="relative min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 overflow-hidden pt-16 bg-zinc-950"
      style={{
        backgroundImage:
          "radial-gradient(circle, rgba(249,115,22,0.07) 1px, transparent 1px)",
        backgroundSize: "28px 28px",
      }}
    >
      {/* Orange diagonal accent block — top-right */}
      <div
        className="pointer-events-none absolute top-0 right-0 w-[700px] h-[600px] -z-0 opacity-15"
        aria-hidden="true"
        style={{
          background:
            "linear-gradient(145deg, transparent 35%, #f97316 35%, #f97316 55%, transparent 55%)",
        }}
      />

      {/* Radial orange glow — center */}
      <div
        className="pointer-events-none absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] -z-0"
        aria-hidden="true"
        style={{
          background:
            "radial-gradient(circle, rgba(249,115,22,0.10) 0%, transparent 65%)",
        }}
      />

      <div className="relative z-10 max-w-5xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="inline-flex items-center gap-2 rounded-full border border-orange-500/40 bg-orange-500/10 px-4 py-1.5 text-xs text-orange-400 font-black uppercase tracking-widest mb-8"
        >
          <Zap className="h-3 w-3 fill-orange-400" />
          AI-Powered · GPT-4o · Free to Try
        </motion.div>

        {/* Headline */}
        <motion.h1
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-6xl sm:text-7xl lg:text-[90px] font-black tracking-tighter leading-[0.93] mb-6 text-white uppercase"
        >
          Your Fitness
          <br />
          Plan,{" "}
          <span className="text-orange-500">Built</span>
          <br />
          by AI.
        </motion.h1>

        {/* Subheadline */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="text-lg sm:text-xl text-white/55 max-w-xl mx-auto mb-10 font-medium leading-relaxed"
        >
          Tell us your goals. Get a complete workout or meal plan in seconds —
          personalized to your body, equipment, and schedule.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-20"
        >
          <Button
            asChild
            size="lg"
            className="w-full sm:w-auto bg-orange-500 hover:bg-orange-400 text-white font-black uppercase tracking-wide text-sm px-10 h-14 rounded-xl shadow-2xl shadow-orange-500/30 transition-all duration-200 hover:scale-[1.02]"
          >
            <Link href="/workout-builder">
              Build My Workout Plan
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
          <Button
            asChild
            variant="outline"
            size="lg"
            className="w-full sm:w-auto font-bold uppercase tracking-wide text-sm px-10 h-14 border-white/20 text-white hover:bg-white/8 hover:border-white/40 rounded-xl transition-all duration-200"
          >
            <Link href="/meal-builder">
              Build My Meal Plan
              <ArrowRight className="ml-2 h-4 w-4" />
            </Link>
          </Button>
        </motion.div>

        {/* Stats strip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="flex flex-col sm:flex-row items-center justify-center divide-y sm:divide-y-0 sm:divide-x divide-white/8 border border-white/8 rounded-2xl bg-white/[0.03] overflow-hidden"
        >
          {stats.map((stat) => (
            <div key={stat.label} className="flex-1 text-center py-5 px-10">
              <div className="text-3xl font-black text-white">{stat.value}</div>
              <div className="text-[10px] text-white/40 uppercase tracking-[0.15em] mt-0.5 font-bold">
                {stat.label}
              </div>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <div className="w-0.5 h-8 rounded-full bg-orange-500/40 animate-pulse" />
      </motion.div>
    </section>
  );
}
