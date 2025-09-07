"use client"

import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"
import { logoutAction } from "./actions"
import { LogOut } from "lucide-react"

export function LogoutButton() {
  const router = useRouter()

  async function handleLogout() {
    await logoutAction()
    router.push("/admin/login")
    router.refresh()
  }

  return (
    <Button variant="outline" onClick={handleLogout} className="w-full justify-start gap-2 bg-transparent">
      <LogOut className="h-4 w-4" />
      Logout
    </Button>
  )
}
