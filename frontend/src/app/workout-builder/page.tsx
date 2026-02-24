import Link from "next/link";
import { ArrowLeft, Construction } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function WorkoutBuilderPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center gap-6 px-4 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/10 border border-blue-500/20">
        <Construction className="h-8 w-8 text-blue-400" />
      </div>
      <h1 className="text-3xl font-bold">Workout Builder</h1>
      <p className="text-muted-foreground max-w-sm">
        The AI workout plan builder is coming in the next phase. Check back soon!
      </p>
      <Button asChild variant="outline" className="border-white/20">
        <Link href="/">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Home
        </Link>
      </Button>
    </div>
  );
}
