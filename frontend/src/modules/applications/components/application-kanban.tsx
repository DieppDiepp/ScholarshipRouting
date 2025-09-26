"use client";

import type React from "react";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/core/components/ui/dropdown-menu";
import { Progress } from "@/core/components/ui/progress";
import {
	AlertTriangle,
	Bell,
	Calendar,
	Edit,
	ExternalLink,
	FileText,
	MoreHorizontal,
	Upload,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface Application {
	id: string;
	scholarshipId: string;
	scholarshipTitle: string;
	provider: string;
	country: string;
	amount: string;
	deadline: string;
	status: string;
	progress: number;
	lastUpdated: string;
	documents: {
		required: string[];
		uploaded: string[];
		pending: string[];
	};
	timeline: Array<{
		date: string;
		action: string;
		type: string;
	}>;
	reminders: Array<{
		date: string;
		message: string;
	}>;
}

interface ApplicationKanbanProps {
	applications: Application[];
	onStatusChange: (appId: string, newStatus: string) => void;
}

const statusColumns = [
	{ id: "not-started", title: "Not Started", color: "bg-gray-100" },
	{ id: "in-progress", title: "In Progress", color: "bg-blue-100" },
	{ id: "submitted", title: "Submitted", color: "bg-yellow-100" },
	{ id: "interview", title: "Interview", color: "bg-purple-100" },
	{ id: "result", title: "Result", color: "bg-green-100" },
];

export function ApplicationKanban({
	applications,
	onStatusChange,
}: ApplicationKanbanProps) {
	const [draggedItem, setDraggedItem] = useState<string | null>(null);

	const getApplicationsByStatus = (status: string) => {
		return applications.filter((app) => app.status === status);
	};

	const getDaysUntilDeadline = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	};

	const handleDragStart = (e: React.DragEvent, appId: string) => {
		setDraggedItem(appId);
		e.dataTransfer.effectAllowed = "move";
	};

	const handleDragOver = (e: React.DragEvent) => {
		e.preventDefault();
		e.dataTransfer.dropEffect = "move";
	};

	const handleDrop = (e: React.DragEvent, newStatus: string) => {
		e.preventDefault();
		if (draggedItem) {
			onStatusChange(draggedItem, newStatus);
			setDraggedItem(null);
		}
	};

	const ApplicationCard = ({ application }: { application: Application }) => {
		const daysLeft = getDaysUntilDeadline(application.deadline);
		const isUrgent = daysLeft <= 30 && daysLeft > 0;
		const isExpired = daysLeft < 0;

		return (
			<Card
				className="mb-4 cursor-move hover:shadow-md transition-shadow"
				draggable
				onDragStart={(e) => handleDragStart(e, application.id)}
			>
				<CardHeader className="pb-3">
					<div className="flex justify-between items-start gap-2">
						<div className="flex-1">
							<CardTitle className="text-sm font-medium leading-tight mb-1">
								{application.scholarshipTitle}
							</CardTitle>
							<p className="text-xs text-muted-foreground">
								{application.provider}
							</p>
						</div>
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<Button variant="ghost" size="sm" className="h-6 w-6 p-0">
									<MoreHorizontal className="h-3 w-3" />
								</Button>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end">
								<DropdownMenuItem asChild>
									<Link href={`/applications/${application.id}`}>
										<Edit className="mr-2 h-4 w-4" />
										Edit Application
									</Link>
								</DropdownMenuItem>
								<DropdownMenuItem>
									<Upload className="mr-2 h-4 w-4" />
									Upload Documents
								</DropdownMenuItem>
								<DropdownMenuItem asChild>
									<Link href={`/scholarships/${application.scholarshipId}`}>
										<ExternalLink className="mr-2 h-4 w-4" />
										View Scholarship
									</Link>
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
					</div>
				</CardHeader>

				<CardContent className="space-y-3">
					{/* Progress */}
					<div className="space-y-1">
						<div className="flex justify-between text-xs">
							<span>Progress</span>
							<span className="font-medium">{application.progress}%</span>
						</div>
						<Progress value={application.progress} className="h-1.5" />
					</div>

					{/* Deadline */}
					<div className="flex items-center gap-2 text-xs">
						<Calendar className="h-3 w-3" />
						<span
							className={`${isUrgent ? "text-orange-600" : isExpired ? "text-red-600" : "text-muted-foreground"}`}
						>
							{new Date(application.deadline).toLocaleDateString()}
							{!isExpired && (
								<span className="ml-1">
									({daysLeft} day{daysLeft !== 1 ? "s" : ""} left)
								</span>
							)}
						</span>
						{isUrgent && <AlertTriangle className="h-3 w-3 text-orange-600" />}
						{isExpired && <AlertTriangle className="h-3 w-3 text-red-600" />}
					</div>

					{/* Documents Status */}
					<div className="flex items-center justify-between text-xs">
						<span className="flex items-center gap-1">
							<FileText className="h-3 w-3" />
							Documents
						</span>
						<span className="text-muted-foreground">
							{application.documents.uploaded.length}/
							{application.documents.required.length}
						</span>
					</div>

					{/* Amount */}
					<div className="text-xs text-muted-foreground">
						{application.amount}
					</div>

					{/* Reminders */}
					{application.reminders.length > 0 && (
						<div className="flex items-center gap-1 text-xs text-orange-600">
							<Bell className="h-3 w-3" />
							<span>
								{application.reminders.length} reminder
								{application.reminders.length !== 1 ? "s" : ""}
							</span>
						</div>
					)}

					{/* Last Updated */}
					<div className="text-xs text-muted-foreground">
						Updated {new Date(application.lastUpdated).toLocaleDateString()}
					</div>
				</CardContent>
			</Card>
		);
	};

	return (
		<div className="space-y-6">
			{/* Mobile: Stack columns vertically */}
			<div className="block lg:hidden space-y-6">
				{statusColumns.map((column) => {
					const columnApplications = getApplicationsByStatus(column.id);

					return (
						<div key={column.id} className="space-y-4">
							<div className={`${column.color} rounded-lg p-4`}>
								<div className="flex items-center justify-between">
									<h3 className="font-medium text-sm">{column.title}</h3>
									<Badge variant="secondary" className="text-xs">
										{columnApplications.length}
									</Badge>
								</div>
							</div>

							<div className="space-y-3">
								{columnApplications.map((application) => (
									<ApplicationCard
										key={application.id}
										application={application}
									/>
								))}

								{columnApplications.length === 0 && (
									<div className="text-center text-muted-foreground text-sm py-4 border-2 border-dashed border-muted rounded-lg">
										No applications
									</div>
								)}
							</div>
						</div>
					);
				})}
			</div>

			{/* Desktop: Grid layout */}
			<div className="hidden lg:grid lg:grid-cols-5 gap-6">
				{statusColumns.map((column) => {
					const columnApplications = getApplicationsByStatus(column.id);

					return (
						<div key={column.id} className="space-y-4">
							<div
								className={`${column.color} rounded-lg p-4`}
								onDragOver={handleDragOver}
								onDrop={(e) => handleDrop(e, column.id)}
							>
								<div className="flex items-center justify-between">
									<h3 className="font-medium text-sm">{column.title}</h3>
									<Badge variant="secondary" className="text-xs">
										{columnApplications.length}
									</Badge>
								</div>
							</div>

							<div
								className="min-h-96 space-y-4"
								onDragOver={handleDragOver}
								onDrop={(e) => handleDrop(e, column.id)}
							>
								{columnApplications.map((application) => (
									<ApplicationCard
										key={application.id}
										application={application}
									/>
								))}

								{columnApplications.length === 0 && (
									<div className="text-center text-muted-foreground text-sm py-8">
										No applications
									</div>
								)}
							</div>
						</div>
					);
				})}
			</div>
		</div>
	);
}
