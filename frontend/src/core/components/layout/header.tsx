"use client";

import {
	Avatar,
	AvatarFallback,
	AvatarImage,
} from "@/core/components/ui/avatar";
import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuLabel,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
} from "@/core/components/ui/dropdown-menu";
import { ThemeToggle } from "@/core/components/ui/themeToggle";
import {
	Bell,
	Calendar,
	FileText,
	GraduationCap,
	Menu,
	Search,
	Settings,
	User,
	X,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

const navigationItems = [
	{ href: "/scholarships", label: "Scholarships", icon: Search },
	{ href: "/applications", label: "My Applications", icon: FileText },
	{ href: "/calendar", label: "Deadlines", icon: Calendar },
	{ href: "/profile", label: "Profile", icon: User },
];

export function Header() {
	const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

	const closeMobileMenu = () => setIsMobileMenuOpen(false);
	const toggleMobileMenu = () => setIsMobileMenuOpen((prev) => !prev);

	return (
		<header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
			<div className="w-full flex h-16 items-center justify-between px-4 sm:px-6">
				{/* Logo */}
				<Link href="/" className="flex items-center space-x-2">
					<div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
						<GraduationCap className="h-5 w-5 text-primary-foreground" />
					</div>
					<span className="text-lg font-bold">ScholarSearch</span>
				</Link>

				{/* Desktop Navigation */}
				<nav className="hidden md:flex items-center space-x-6 lg:space-x-8">
					{navigationItems.map((item) => (
						<Link
							key={item.href}
							href={item.href}
							className="flex items-center space-x-2 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground whitespace-nowrap"
						>
							<item.icon className="h-4 w-4" />
							<span>{item.label}</span>
						</Link>
					))}
				</nav>

				{/* Actions */}
				<div className="flex items-center gap-2 sm:gap-4">
					<ThemeToggle />
					<DropdownMenu>
						<DropdownMenuTrigger className="relative w-8 h-8">
							<Bell className="h-4 w-4" />
							<Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-1 text-xs">
								3
							</Badge>
						</DropdownMenuTrigger>
						<DropdownMenuContent
							className="w-56 z-[9999]"
							align="end"
							forceMount
						>
							<DropdownMenuLabel className="font-normal">
								<div className="flex flex-col space-y-1">
									<p className="text-sm font-medium leading-none">John Doe</p>
									<p className="text-xs leading-none text-muted-foreground">
										john.doe@example.com
									</p>
								</div>
							</DropdownMenuLabel>
							<DropdownMenuSeparator />
							<DropdownMenuItem asChild>
								<Link href="/profile" className="flex items-center">
									<User className="mr-2 h-4 w-4" />
									<span>Profile</span>
								</Link>
							</DropdownMenuItem>
							<DropdownMenuItem asChild>
								<Link href="/settings" className="flex items-center">
									<Settings className="mr-2 h-4 w-4" />
									<span>Settings</span>
								</Link>
							</DropdownMenuItem>
							<DropdownMenuSeparator />
							<DropdownMenuItem>Log out</DropdownMenuItem>
						</DropdownMenuContent>
					</DropdownMenu>

					<DropdownMenu>
						<DropdownMenuTrigger className="p-0">
							<Avatar className="h-8 w-8">
								<AvatarImage src="/diverse-user-avatars.png" alt="User" />
								<AvatarFallback>JD</AvatarFallback>
							</Avatar>
						</DropdownMenuTrigger>
						<DropdownMenuContent
							className="w-56 z-[9999]"
							align="end"
							forceMount
						>
							<DropdownMenuLabel className="font-normal">
								<div className="flex flex-col space-y-1">
									<p className="text-sm font-medium leading-none">John Doe</p>
									<p className="text-xs leading-none text-muted-foreground">
										john.doe@example.com
									</p>
								</div>
							</DropdownMenuLabel>
							<DropdownMenuSeparator />
							<DropdownMenuItem asChild>
								<Link href="/profile" className="flex items-center">
									<User className="mr-2 h-4 w-4" />
									<span>Profile</span>
								</Link>
							</DropdownMenuItem>
							<DropdownMenuItem asChild>
								<Link href="/settings" className="flex items-center">
									<Settings className="mr-2 h-4 w-4" />
									<span>Settings</span>
								</Link>
							</DropdownMenuItem>
							<DropdownMenuSeparator />
							<DropdownMenuItem>Log out</DropdownMenuItem>
						</DropdownMenuContent>
					</DropdownMenu>

					{/* Mobile Menu Button */}
					<Button
						variant="ghost"
						size="icon"
						className="md:hidden"
						onClick={toggleMobileMenu}
					>
						{isMobileMenuOpen ? (
							<X className="h-5 w-5" />
						) : (
							<Menu className="h-5 w-5" />
						)}
					</Button>
				</div>
			</div>

			{/* Mobile Navigation */}
			{isMobileMenuOpen && (
				<div className="md:hidden border-t bg-background shadow-sm">
					<nav className="container px-4 py-4 space-y-2">
						{navigationItems.map((item) => (
							<Link
								key={item.href}
								href={item.href}
								className="flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
								onClick={closeMobileMenu}
							>
								<item.icon className="h-4 w-4" />
								<span>{item.label}</span>
							</Link>
						))}
					</nav>
				</div>
			)}

			{/* Optional overlay for mobile menu (comment back in if you’d like) */}
			{/* {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/70 backdrop-blur-sm md:hidden"
          onClick={closeMobileMenu}
        />
      )} */}
		</header>
	);
}
