import { NextRequest, NextResponse } from "next/server";
import { flowglad } from "@/lib/flowglad";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");

    if (!file || !(file instanceof Blob)) {
      return NextResponse.json({ error: "No file provided" }, { status: 400 });
    }

    // In production, DAuth provides this. For dev, use header or default.
    const userId = request.headers.get("x-user-id") ?? "dev-user";

    // Check Flowglad billing — first review free, then $2.99/contract
    try {
      const fg = flowglad(userId);
      const billing = await fg.getBilling();
      const balance = billing.checkUsageBalance("contract_reviews");
      if (balance && balance.availableBalance <= 0) {
        return NextResponse.json(
          { error: "Upgrade required", code: "BILLING_REQUIRED" },
          { status: 402 }
        );
      }
    } catch {
      // If Flowglad is not configured or billing check fails,
      // allow the request through (graceful degradation for hackathon)
      console.warn("Flowglad billing check skipped");
    }

    // Forward to Python backend
    const backendForm = new FormData();
    backendForm.append("file", file);
    backendForm.append("user_id", userId);

    const res = await fetch(`${BACKEND_URL}/analyze`, {
      method: "POST",
      body: backendForm,
    });

    if (!res.ok) {
      return NextResponse.json(
        { error: "Analysis service unavailable" },
        { status: 502 }
      );
    }

    const data = await res.json();

    // Record usage event after successful submission
    try {
      const fg = flowglad(userId);
      const billing = await fg.getBilling();
      const sub = billing.currentSubscription;
      if (sub) {
        await fg.createUsageEvent({
          usageMeterSlug: "contract_reviews",
          amount: 1,
          subscriptionId: sub.id,
          transactionId: `review-${data.review_id}-${Date.now()}`,
        });
      }
    } catch {
      console.warn("Flowglad usage event skipped");
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Review upload error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
