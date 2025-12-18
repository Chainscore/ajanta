import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JamCode.Fun - JAM Service Development IDE | Polkadot JAM Chain",
  description:
    "Build and deploy JAM services on Polkadot Join-Accumulate Machine. Browser-based IDE for Python, C, and C++ smart contract development. Compile to PVM bytecode and simulate execution.",
  keywords: [
    "JAM",
    "Join Accumulate Machine",
    "Polkadot",
    "JAM Chain",
    "JAM Services",
    "PVM",
    "Polkadot Virtual Machine",
    "blockchain development",
    "smart contracts",
    "Web3 IDE",
    "Polkadot SDK",
    "JAM protocol",
    "accumulate",
    "refine",
    "blockchain IDE",
    "crypto development",
    "Substrate",
    "decentralized services",
  ],
  authors: [{ name: "Chainscore Labs", url: "https://chainscore.finance" }],
  creator: "Chainscore Labs",
  publisher: "Chainscore Labs",
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
    },
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://jamcode.fun",
    siteName: "JamCode.Fun",
    title: "JamCode.Fun - JAM Service Development IDE",
    description:
      "Build JAM services on Polkadot Join-Accumulate Machine. Browser IDE for Python, C, C++ development. Compile to PVM and simulate execution.",
    images: [
      {
        url: "https://jamcode.fun/og-image.svg",
        width: 1200,
        height: 630,
        alt: "JamCode.Fun - JAM Service Development IDE",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "JamCode.Fun - JAM Service Development IDE",
    description:
      "Build and deploy JAM services on Polkadot. Browser-based IDE for Python, C, C++ smart contract development.",
    images: ["https://jamcode.fun/og-image.svg"],
    creator: "@chainscore",
  },
  alternates: {
    canonical: "https://jamcode.fun",
  },
  category: "technology",
  classification: "Blockchain Development Tools",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
        {/* Structured Data for Rich Snippets */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebApplication",
              name: "JamCode.Fun",
              description:
                "Browser-based IDE for building JAM services on Polkadot Join-Accumulate Machine",
              url: "https://jamcode.fun",
              applicationCategory: "DeveloperApplication",
              operatingSystem: "Any",
              offers: {
                "@type": "Offer",
                price: "0",
                priceCurrency: "USD",
              },
              author: {
                "@type": "Organization",
                name: "Chainscore Labs",
                url: "https://chainscore.finance",
              },
              keywords:
                "JAM, Polkadot, Join Accumulate Machine, blockchain IDE, PVM, smart contracts",
            }),
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
