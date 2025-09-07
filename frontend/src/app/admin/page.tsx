import { requireAuth } from "@/lib/auth"
import { AdminDashboard } from "./dashboard"

export default async function AdminPage() {
  await requireAuth()

  return <AdminDashboard />
}
