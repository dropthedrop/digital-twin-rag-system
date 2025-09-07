'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Send, Bot, User, ArrowLeft, Clock, Database } from "lucide-react"
import Link from "next/link"

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  metadata?: {
    latency?: number
    sources?: string[]
    confidence?: number
  }
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      role: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input.trim() }),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.response,
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          latency: data.latency,
          sources: data.sources,
          confidence: data.confidence
        }
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
      console.error('Chat error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/">
                <ArrowLeft className="h-4 w-4" />
              </Link>
            </Button>
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              <div>
                <h1 className="font-semibold">Digital Twin AI</h1>
                <p className="text-sm text-muted-foreground">RAG-powered assistant</p>
              </div>
            </div>
          </div>
          <Badge variant="outline" className="gap-1">
            <Database className="h-3 w-3" />
            Connected
          </Badge>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="container mx-auto max-w-4xl space-y-4">
          {messages.length === 0 && (
            <Card>
              <CardContent className="pt-6">
                <div className="text-center text-muted-foreground space-y-2">
                  <Bot className="h-12 w-12 mx-auto opacity-50" />
                  <p className="text-lg font-medium">Welcome to Digital Twin AI</p>
                  <p className="text-sm">Ask me anything about the knowledge base. I use advanced RAG technology to provide accurate, contextual responses.</p>
                </div>
              </CardContent>
            </Card>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <Card className={`max-w-[80%] ${message.role === 'user' ? 'bg-primary text-primary-foreground' : ''}`}>
                <CardContent className="pt-4">
                  <div className="flex items-start gap-3">
                    <div className={`p-2 rounded-full ${message.role === 'user' ? 'bg-primary-foreground/20' : 'bg-primary/10'}`}>
                      {message.role === 'user' ? (
                        <User className="h-4 w-4" />
                      ) : (
                        <Bot className="h-4 w-4" />
                      )}
                    </div>
                    <div className="flex-1 space-y-2">
                      <p className="text-sm leading-relaxed">{message.content}</p>
                      
                      {/* Metadata for assistant messages */}
                      {message.role === 'assistant' && message.metadata && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {message.metadata.latency && (
                            <Badge variant="secondary" className="text-xs gap-1">
                              <Clock className="h-3 w-3" />
                              {message.metadata.latency.toFixed(3)}s
                            </Badge>
                          )}
                          {message.metadata.confidence && (
                            <Badge variant="secondary" className="text-xs">
                              {(message.metadata.confidence * 100).toFixed(1)}% confidence
                            </Badge>
                          )}
                          {message.metadata.sources && message.metadata.sources.length > 0 && (
                            <Badge variant="secondary" className="text-xs">
                              {message.metadata.sources.length} sources
                            </Badge>
                          )}
                        </div>
                      )}
                      
                      <p className="text-xs opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}

          {isLoading && (
            <div className="flex justify-start">
              <Card className="max-w-[80%]">
                <CardContent className="pt-4">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-primary/10">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {error && (
            <Alert variant="destructive">
              <AlertDescription>
                Error: {error}
              </AlertDescription>
            </Alert>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t bg-card p-4">
        <div className="container mx-auto max-w-4xl">
          <form onSubmit={sendMessage} className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about the knowledge base..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </div>
  )
}