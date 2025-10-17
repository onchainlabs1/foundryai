import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Link from 'next/link'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AIMS Readiness',
  description: 'ISO/IEC 42001 + EU AI Act compliance platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <nav className="border-b">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <Link href="/" className="text-xl font-bold">
                  AIMS Readiness
                </Link>
                            <div className="flex gap-6">
                              <Link href="/" className="hover:text-primary">Dashboard</Link>
                              <Link href="/inventory" className="hover:text-primary">Inventory</Link>
                              <Link href="/reports" className="hover:text-primary">Reports</Link>
                              <Link href="/templates" className="hover:text-primary">Templates</Link>
                              <Link href="/onboarding" className="hover:text-primary">Onboarding</Link>
                              <Link href="/login" className="hover:text-primary">Login</Link>
                            </div>
              </div>
            </div>
          </nav>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}

