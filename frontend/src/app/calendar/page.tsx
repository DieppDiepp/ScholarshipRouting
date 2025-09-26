"use client";

import { CalendarView } from "@/core/components/calendar/calendar-view";
import { DeadlineList } from "@/core/components/calendar/deadline-list";
import { DeadlineStats } from "@/core/components/calendar/deadline-stats";
import { UpcomingDeadlines } from "@/core/components/calendar/upcoming-deadlines";
import { Button } from "@/core/components/ui/button";
import { Card, CardContent } from "@/core/components/ui/card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import { Calendar, Filter, List, Plus } from "lucide-react";
import { useState } from "react";

// Mock deadline data combining scholarships and applications
const mockDeadlines = [
	{
		id: "d1",
		title: "University of Oxford Graduate Scholarship",
		type: "application",
		date: "2024-03-15",
		time: "23:59",
		status: "pending",
		priority: "high",
		description: "Final application deadline",
		applicationId: "app1",
		scholarshipId: "s1",
		daysLeft: 45,
		category: "Application Deadline",
		provider: "University of Oxford",
		amount: "Full tuition + £15,000 stipend",
	},
	{
		id: "d2",
		title: "MIT Graduate Fellowship",
		type: "application",
		date: "2024-02-01",
		time: "17:00",
		status: "urgent",
		priority: "critical",
		description: "Application submission deadline",
		applicationId: "app2",
		scholarshipId: "s2",
		daysLeft: 12,
		category: "Application Deadline",
		provider: "MIT",
		amount: "Full tuition + $40,000 stipend",
	},
	{
		id: "d3",
		title: "Personal Statement - Oxford",
		type: "task",
		date: "2024-02-15",
		time: "12:00",
		status: "pending",
		priority: "medium",
		description: "Complete personal statement for Oxford application",
		applicationId: "app1",
		scholarshipId: "s1",
		daysLeft: 26,
		category: "Document Deadline",
		provider: "University of Oxford",
	},
	{
		id: "d4",
		title: "Reference Letters - Cambridge",
		type: "task",
		date: "2024-02-20",
		time: "15:00",
		status: "pending",
		priority: "medium",
		description: "Collect reference letters from professors",
		applicationId: "app4",
		scholarshipId: "s4",
		daysLeft: 31,
		category: "Document Deadline",
		provider: "University of Cambridge",
	},
	{
		id: "d5",
		title: "DAAD Study Scholarship",
		type: "application",
		date: "2024-04-30",
		time: "23:59",
		status: "future",
		priority: "medium",
		description: "Application deadline for DAAD scholarship",
		applicationId: "app3",
		scholarshipId: "s3",
		daysLeft: 90,
		category: "Application Deadline",
		provider: "DAAD",
		amount: "€850/month + tuition coverage",
	},
	{
		id: "d6",
		title: "Cambridge Interview",
		type: "interview",
		date: "2024-01-30",
		time: "14:00",
		status: "upcoming",
		priority: "critical",
		description: "Virtual interview for Cambridge Trust Scholarship",
		applicationId: "app4",
		scholarshipId: "s4",
		daysLeft: 5,
		category: "Interview",
		provider: "University of Cambridge",
	},
	{
		id: "d7",
		title: "Language Certificate Upload",
		type: "task",
		date: "2024-03-01",
		time: "18:00",
		status: "pending",
		priority: "low",
		description: "Upload IELTS certificate for DAAD application",
		applicationId: "app3",
		scholarshipId: "s3",
		daysLeft: 31,
		category: "Document Deadline",
		provider: "DAAD",
	},
	{
		id: "d8",
		title: "Fulbright Result Notification",
		type: "result",
		date: "2024-02-10",
		time: "09:00",
		status: "waiting",
		priority: "high",
		description: "Expected result notification date",
		applicationId: "app5",
		scholarshipId: "s5",
		daysLeft: 21,
		category: "Result",
		provider: "Fulbright Commission",
	},
];

