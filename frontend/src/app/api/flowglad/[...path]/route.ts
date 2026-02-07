import { nextRouteHandler } from "@flowglad/nextjs/server";
import { flowglad } from "@/lib/flowglad";
import { NextRequest } from "next/server";

export const { GET, POST } = nextRouteHandler({
  getCustomerExternalId: async (req: NextRequest) => {
    // In production, extract from DAuth session.
    // For hackathon/dev, use a header or default to "dev-user".
    const userId = req.headers.get("x-user-id") ?? "dev-user";
    return userId;
  },
  flowglad,
});
