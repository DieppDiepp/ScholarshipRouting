"use client";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/core/components/ui/dialog";
import { getDaysInMonth, getFirstDayOfMonth } from "@/core/lib/date";
import {
	AlertTriangle,
	Calendar,
	CheckCircle,
	ChevronLeft,
	ChevronRight,
	Clock,
} from "lucide-react";
import { useState } from "react";

interface CalendarViewProps {
	deadlines: any[];
	selectedMonth: number;
	selectedYear: number;
	onMonthChange: (month: number) => void;
	onYearChange: (year: number) => void;
	onStatusChange: (deadlineId: string, newStatus: string) => void;
}

const monthNames = [
	"January",
	"February",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December",
];

export function CalendarView({
	deadlines,
	selectedMonth,
	selectedYear,
	onMonthChange,
	onYearChange,
	onStatusChange,
}: CalendarViewProps) {
	const [selectedDate, setSelectedDate] = useState<Date | null>(null);

	const getDeadlinesForDate = (date: Date) => {
		return deadlines.filter((deadline) => {
			const deadlineDate = new Date(deadline.date);
			return deadlineDate.toDateString() === date.toDateString();
		});
	};

	const navigateMonth = (direction: "prev" | "next") => {
		if (direction === "prev") {
			if (selectedMonth === 0) {
				onMonthChange(11);
				onYearChange(selectedYear - 1);
			} else {
				onMonthChange(selectedMonth - 1);
			}
		} else {
			if (selectedMonth === 11) {
				onMonthChange(0);
				onYearChange(selectedYear + 1);
			} else {
				onMonthChange(selectedMonth + 1);
			}
		}
	};

	const renderCalendarDays = () => {
		const daysInMonth = getDaysInMonth(selectedMonth, selectedYear);
		const firstDay = getFirstDayOfMonth(selectedMonth, selectedYear);
		const days = [];

		// Empty cells for days before the first day of the month
		for (let i = 0; i < firstDay; i++) {
			days.push(
				<div key={`empty-${i}`} className="h-24 border border-muted" />,
			);
		}

		// Days of the month
		for (let day = 1; day <= daysInMonth; day++) {
			const date = new Date(selectedYear, selectedMonth, day);
			const dayDeadlines = getDeadlinesForDate(date);
			const isToday = date.toDateString() === new Date().toDateString();

			days.push(
				<div
					key={day}
					className={`h-24 border border-muted p-1 cursor-pointer hover:bg-muted/50 ${
						isToday ? "bg-primary/10 border-primary" : ""
					}`}
					onClick={() => setSelectedDate(date)}
				>
					<div
						className={`text-sm font-medium mb-1 ${isToday ? "text-primary" : ""}`}
					>
						{day}
					</div>
					<div className="space-y-1">
						{dayDeadlines.slice(0, 2).map((deadline) => (
							<div
								key={deadline.id}
								className={`text-xs p-1 rounded truncate ${
									deadline.priority === "critical"
										? "bg-red-100 text-red-800"
										: deadline.priority === "high"
											? "bg-orange-100 text-orange-800"
											: "bg-blue-100 text-blue-800"
								}`}
							>
								{deadline.title}
							</div>
						))}
						{dayDeadlines.length > 2 && (
							<div className="text-xs text-muted-foreground">
								+{dayDeadlines.length - 2} more
							</div>
						)}
					</div>
				</div>,
			);
		}

		return days;
	};

	const getDeadlineIcon = (type: string) => {
		switch (type) {
			case "application":
				return <Calendar className="h-4 w-4" />;
			case "interview":
				return <Clock className="h-4 w-4" />;
			case "task":
				return <CheckCircle className="h-4 w-4" />;
			case "result":
				return <AlertTriangle className="h-4 w-4" />;
			default:
				return <Calendar className="h-4 w-4" />;
		}
	};

	const getPriorityColor = (priority: string) => {
		switch (priority) {
			case "critical":
				return "text-red-600 bg-red-100";
			case "high":
				return "text-orange-600 bg-orange-100";
			case "medium":
				return "text-blue-600 bg-blue-100";
			case "low":
				return "text-green-600 bg-green-100";
			default:
				return "text-muted-foreground bg-muted";
		}
	};

	return (
		<div className="space-y-6">
			{/* Calendar Header */}
			<Card>
				<CardHeader>
					<div className="flex items-center justify-between">
						<CardTitle className="text-xl">
							{monthNames[selectedMonth]} {selectedYear}
						</CardTitle>
						<div className="flex items-center gap-2">
							<Button
								variant="outline"
								size="sm"
								onClick={() => navigateMonth("prev")}
							>
								<ChevronLeft className="h-4 w-4" />
							</Button>
							<Button
								variant="outline"
								size="sm"
								onClick={() => navigateMonth("next")}
							>
								<ChevronRight className="h-4 w-4" />
							</Button>
							<Button
								variant="outline"
								size="sm"
								onClick={() => {
									const today = new Date();
									onMonthChange(today.getMonth());
									onYearChange(today.getFullYear());
								}}
							>
								Today
							</Button>
						</div>
					</div>
				</CardHeader>
			</Card>

			{/* Calendar Grid */}
			<Card>
				<CardContent className="p-0">
					{/* Day Headers */}
					<div className="grid grid-cols-7 border-b">
						{["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
							<div
								key={day}
								className="p-3 text-center font-medium text-sm bg-muted"
							>
								{day}
							</div>
						))}
					</div>

					{/* Calendar Days */}
					<div className="grid grid-cols-7">{renderCalendarDays()}</div>
				</CardContent>
			</Card>

			{/* Date Detail Dialog */}
			{selectedDate && (
				<Dialog
					open={!!selectedDate}
					onOpenChange={() => setSelectedDate(null)}
				>
					<DialogContent className="max-w-2xl">
						<DialogHeader>
							<DialogTitle>
								Deadlines for {selectedDate.toLocaleDateString()}
							</DialogTitle>
							<DialogDescription>
								All deadlines and events scheduled for this date
							</DialogDescription>
						</DialogHeader>
						<div className="space-y-4 max-h-96 overflow-y-auto">
							{getDeadlinesForDate(selectedDate).length === 0 ? (
								<div className="text-center py-8 text-muted-foreground">
									No deadlines scheduled for this date
								</div>
							) : (
								getDeadlinesForDate(selectedDate).map((deadline) => (
									<Card key={deadline.id}>
										<CardContent className="p-4">
											<div className="flex items-start justify-between">
												<div className="flex items-start gap-3">
													<div
														className={`p-2 rounded-lg ${getPriorityColor(deadline.priority)}`}
													>
														{getDeadlineIcon(deadline.type)}
													</div>
													<div className="flex-1">
														<h3 className="font-medium">{deadline.title}</h3>
														<p className="text-sm text-muted-foreground mb-2">
															{deadline.description}
														</p>
														<div className="flex items-center gap-2 text-xs text-muted-foreground">
															<span>{deadline.provider}</span>
															<span>•</span>
															<span>{deadline.time}</span>
															<span>•</span>
															<span>{deadline.daysLeft} days left</span>
														</div>
													</div>
												</div>
												<div className="flex flex-col items-end gap-2">
													<Badge variant="outline" className="text-xs">
														{deadline.category}
													</Badge>
													<Badge
														className={`text-xs border-0 ${getPriorityColor(deadline.priority)}`}
													>
														{deadline.priority}
													</Badge>
												</div>
											</div>
										</CardContent>
									</Card>
								))
							)}
						</div>
					</DialogContent>
				</Dialog>
			)}
		</div>
	);
}
