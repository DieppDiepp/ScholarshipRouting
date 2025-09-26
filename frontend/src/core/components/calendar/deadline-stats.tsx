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
	Calendar,
	CheckCircle,
	Clock,
	TrendingUp,
} from "lucide-react";

interface DeadlineStatsProps {
	deadlines: any[];
}

export function DeadlineStats({ deadlines }: DeadlineStatsProps) {
	const totalDeadlines = deadlines.length;
	const urgentDeadlines = deadlines.filter(
		(d) => d.daysLeft <= 7 && d.daysLeft > 0,
	).length;
	const overdueDeadlines = deadlines.filter((d) => d.daysLeft <= 0).length;
	const upcomingDeadlines = deadlines.filter(
		(d) => d.daysLeft > 7 && d.daysLeft <= 30,
	).length;
	const completedDeadlines = deadlines.filter(
		(d) => d.status === "completed",
	).length;

	const completionRate =
		totalDeadlines > 0
			? Math.round((completedDeadlines / totalDeadlines) * 100)
			: 0;

	const stats = [
		{
			title: "Total Deadlines",
			value: totalDeadlines,
			icon: Calendar,
			color: "text-blue-600",
			bgColor: "bg-blue-100",
		},
		{
			title: "Urgent (≤7 days)",
			value: urgentDeadlines,
			icon: AlertTriangle,
			color: "text-red-600",
			bgColor: "bg-red-100",
		},
		{
			title: "Upcoming (≤30 days)",
			value: upcomingDeadlines,
			icon: Clock,
			color: "text-orange-600",
			bgColor: "bg-orange-100",
		},
		{
			title: "Completed",
			value: completedDeadlines,
			icon: CheckCircle,
			color: "text-green-600",
			bgColor: "bg-green-100",
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

			{/* Completion Rate Card */}
			<Card className="md:col-span-2 lg:col-span-2">
				<CardHeader className="pb-3">
					<CardTitle className="text-sm font-medium flex items-center gap-2">
						<TrendingUp className="h-4 w-4" />
						Completion Progress
					</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="space-y-2">
						<div className="flex justify-between text-sm">
							<span>Overall Completion Rate</span>
							<span className="font-medium">{completionRate}%</span>
						</div>
						<Progress value={completionRate} className="h-2" />
						<div className="flex justify-between text-xs text-muted-foreground">
							<span>{overdueDeadlines} overdue</span>
							<span>{urgentDeadlines + upcomingDeadlines} pending</span>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
