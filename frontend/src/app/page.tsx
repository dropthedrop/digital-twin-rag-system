import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold">Digital Twin</CardTitle>
          <CardDescription>Professional AI-powered digital twin system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button asChild className="w-full">
            <Link href="/chat">Start Conversation</Link>
          </Button>
          <Button asChild variant="outline" className="w-full bg-transparent">
            <Link href="/admin">Admin Dashboard</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
