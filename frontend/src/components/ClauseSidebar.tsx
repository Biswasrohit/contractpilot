"use client";

import { useRef, useEffect } from "react";

interface ClauseData {
  _id: string;
  clauseType?: string;
  riskLevel: string;
  riskCategory: string;
  explanation: string;
  concern?: string;
  suggestion?: string;
  pageNumber?: number;
}

interface ClauseSidebarProps {
  clauses: ClauseData[];
  activeClauseId: string | null;
  onClauseHover: (clauseId: string | null) => void;
  onClauseClick: (clauseId: string) => void;
}

const RISK_BADGE: Record<string, string> = {
  high: "bg-red-100 text-red-700 border-red-200",
  medium: "bg-amber-100 text-amber-700 border-amber-200",
  low: "bg-green-100 text-green-700 border-green-200",
};

const CATEGORY_BADGE: Record<string, string> = {
  financial: "bg-red-50 text-red-600",
  compliance: "bg-amber-50 text-amber-600",
  operational: "bg-blue-50 text-blue-600",
  reputational: "bg-purple-50 text-purple-600",
};

export default function ClauseSidebar({
  clauses,
  activeClauseId,
  onClauseHover,
  onClauseClick,
}: ClauseSidebarProps) {
  const cardRefs = useRef<Map<string, HTMLDivElement>>(new Map());

  // Auto-scroll to active clause card
  useEffect(() => {
    if (!activeClauseId) return;
    const el = cardRefs.current.get(activeClauseId);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [activeClauseId]);

  return (
    <div className="h-full overflow-y-auto p-4 space-y-3">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
        Clause Analysis ({clauses.length})
      </h3>

      {clauses.map((clause) => {
        const isActive = activeClauseId === clause._id;
        return (
          <div
            key={clause._id}
            ref={(el) => {
              if (el) cardRefs.current.set(clause._id, el);
            }}
            className={`rounded-lg border p-4 cursor-pointer transition-all duration-150 ${
              isActive
                ? "border-blue-400 bg-blue-50 shadow-md ring-1 ring-blue-200"
                : "border-gray-200 bg-white hover:border-gray-300 hover:shadow-sm"
            }`}
            onMouseEnter={() => onClauseHover(clause._id)}
            onMouseLeave={() => onClauseHover(null)}
            onClick={() => onClauseClick(clause._id)}
          >
            {/* Header: type + badges */}
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className="font-medium text-sm text-gray-900 truncate max-w-[200px]">
                {clause.clauseType || "Clause"}
              </span>
              <span
                className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded border ${
                  RISK_BADGE[clause.riskLevel] || RISK_BADGE.medium
                }`}
              >
                {clause.riskLevel}
              </span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded ${
                  CATEGORY_BADGE[clause.riskCategory] || CATEGORY_BADGE.operational
                }`}
              >
                {clause.riskCategory}
              </span>
              {clause.pageNumber !== undefined && (
                <span className="text-[10px] text-gray-400 ml-auto">
                  p.{clause.pageNumber + 1}
                </span>
              )}
            </div>

            {/* Explanation */}
            <p className="text-sm text-gray-600 leading-relaxed line-clamp-3">
              {clause.explanation}
            </p>

            {/* Concern */}
            {clause.concern && (
              <div className="mt-2 text-xs text-amber-700 bg-amber-50 rounded px-2 py-1">
                <span className="font-medium">Watch out:</span> {clause.concern}
              </div>
            )}

            {/* Suggestion */}
            {clause.suggestion && (
              <div className="mt-1.5 text-xs text-blue-700 bg-blue-50 rounded px-2 py-1">
                <span className="font-medium">Suggestion:</span> {clause.suggestion}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
