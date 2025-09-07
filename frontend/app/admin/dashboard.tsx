"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { LogoutButton } from "./logout-button"
import {
  BarChart3,
  FileText,
  Database,
  Settings,
  Monitor,
  Menu,
  X,
  Activity,
  Users,
  MessageSquare,
  TrendingUp,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navigationItems = [
  {
    title: "Overview & Analytics",
    icon: BarChart3,
    id: "overview",
    description: "System metrics and chat analytics",
  },
  {
    title: "Content Management",
    icon: FileText,
    id: "content",
    description: "Edit professional data and content",
  },
  {
    title: "Embedding Management",
    icon: Database,
    id: "embeddings",
    description: "Manage vector database and embeddings",
  },
  {
    title: "Database Operations",
    icon: Settings,
    id: "database",
    description: "PostgreSQL management and operations",
  },
  {
    title: "System Monitoring",
    icon: Monitor,
    id: "monitoring",
    description: "Real-time logs and performance metrics",
  },
]

export function AdminDashboard() {
  const [activeSection, setActiveSection] = useState("overview")
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-64 bg-card border-r border-border transform transition-transform duration-200 ease-in-out lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex flex-col h-full">
          {/* Sidebar header */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <div>
              <h2 className="text-lg font-semibold">Admin Dashboard</h2>
              <p className="text-sm text-muted-foreground">Digital Twin System</p>
            </div>
            <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setSidebarOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  setActiveSection(item.id)
                  setSidebarOpen(false)
                }}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors",
                  activeSection === item.id
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent hover:text-accent-foreground",
                )}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                <span className="text-sm font-medium">{item.title}</span>
              </button>
            ))}
          </nav>

          {/* Sidebar footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center gap-2 mb-3">
              <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-muted-foreground">System Online</span>
            </div>
            <LogoutButton />
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="bg-card border-b border-border px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
                <Menu className="h-4 w-4" />
              </Button>
              <div>
                <h1 className="text-2xl font-bold">
                  {navigationItems.find((item) => item.id === activeSection)?.title}
                </h1>
                <p className="text-sm text-muted-foreground">
                  {navigationItems.find((item) => item.id === activeSection)?.description}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                <Activity className="h-3 w-3 mr-1" />
                Active
              </Badge>
            </div>
          </div>
        </header>

        {/* Content area */}
        <main className="p-6">
          {activeSection === "overview" && <OverviewContent />}
          {activeSection === "content" && <ContentManagementPlaceholder />}
          {activeSection === "embeddings" && <EmbeddingManagementPlaceholder />}
          {activeSection === "database" && <DatabaseOperationsPlaceholder />}
          {activeSection === "monitoring" && <SystemMonitoringPlaceholder />}
        </main>
      </div>
    </div>
  )
}

function OverviewContent() {
  return (
    <div className="space-y-6">
      {/* Quick stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Conversations</p>
                <p className="text-2xl font-bold">1,234</p>
              </div>
              <MessageSquare className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Active Users</p>
                <p className="text-2xl font-bold">89</p>
              </div>
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Response Time</p>
                <p className="text-2xl font-bold">1.2s</p>
              </div>
              <Activity className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold">98.5%</p>
              </div>
              <TrendingUp className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main content cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest system events and user interactions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="h-2 w-2 bg-blue-500 rounded-full" />
                <div className="flex-1">
                  <p className="text-sm font-medium">New conversation started</p>
                  <p className="text-xs text-muted-foreground">2 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="h-2 w-2 bg-green-500 rounded-full" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Content updated successfully</p>
                  <p className="text-xs text-muted-foreground">15 minutes ago</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                <div className="h-2 w-2 bg-orange-500 rounded-full" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Embeddings regenerated</p>
                  <p className="text-xs text-muted-foreground">1 hour ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>Current system status and performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Database Connection</span>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Healthy</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Vector Database</span>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Operational</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">API Response</span>
                <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Slow</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Storage Usage</span>
                <span className="text-sm text-muted-foreground">67% (2.1GB)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function ContentManagementPlaceholder() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Content Management</CardTitle>
        <CardDescription>This section will be implemented in the next task</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Coming soon: Professional data editor, JSON content management, and content chunks management.
        </p>
      </CardContent>
    </Card>
  )
}

function EmbeddingManagementPlaceholder() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Embedding Management</CardTitle>
        <CardDescription>This section will be implemented in a future task</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Coming soon: Vector database operations, embedding analytics, and regeneration tools.
        </p>
      </CardContent>
    </Card>
  )
}

function DatabaseOperationsPlaceholder() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Database Operations</CardTitle>
        <CardDescription>This section will be implemented in a future task</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">
          Coming soon: PostgreSQL management, data migration tools, and performance monitoring.
        </p>
      </CardContent>
    </Card>
  )
}

function SystemMonitoringPlaceholder() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>System Monitoring</CardTitle>
        <CardDescription>This section will be implemented in a future task</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground">Coming soon: Real-time logs, operational data, and performance metrics.</p>
      </CardContent>
    </Card>
  )
}
