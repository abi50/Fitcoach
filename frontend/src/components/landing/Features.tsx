"use client";

import { motion } from "framer-motion";
import { Zap, UtensilsCrossed, Trophy } from "lucide-react";

const features = [
  {
    icon: Zap,
    accentClass: "bg-orange-500",
    iconClass: "text-orange-500",
    tag: "Most Popular",
    title: "AI Workout Plans",
    description:
      "GPT-4o builds your perfect weekly program — tailored to your goals, experience level, and available equipment. Download as PDF or save to your profile.",
  },
  {
    icon: UtensilsCrossed,
    accentClass: "bg-amber-400",
    iconClass: "text-amber-400",
    tag: null,
    title: "Smart Meal Plans",
    description:
      "Calorie-matched, macro-optimized daily meals designed around your body and training style. Protein targets, meal timing, and prep tips included.",
  },
  {
    icon: Trophy,
    accentClass: "bg-yellow-400",
    iconClass: "text-yellow-400",
    tag: null,
    title: "Track Every PR",
    description:
      "Log your sessions, detect personal records automatically, and celebrate every milestone. Watch your strength grow week over week.",
  },
];

const containerVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
};

export function Features() {
  return (
    <section className="bg-zinc-950">
      {/* Ticker strip */}
      <div className="bg-orange-500 py-3 overflow-hidden">
        <div className="flex items-center gap-10 whitespace-nowrap text-white text-xs font-black uppercase tracking-widest justify-center flex-wrap sm:flex-nowrap">
          {[
            "AI Workout Plans",
            "Smart Meal Plans",
            "Personal Records",
            "Recovery Scores",
            "Free to Start",
            "No Account Required",
          ].map((item) => (
            <span key={item} className="flex items-center gap-3">
              <span className="w-1 h-1 rounded-full bg-white/50 inline-block" />
              {item}
            </span>
          ))}
        </div>
      </div>

      <div className="py-28 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto">
          {/* Section label + heading */}
          <div className="text-center mb-16">
            <span className="inline-block text-orange-500 text-[10px] font-black uppercase tracking-[0.2em] mb-4">
              Why FitCoach AI
            </span>
            <h2 className="text-4xl sm:text-5xl font-black tracking-tighter text-white uppercase leading-[1.0]">
              Train Smarter.
              <br />
              <span className="text-white/30">Not Harder.</span>
            </h2>
          </div>

          {/* Cards */}
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-80px" }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
          >
            {features.map((feature) => (
              <motion.div
                key={feature.title}
                variants={cardVariants}
                className="relative group rounded-2xl bg-zinc-900 hover:bg-zinc-800 transition-colors duration-300 border border-white/5 overflow-hidden"
              >
                {/* Colored top bar */}
                <div className={`h-1 w-full ${feature.accentClass}`} />

                <div className="p-8">
                  {/* Tag */}
                  {feature.tag && (
                    <span className="inline-block text-[10px] font-black text-orange-500 uppercase tracking-widest mb-4">
                      {feature.tag}
                    </span>
                  )}

                  {/* Icon */}
                  <div className="mb-5">
                    <feature.icon className={`h-7 w-7 ${feature.iconClass}`} />
                  </div>

                  {/* Text */}
                  <h3 className="text-lg font-black text-white uppercase tracking-tight mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-white/45 leading-relaxed text-sm">
                    {feature.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
