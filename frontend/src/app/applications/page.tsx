"use client";

import { Button } from "@/core/components/ui/button";
import { Card, CardContent } from "@/core/components/ui/card";
import { Input } from "@/core/components/ui/input";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import { ApplicationKanban } from "@/modules/applications/components/application-kanban";
import { ApplicationStats } from "@/modules/applications/components/application-stats";
import { ApplicationTable } from "@/modules/applications/components/application-table";
import { Plus, Search } from "lucide-react";
import { useState } from "react";

// Mock application data
const mockApplications = [
	{
		id: "app1",
		scholarshipId: "s1",
		scholarshipTitle: "University of Oxford Graduate Scholarship",
		provider: "University of Oxford",
		country: "United Kingdom",
		amount: "Full tuition + £15,000 stipend",
		deadline: "2024-03-15",
		status: "in-progress",
		progress: 65,
		lastUpdated: "2024-01-15",
		documents: {
			required: ["CV", "Transcript", "Personal Statement", "Reference Letters"],
			uploaded: ["CV", "Transcript"],
			pending: ["Personal Statement", "Reference Letters"],
		},
		timeline: [
			{ date: "2024-01-10", action: "Application started", type: "info" },
			{ date: "2024-01-12", action: "CV uploaded", type: "success" },
			{ date: "2024-01-15", action: "Transcript uploaded", type: "success" },
		],
		reminders: [
			{ date: "2024-02-01", message: "Personal Statement due in 2 weeks" },
			{ date: "2024-02-15", message: "Reference letters due in 4 weeks" },
		],
	},
	{
		id: "app2",
		scholarshipId: "s2",
		scholarshipTitle: "MIT Graduate Fellowship",
		provider: "Massachusetts Institute of Technology",
		country: "United States",
		amount: "Full tuition + $40,000 stipend",
		deadline: "2024-02-01",
		status: "submitted",
		progress: 100,
		lastUpdated: "2024-01-20",
		documents: {
			required: ["CV", "Transcript", "Research Proposal", "Reference Letters"],
			uploaded: ["CV", "Transcript", "Research Proposal", "Reference Letters"],
			pending: [],
		},
		timeline: [
			{ date: "2024-01-05", action: "Application started", type: "info" },
			{ date: "2024-01-10", action: "All documents uploaded", type: "success" },
			{ date: "2024-01-20", action: "Application submitted", type: "success" },
		],
		reminders: [],
	},
	{
		id: "app3",
		scholarshipId: "s3",
		scholarshipTitle: "DAAD Study Scholarship",
		provider: "German Academic Exchange Service",
		country: "Germany",
		amount: "€850/month + tuition coverage",
		deadline: "2024-04-30",
		status: "not-started",
		progress: 0,
		lastUpdated: "2024-01-08",
		documents: {
			required: [
				"CV",
				"Transcript",
				"Motivation Letter",
				"Language Certificate",
			],
			uploaded: [],
			pending: [
				"CV",
				"Transcript",
				"Motivation Letter",
				"Language Certificate",
			],
		},
		timeline: [
			{ date: "2024-01-08", action: "Added to applications", type: "info" },
		],
		reminders: [
			{ date: "2024-02-01", message: "Start preparing application documents" },
		],
	},
	{
		id: "app4",
		scholarshipId: "s4",
		scholarshipTitle: "Cambridge Trust Scholarship",
		provider: "University of Cambridge",
		country: "United Kingdom",
		amount: "Full funding + living costs",
		deadline: "2024-01-31",
		status: "interview",
		progress: 90,
		lastUpdated: "2024-01-18",
		documents: {
			required: ["CV", "Transcript", "Research Proposal", "Reference Letters"],
			uploaded: ["CV", "Transcript", "Research Proposal", "Reference Letters"],
			pending: [],
		},
		timeline: [
			{ date: "2024-01-01", action: "Application submitted", type: "success" },
			{
				date: "2024-01-18",
				action: "Interview invitation received",
				type: "success",
			},
		],
		reminders: [
			{ date: "2024-01-25", message: "Interview scheduled for January 30th" },
		],
	},
	{
		id: "app5",
		scholarshipId: "s5",
		scholarshipTitle: "Fulbright Scholarship",
		provider: "Fulbright Commission",
		country: "United States",
		amount: "Full funding + research support",
		deadline: "2024-01-15",
		status: "result",
		progress: 100,
		lastUpdated: "2024-01-22",
		documents: {
			required: ["CV", "Transcript", "Project Proposal", "Reference Letters"],
			uploaded: ["CV", "Transcript", "Project Proposal", "Reference Letters"],
			pending: [],
		},
		timeline: [
			{ date: "2023-12-01", action: "Application submitted", type: "success" },
			{ date: "2024-01-10", action: "Interview completed", type: "success" },
			{ date: "2024-01-22", action: "Acceptance received", type: "success" },
		],
		reminders: [],
	},
];

