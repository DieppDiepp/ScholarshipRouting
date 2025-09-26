import { Header } from "@/core/components/layout/header";
import { Analytics } from "@vercel/analytics/next";
import { GeistMono } from "geist/font/mono";
import { GeistSans } from "geist/font/sans";
import type { Metadata } from "next";
import type React from "react";
import { Suspense } from "react";
import "./globals.css";

export const metadata: Metadata = {
	title: "ScholarSearch - Graduate Study Abroad Scholarship Platform",
	description:
		"Find and apply for graduate study abroad scholarships with AI-powered matching and application assistance",
	generator: "v0.app",
};

export default function RootLayout({
	children,
}: Readonly<{
	children: React.ReactNode;
}>) {
	return (
		<html lang="en">
			<body className={`font-sans ${GeistSans.variable} ${GeistMono.variable}`}>
				<div className="min-h-screen bg-background">
					<Suspense fallback={<div>Loading...</div>}>
						<Header />
						<main className="flex-1">{children}</main>
					</Suspense>
				</div>
				<Analytics />
			</body>
		</html>
	);
}
