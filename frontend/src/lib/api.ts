/**
 * Python backend HTTP client.
 */

const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export async function analyzeContract(file: File, userId: string) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", userId);

  const res = await fetch(`${BACKEND_URL}/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Analysis failed: ${res.statusText}`);
  }

  return res.json();
}

export function getReportUrl(reviewId: string) {
  return `${BACKEND_URL}/report/${reviewId}`;
}

export function getPdfUrl(reviewId: string) {
  return `${BACKEND_URL}/pdf/${reviewId}`;
}
