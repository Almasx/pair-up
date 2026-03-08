import { v } from "convex/values";
import { query, mutation } from "./_generated/server";

export const list = query({
  handler: async (ctx) => {
    return await ctx.db.query("sessions").collect();
  },
});

export const create = mutation({
  args: {
    intervieweeId: v.id("users"),
    interviewerId: v.id("users"),
    status: v.string(),
    scheduledAt: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("sessions", args);
  },
});
