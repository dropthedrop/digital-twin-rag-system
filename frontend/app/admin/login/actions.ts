"use server"

import { createSession, rateLimit } from "@/lib/auth"
import { headers } from "next/headers"

export async function loginAction(formData: FormData) {
  const password = formData.get("password") as string

  // Get client IP for rate limiting
  const headersList = await headers()
  const forwardedFor = headersList.get("x-forwarded-for")
  const clientIP = forwardedFor ? forwardedFor.split(",")[0] : "unknown"

  // Rate limiting
  const rateLimitResult = rateLimit(`login:${clientIP}`, 5, 15 * 60 * 1000)
  if (!rateLimitResult.success) {
    return {
      success: false,
      error: "Too many login attempts. Please try again later.",
    }
  }

  // Simple password check (in production, use proper hashing)
  const adminPassword = process.env.ADMIN_PASSWORD || "admin123"

  if (password !== adminPassword) {
    return {
      success: false,
      error: "Invalid password",
    }
  }

  // Create session
  await createSession("admin", true)

  return { success: true }
}
