"use client";

import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Progress } from "@/core/components/ui/progress";
import {
	AlertTriangle,
	CheckCircle,
	Clock,
	FileText,
	TrendingUp,
} from "lucide-react";

interface Application {
	id: string;
	status: string;
	progress: number;
	deadline: string;
	documents: {
		required: string[];
		uploaded: string[];
		pending: string[];
	};
	reminders: Array<{
		date: string;
		message: string;
	}>;
}

interface ApplicationStatsProps {
	applications: Application[];
}

export function ApplicationStats({ applications }: ApplicationStatsProps) {
	const totalApplications = applications.length;
	const completedApplications = applications.filter(
		(app) =>
			app.status === "submitted" ||
			app.status === "interview" ||
			app.status === "result",
	).length;
	const inProgressApplications = applications.filter(
		(app) => app.status === "in-progress",
	).length;
	const notStartedApplications = applications.filter(
		(app) => app.status === "not-started",
	).length;

	const averageProgress =
		totalApplications > 0
			? Math.round(
					applications.reduce((sum, app) => sum + app.progress, 0) /
						totalApplications,
				)
			: 0;

	const urgentDeadlines = applications.filter((app) => {
		const daysLeft = Math.ceil(
			(new Date(app.deadline).getTime() - new Date().getTime()) /
				(1000 * 60 * 60 * 24),
		);
		return daysLeft <= 30 && daysLeft > 0;
	}).length;

	const totalReminders = applications.reduce(
		(sum, app) => sum + app.reminders.length,
		0,
	);

	const stats = [
		{
			title: "Total Applications",
			value: totalApplications,
			icon: FileText,
			color: "text-blue-600",
			bgColor: "bg-blue-100",
		},
		{
			title: "In Progress",
			value: inProgressApplications,
			icon: Clock,
			color: "text-orange-600",
			bgColor: "bg-orange-100",
		},
		{
			title: "Completed",
			value: completedApplications,
			icon: CheckCircle,
			color: "text-green-600",
			bgColor: "bg-green-100",
		},
		{
			title: "Urgent Deadlines",
			value: urgentDeadlines,
			icon: AlertTriangle,
			color: "text-red-600",
			bgColor: "bg-red-100",
		},
	];

	return (
		<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
			{stats.map((stat) => (
				<Card key={stat.title}>
					<CardContent className="p-4">
						<div className="flex items-center justify-between">
							<div>
								<p className="text-sm text-muted-foreground">{stat.title}</p>
								<p className="text-2xl font-bold">{stat.value}</p>
							</div>
							<div className={`p-2 rounded-lg ${stat.bgColor}`}>
								<stat.icon className={`h-5 w-5 ${stat.color}`} />
							</div>
						</div>
					</CardContent>
				</Card>
			))}

			{/* Average Progress Card */}
			<Card className="md:col-span-2 lg:col-span-2">
				<CardHeader className="pb-3">
					<CardTitle className="text-sm font-medium flex items-center gap-2">
						<TrendingUp className="h-4 w-4" />
						Overall Progress
					</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="space-y-2">
						<div className="flex justify-between text-sm">
							<span>Average Completion</span>
							<span className="font-medium">{averageProgress}%</span>
						</div>
						<Progress value={averageProgress} className="h-2" />
						<div className="flex justify-between text-xs text-muted-foreground">
							<span>{notStartedApplications} not started</span>
							<span>{totalReminders} active reminders</span>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