export default function ApplicationsPage() {
	const [applications, setApplications] = useState(mockApplications);
	const [viewMode, setViewMode] = useState<"kanban" | "table">("kanban");
	const [searchQuery, setSearchQuery] = useState("");
	const [statusFilter, setStatusFilter] = useState("all");
	const [sortBy, setSortBy] = useState("deadline");

	const filteredApplications = applications.filter((app) => {
		const matchesSearch =
			searchQuery === "" ||
			app.scholarshipTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
			app.provider.toLowerCase().includes(searchQuery.toLowerCase()) ||
			app.country.toLowerCase().includes(searchQuery.toLowerCase());

		const matchesStatus = statusFilter === "all" || app.status === statusFilter;

		return matchesSearch && matchesStatus;
	});

	const sortedApplications = [...filteredApplications].sort((a, b) => {
		switch (sortBy) {
			case "deadline":
				return new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
			case "progress":
				return b.progress - a.progress;
			case "updated":
				return (
					new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
				);
			default:
				return 0;
		}
	});

	const updateApplicationStatus = (appId: string, newStatus: string) => {
		setApplications((prev) =>
			prev.map((app) =>
				app.id === appId
					? {
							...app,
							status: newStatus,
							lastUpdated: new Date().toISOString().split("T")[0],
							timeline: [
								...app.timeline,
								{
									date: new Date().toISOString().split("T")[0],
									action: `Status changed to ${newStatus}`,
									type: "info",
								},
							],
						}
					: app,
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
							<h1 className="text-3xl font-bold mb-2">My Applications</h1>
							<p className="text-muted-foreground">
								Track and manage your scholarship applications
							</p>
						</div>
						<Button className="w-fit">
							<Plus className="mr-2 h-4 w-4" />
							Add New Application
						</Button>
					</div>

					{/* Stats Overview */}
					<ApplicationStats applications={applications} />
				</div>

				{/* Controls */}
				<Card className="mb-6">
					<CardContent className="p-6">
						<div className="flex flex-col lg:flex-row gap-4">
							{/* Search */}
							<div className="flex-1 relative">
								<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
								<Input
									placeholder="Search applications..."
									value={searchQuery}
									onChange={(e) => setSearchQuery(e.target.value)}
									className="pl-10"
								/>
							</div>

							{/* Filters */}
							<div className="flex gap-2">
								<Select value={statusFilter} onValueChange={setStatusFilter}>
									<SelectTrigger className="w-40">
										<SelectValue placeholder="Status" />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="all">All Status</SelectItem>
										<SelectItem value="not-started">Not Started</SelectItem>
										<SelectItem value="in-progress">In Progress</SelectItem>
										<SelectItem value="submitted">Submitted</SelectItem>
										<SelectItem value="interview">Interview</SelectItem>
										<SelectItem value="result">Result</SelectItem>
									</SelectContent>
								</Select>

								<Select value={sortBy} onValueChange={setSortBy}>
									<SelectTrigger className="w-40">
										<SelectValue placeholder="Sort by" />
									</SelectTrigger>
									<SelectContent>
										<SelectItem value="deadline">Deadline</SelectItem>
										<SelectItem value="progress">Progress</SelectItem>
										<SelectItem value="updated">Last Updated</SelectItem>
									</SelectContent>
								</Select>

								<Button
									variant={viewMode === "kanban" ? "default" : "outline"}
									onClick={() => setViewMode("kanban")}
									size="sm"
								>
									Kanban
								</Button>
								<Button
									variant={viewMode === "table" ? "default" : "outline"}
									onClick={() => setViewMode("table")}
									size="sm"
								>
									Table
								</Button>
							</div>
						</div>
					</CardContent>
				</Card>

				{/* Main Content */}
				{viewMode === "kanban" ? (
					<ApplicationKanban
						applications={sortedApplications}
						onStatusChange={updateApplicationStatus}
					/>
				) : (
					<ApplicationTable
						applications={sortedApplications}
						onStatusChange={updateApplicationStatus}
					/>
				)}
			</div>
		</div>
	);
}
