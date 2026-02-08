"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

type Plan = "free" | "paid";

interface PlanContextValue {
  plan: Plan;
  setPlan: (plan: Plan) => void;
  isFree: boolean;
}

const PlanContext = createContext<PlanContextValue>({
  plan: "free",
  setPlan: () => {},
  isFree: true,
});

export function PlanProvider({ children }: { children: ReactNode }) {
  const [plan, setPlanState] = useState<Plan>("free");

  useEffect(() => {
    const stored = localStorage.getItem("contractpilot_plan") as Plan | null;
    if (stored === "free" || stored === "paid") {
      setPlanState(stored);
    }
  }, []);

  const setPlan = (newPlan: Plan) => {
    setPlanState(newPlan);
    localStorage.setItem("contractpilot_plan", newPlan);
  };

  return (
    <PlanContext.Provider value={{ plan, setPlan, isFree: plan === "free" }}>
      {children}
    </PlanContext.Provider>
  );
}

export function usePlan() {
  return useContext(PlanContext);
}
