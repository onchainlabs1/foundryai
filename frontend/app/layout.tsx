import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'
import { ThemeProvider } from '@/contexts/theme-context'
import { ThemeToggle } from '@/components/theme-toggle'
import { Toaster } from '@/components/ui/toaster'
import { 
  LayoutDashboard, 
  Target, 
  Package, 
  FileText, 
  Shield, 
  Lock, 
  AlertTriangle, 
  Eye, 
  Building, 
  Settings, 
  User,
  Search,
  Bell,
  Globe,
  Plus
} from 'lucide-react'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AIMS Studio',
  description: 'AI Governance Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          defaultTheme="light"
          storageKey="aims-ui-theme"
        >
          <div className="min-h-screen bg-background flex">
            {/* Sidebar */}
            <aside className="w-64 sidebar-bg flex flex-col">
              {/* Logo */}
              <div className="p-6 border-b border-border">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                    <span className="text-primary-foreground font-bold text-sm">A</span>
                  </div>
                  <span className="text-lg font-semibold">AIMS Studio</span>
                </div>
                <p className="text-sm text-muted-foreground mt-1">AI Governance</p>
              </div>

              {/* Navigation */}
              <nav className="flex-1 p-4 space-y-2">
                <div className="space-y-1">
                  <Link 
                    href="/" 
                    className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground"
                  >
                    <LayoutDashboard className="w-4 h-4" />
                    Dashboard
                  </Link>
                  <Link 
                    href="/onboarding" 
                    className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                  >
                    <Target className="w-4 h-4" />
                    Onboarding
                  </Link>
                  <Link 
                    href="/inventory" 
                    className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                  >
                    <Package className="w-4 h-4" />
                    Inventory
                  </Link>
                  <Link 
                    href="/documents" 
                    className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                  >
                    <FileText className="w-4 h-4" />
                    Obligations
                  </Link>
                  <Link 
                    href="/reports" 
                    className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                  >
                    <Shield className="w-4 h-4" />
                    Risk & FRIA
                  </Link>
                  <Link 
                    href="/templates" 
                    className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                  >
                    <Lock className="w-4 h-4" />
                    Controls
                  </Link>
                </div>

                <div className="pt-4">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Documents</p>
                  <div className="space-y-1">
                    <Link 
                      href="/documents" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <FileText className="w-4 h-4" />
                      Docs Generator
                    </Link>
                    <Link 
                      href="/eu-register" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <FileText className="w-4 h-4" />
                      EU Register
                    </Link>
                  </div>
                </div>

                <div className="pt-4">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">Operations</p>
                  <div className="space-y-1">
                    <Link 
                      href="/incidents" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <AlertTriangle className="w-4 h-4" />
                      Incidents
                    </Link>
                    <Link 
                      href="/transparency" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <Eye className="w-4 h-4" />
                      Transparency
                    </Link>
                    <Link 
                      href="/audit" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <Building className="w-4 h-4" />
                      Audit Room
                    </Link>
                  </div>
                </div>

                <div className="pt-4">
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">System</p>
                  <div className="space-y-1">
                    <Link 
                      href="/settings" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <Settings className="w-4 h-4" />
                      Settings
                    </Link>
                    <Link 
                      href="/accessibility" 
                      className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent"
                    >
                      <User className="w-4 h-4" />
                      Accessibility
                    </Link>
                  </div>
                </div>
              </nav>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
              {/* Header */}
              <header className="header-bg px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
                      <input 
                        type="text" 
                        placeholder="Search (⌘K)" 
                        className="pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90">
                      <Plus className="w-4 h-4" />
                      New System
                    </button>
                    <button className="relative p-2 text-muted-foreground hover:text-foreground">
                      <Bell className="w-5 h-5" />
                      <span className="absolute -top-1 -right-1 w-3 h-3 bg-destructive rounded-full text-xs text-destructive-foreground flex items-center justify-center">3</span>
                    </button>
                    <button className="p-2 text-muted-foreground hover:text-foreground">
                      <Globe className="w-5 h-5" />
                    </button>
                    <button className="p-2 text-muted-foreground hover:text-foreground">
                      <User className="w-5 h-5" />
                    </button>
                    <button className="px-4 py-2 bg-green-500 text-white rounded-lg text-sm font-medium hover:bg-green-600">
                      Update
                    </button>
                    <ThemeToggle />
                  </div>
                </div>
              </header>

              {/* Page Content */}
              <main className="flex-1 p-6 bg-muted/30">
                {children}
              </main>
            </div>
          </div>
        </ThemeProvider>
        <Toaster />
      </body>
    </html>
  )
}

