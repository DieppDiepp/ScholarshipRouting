"use client";

import { Button } from "@/core/components/ui/button";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";

export function ThemeToggle() {
	const [theme, setTheme] = useState<"light" | "dark">("light");

	useEffect(() => {
		const storedTheme = localStorage.getItem("theme") || "light";
		setTheme(storedTheme as "light" | "dark");
		document.documentElement.className = storedTheme;
	}, []);

	const toggleTheme = () => {
		const newTheme = theme === "light" ? "dark" : "light";
		setTheme(newTheme);
		localStorage.setItem("theme", newTheme);
		document.documentElement.className = newTheme;
	};

	return (
		<Button
			variant="ghost"
			size="sm"
			onClick={toggleTheme}
			className="flex items-center"
		>
			{theme === "light" ? (
				<Moon className="h-5 w-5" />
			) : (
				<Sun className="h-5 w-5" />
			)}
		</Button>
	);
}
