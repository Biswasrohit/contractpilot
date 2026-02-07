/**
 * DAuth (Dedalus Auth) session helper for Next.js.
 *
 * DAuth is an OAuth 2.1 MCP server that secures user accounts & sessions.
 * Each user's legal documents are private and encrypted.
 *
 * `auth.subject` is the authenticated user ID — used as:
 *   - Convex `userId` for review ownership
 *   - Flowglad `customerExternalId` for billing
 */

export interface DAuthSession {
  subject: string;
  scopes: string[];
}

/**
 * Get the current DAuth session from the request.
 * In production, this validates the DAuth token from the Authorization header.
 * For development, falls back to a test user.
 */
export async function getDAuthSession(
  request: Request
): Promise<DAuthSession | null> {
  const authHeader = request.headers.get("Authorization");

  if (!authHeader?.startsWith("Bearer ")) {
    // Dev fallback — in production DAuth handles this via MCP
    if (process.env.NODE_ENV === "development") {
      return { subject: "dev-user", scopes: ["read", "reviews:write"] };
    }
    return null;
  }

  // In production, DAuth validates the token via its MCP server.
  // The Python backend handles actual DAuth validation through the Dedalus SDK.
  // This helper extracts the user identity for Next.js API routes.
  const token = authHeader.slice(7);

  try {
    const res = await fetch(`${process.env.DEDALUS_AS_URL}/userinfo`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) return null;

    const userinfo = await res.json();
    return {
      subject: userinfo.sub,
      scopes: userinfo.scopes ?? ["read"],
    };
  } catch {
    return null;
  }
}
