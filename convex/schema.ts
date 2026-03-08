import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    role: v.string(),
  }).index("by_email", ["email"]),

  sessions: defineTable({
    intervieweeId: v.id("users"),
    interviewerId: v.id("users"),
    status: v.string(),
    scheduledAt: v.string(),
  }),
});
