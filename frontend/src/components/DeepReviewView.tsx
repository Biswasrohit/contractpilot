"use client";

import { useState, useMemo } from "react";
import PDFViewer, { ClauseHighlight } from "./PDFViewer";
import ClauseSidebar from "./ClauseSidebar";

interface Clause {
  _id: string;
  clauseType?: string;
  clauseText?: string;
  riskLevel: string;
  riskCategory: string;
  explanation: string;
  concern?: string;
  suggestion?: string;
  k2Reasoning?: string;
  pageNumber?: number;
  rects?: string; // JSON string
  pageWidth?: number;
  pageHeight?: number;
}

interface DeepReviewViewProps {
  pdfUrl: string;
  clauses: Clause[];
}

export default function DeepReviewView({ pdfUrl, clauses }: DeepReviewViewProps) {
  const [activeClauseId, setActiveClauseId] = useState<string | null>(null);

  // Transform clause data into highlight format for the PDF viewer
  const highlights: ClauseHighlight[] = useMemo(() => {
    return clauses
      .filter((c) => c.rects && c.pageNumber !== undefined)
      .map((c) => {
        let rects: { x0: number; y0: number; x1: number; y1: number }[] = [];
        try {
          rects = JSON.parse(c.rects || "[]");
        } catch {
          rects = [];
        }
        return {
          clauseId: c._id,
          pageNumber: c.pageNumber ?? 0,
          rects,
          pageWidth: c.pageWidth ?? 612,
          pageHeight: c.pageHeight ?? 792,
          riskLevel: c.riskLevel,
          clauseType: c.clauseType || "Clause",
          explanation: c.explanation,
        };
      });
  }, [clauses]);

  const handleClauseHover = (clauseId: string | null) => {
    setActiveClauseId(clauseId);
  };

  const handleClauseClick = (clauseId: string) => {
    setActiveClauseId(clauseId);
  };

  return (
    <div className="flex h-[calc(100vh-180px)] rounded-xl overflow-hidden border border-gray-200 bg-white">
      {/* Left: PDF Viewer (60%) */}
      <div className="w-3/5 border-r border-gray-200 overflow-hidden">
        <PDFViewer
          pdfUrl={pdfUrl}
          highlights={highlights}
          activeClauseId={activeClauseId}
          onClauseHover={handleClauseHover}
          onClauseClick={handleClauseClick}
        />
      </div>

      {/* Right: Clause Sidebar (40%) */}
      <div className="w-2/5 overflow-hidden">
        <ClauseSidebar
          clauses={clauses}
          activeClauseId={activeClauseId}
          onClauseHover={handleClauseHover}
          onClauseClick={handleClauseClick}
        />
      </div>
    </div>
  );
}
