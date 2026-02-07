import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

export const getByReview = query({
  args: { reviewId: v.id("reviews") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("clauses")
      .withIndex("by_review", (q) => q.eq("reviewId", args.reviewId))
      .collect();
  },
});

export const addClause = mutation({
  args: {
    reviewId: v.id("reviews"),
    clauseText: v.string(),
    clauseType: v.optional(v.string()),
    riskLevel: v.string(),
    riskCategory: v.string(),
    explanation: v.string(),
    concern: v.optional(v.string()),
    suggestion: v.optional(v.string()),
    k2Reasoning: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("clauses", args);
  },
});
