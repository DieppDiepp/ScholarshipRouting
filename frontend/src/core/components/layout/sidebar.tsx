"use client";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import { cn } from "@/core/lib/utils";
import {
	BarChart3,
	BookOpen,
	Calendar,
	FileText,
	Search,
	Settings,
	Target,
	User,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const sidebarItems = [
	{
		title: "Discovery",
		items: [
			{
				title: "Search Scholarships",
				href: "/scholarships",
				icon: Search,
				badge: "New",
			},
			{
				title: "Saved Scholarships",
				href: "/scholarships/saved",
				icon: BookOpen,
			},
		],
	},
	{
		title: "Applications",
		items: [
			{
				title: "My Applications",
				href: "/applications",
				icon: FileText,
				badge: "5",
			},
			{
				title: "Application Assistant",
				href: "/applications/assistant",
				icon: Target,
			},
			{
				title: "Deadlines",
				href: "/calendar",
				icon: Calendar,
				badge: "3",
			},
		],
	},
	{
		title: "Profile",
		items: [
			{
				title: "My Profile",
				href: "/profile",
				icon: User,
			},
			{
				title: "Progress Tracker",
				href: "/progress",
				icon: BarChart3,
			},
			{
				title: "Settings",
				href: "/settings",
				icon: Settings,
			},
		],
	},
];

interface SidebarProps {
	className?: string;
}

export function Sidebar({ className }: SidebarProps) {
	const pathname = usePathname();

	return (
		<div className={cn("pb-12 w-64", className)}>
			<div className="space-y-4 py-4">
				{sidebarItems.map((section) => (
					<div key={section.title} className="px-3 py-2">
						<h2 className="mb-2 px-4 text-lg font-semibold tracking-tight">
							{section.title}
						</h2>
						<div className="space-y-1">
							{section.items.map((item) => (
								<Button
									key={item.href}
									variant={pathname === item.href ? "secondary" : "ghost"}
									className="w-full justify-start"
									asChild
								>
									<Link href={item.href}>
										<item.icon className="mr-2 h-4 w-4" />
										{item.title}
										{item.badge && (
											<Badge variant="secondary" className="ml-auto">
												{item.badge}
											</Badge>
										)}
									</Link>
								</Button>
							))}
						</div>
					</div>
				))}
			</div>
		</div>
	);
}
