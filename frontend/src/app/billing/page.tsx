"use client";

import Link from "next/link";
import PricingCards from "@/components/PricingCards";

export default function BillingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-4xl mx-auto px-4 pt-16 pb-16">
        <div className="mb-6">
          <Link
            href="/"
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            &larr; Back to home
          </Link>
        </div>

        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            Simple Pricing
          </h1>
          <p className="text-gray-600 max-w-md mx-auto">
            Your first contract review is free. After that, each review is just
            $2.99 — cheaper than a coffee, smarter than a lawyer.
          </p>
        </div>

        <PricingCards />

        <div className="text-center mt-12 text-sm text-gray-400">
          Powered by{" "}
          <a
            href="https://flowglad.com"
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-gray-500"
          >
            Flowglad
          </a>
        </div>
      </div>
    </main>
  );
}
