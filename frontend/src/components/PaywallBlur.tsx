"use client";

import { usePlan } from "@/contexts/PlanContext";
import { useRouter } from "next/navigation";

interface PaywallBlurProps {
  children: React.ReactNode;
  featureLabel: string;
  blurPx?: number;
  className?: string;
}

export default function PaywallBlur({
  children,
  featureLabel,
  blurPx = 10,
  className = "",
}: PaywallBlurProps) {
  const { isFree } = usePlan();
  const router = useRouter();

  if (!isFree) {
    return <>{children}</>;
  }

  return (
    <div className={`relative ${className}`}>
      <div
        className="pointer-events-none select-none"
        style={{ filter: `blur(${blurPx}px)` }}
        aria-hidden="true"
      >
        {children}
      </div>

      <div className="absolute inset-0 flex flex-col items-center justify-center z-20 bg-white/60 backdrop-blur-sm rounded-xl">
        <div className="text-center px-6">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <p className="text-sm font-semibold text-gray-900 mb-1">
            Unlock {featureLabel}
          </p>
          <p className="text-xs text-gray-500 mb-3">
            Upgrade to see the full analysis
          </p>
          <button
            onClick={() => router.push("/billing")}
            className="px-4 py-2 bg-blue-600 text-white text-xs font-medium rounded-lg hover:bg-blue-700 transition-colors"
          >
            Upgrade - $2.99
          </button>
        </div>
      </div>
    </div>
  );
}
