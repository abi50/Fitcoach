"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export function CtaBanner() {
  return (
    <section className="pb-24 px-4 sm:px-6 bg-zinc-950">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-80px" }}
        transition={{ duration: 0.5 }}
        className="max-w-6xl mx-auto rounded-3xl overflow-hidden relative"
        style={{
          background:
            "linear-gradient(135deg, #f97316 0%, #ea580c 50%, #c2410c 100%)",
        }}
      >
        {/* Dot-grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.08]"
          style={{
            backgroundImage:
              "radial-gradient(circle, #fff 1px, transparent 1px)",
            backgroundSize: "22px 22px",
          }}
        />

        {/* Diagonal accent block */}
        <div
          className="absolute top-0 right-0 w-[400px] h-full opacity-15"
          style={{
            background:
              "linear-gradient(145deg, transparent 40%, rgba(255,255,255,0.3) 40%, rgba(255,255,255,0.3) 55%, transparent 55%)",
          }}
        />

        <div className="relative z-10 px-8 py-20 text-center">
          {/* Section label */}
          <span className="inline-block text-white/60 text-[10px] font-black uppercase tracking-[0.2em] mb-4">
            Get Started Today
          </span>

          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black uppercase tracking-tighter text-white mb-4 leading-[0.95]">
            Ready to
            <br />
            Transform?
          </h2>
          <p className="text-white/65 text-lg mb-10 max-w-sm mx-auto font-medium">
            No account. No credit card. No commitment. Just results.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button
              asChild
              size="lg"
              className="w-full sm:w-auto bg-white text-orange-600 hover:bg-white/90 font-black uppercase tracking-wide text-sm px-10 h-14 rounded-xl shadow-2xl transition-all duration-200 hover:scale-[1.02]"
            >
              <Link href="/workout-builder">
                Build Workout Plan
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="w-full sm:w-auto font-bold uppercase tracking-wide text-sm px-10 h-14 border-white/40 text-white hover:bg-white/10 rounded-xl"
            >
              <Link href="/meal-builder">Build Meal Plan</Link>
            </Button>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