export default function CalendarPage() {
	const [deadlines, setDeadlines] = useState(mockDeadlines);
	const [viewMode, setViewMode] = useState<"calendar" | "list">("calendar");
	const [filterType, setFilterType] = useState("all");
	const [filterStatus, setFilterStatus] = useState("all");
	const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
	const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

	const filteredDeadlines = deadlines.filter((deadline) => {
		const matchesType = filterType === "all" || deadline.type === filterType;
		const matchesStatus =
			filterStatus === "all" || deadline.status === filterStatus;
		return matchesType && matchesStatus;
	});

	const sortedDeadlines = [...filteredDeadlines].sort((a, b) => {
		return new Date(a.date).getTime() - new Date(b.date).getTime();
	});

	const updateDeadlineStatus = (deadlineId: string, newStatus: string) => {
		setDeadlines((prev) =>
			prev.map((deadline) =>
				deadline.id === deadlineId
					? { ...deadline, status: newStatus }
					: deadline,
			),
		);
	};

	return (
		<div className="min-h-screen bg-background">
			<div className="container mx-auto max-w-7xl px-4 py-8">
				{/* Header */}
				<div className="mb-8">
					<div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
						<div>
							<h1 className="text-3xl font-bold mb-2">Deadline Tracker</h1>
							<p className="text-muted-foreground">
								Stay on top of all your scholarship deadlines and important
								dates
							</p>
						</div>
						<Button>
							<Plus className="mr-2 h-4 w-4" />
							Add Custom Deadline
						</Button>
					</div>

					{/* Stats Overview */}
					<DeadlineStats deadlines={deadlines} />
				</div>

				<div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
					{/* Sidebar - Upcoming Deadlines */}
					<div className="lg:col-span-1">
						<UpcomingDeadlines deadlines={sortedDeadlines.slice(0, 8)} />
					</div>

					{/* Main Content */}
					<div className="lg:col-span-3 space-y-6">
						{/* Controls */}
						<Card>
							<CardContent className="p-6">
								<div className="flex flex-col lg:flex-row gap-4">
									{/* View Toggle */}
									<div className="flex gap-2">
										<Button
											variant={viewMode === "calendar" ? "default" : "outline"}
											onClick={() => setViewMode("calendar")}
											size="sm"
										>
											<Calendar className="mr-2 h-4 w-4" />
											Calendar
										</Button>
										<Button
											variant={viewMode === "list" ? "default" : "outline"}
											onClick={() => setViewMode("list")}
											size="sm"
										>
											<List className="mr-2 h-4 w-4" />
											List
										</Button>
									</div>

									{/* Filters */}
									<div className="flex gap-2 flex-1">
										<Select value={filterType} onValueChange={setFilterType}>
											<SelectTrigger className="w-40">
												<SelectValue placeholder="Type" />
											</SelectTrigger>
											<SelectContent>
												<SelectItem value="all">All Types</SelectItem>
												<SelectItem value="application">
													Applications
												</SelectItem>
												<SelectItem value="task">Tasks</SelectItem>
												<SelectItem value="interview">Interviews</SelectItem>
												<SelectItem value="result">Results</SelectItem>
											</SelectContent>
										</Select>

										<Select
											value={filterStatus}
											onValueChange={setFilterStatus}
										>
											<SelectTrigger className="w-40">
												<SelectValue placeholder="Status" />
											</SelectTrigger>
											<SelectContent>
												<SelectItem value="all">All Status</SelectItem>
												<SelectItem value="urgent">Urgent</SelectItem>
												<SelectItem value="upcoming">Upcoming</SelectItem>
												<SelectItem value="pending">Pending</SelectItem>
												<SelectItem value="completed">Completed</SelectItem>
											</SelectContent>
										</Select>

										<Button variant="outline" size="sm">
											<Filter className="mr-2 h-4 w-4" />
											More Filters
										</Button>
									</div>
								</div>
							</CardContent>
						</Card>

						{/* Main View */}
						{viewMode === "calendar" ? (
							<CalendarView
								deadlines={filteredDeadlines}
								selectedMonth={selectedMonth}
								selectedYear={selectedYear}
								onMonthChange={setSelectedMonth}
								onYearChange={setSelectedYear}
								onStatusChange={updateDeadlineStatus}
							/>
						) : (
							<DeadlineList
								deadlines={sortedDeadlines}
								onStatusChange={updateDeadlineStatus}
							/>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}
