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
	AlertTriangle,
	Bell,
	Calendar,
	CheckCircle,
	Clock,
	ExternalLink,
} from "lucide-react";
import Link from "next/link";

interface UpcomingDeadlinesProps {
	deadlines: any[];
}

export function UpcomingDeadlines({ deadlines }: UpcomingDeadlinesProps) {
	const getDeadlineIcon = (type: string) => {
		switch (type) {
			case "application":
				return <Calendar className="h-4 w-4 text-blue-600" />;
			case "interview":
				return <Clock className="h-4 w-4 text-purple-600" />;
			case "task":
				return <CheckCircle className="h-4 w-4 text-green-600" />;
			case "result":
				return <AlertTriangle className="h-4 w-4 text-orange-600" />;
			default:
				return <Calendar className="h-4 w-4 text-muted-foreground" />;
		}
	};

	const getPriorityColor = (priority: string, daysLeft: number) => {
		if (daysLeft <= 0) return "text-red-600";
		if (daysLeft <= 7) return "text-red-600";
		if (priority === "critical") return "text-red-600";
		if (priority === "high") return "text-orange-600";
		return "text-muted-foreground";
	};

	return (
		<Card className="h-fit">
			<CardHeader>
				<CardTitle className="text-lg flex items-center gap-2">
					<Bell className="h-5 w-5" />
					Upcoming Deadlines
				</CardTitle>
			</CardHeader>
			<CardContent className="space-y-4">
				{deadlines.length === 0 ? (
					<div className="text-center py-8 text-muted-foreground">
						<Calendar className="h-8 w-8 mx-auto mb-2" />
						<p className="text-sm">No upcoming deadlines</p>
					</div>
				) : (
					deadlines.map((deadline) => (
						<div
							key={deadline.id}
							className="space-y-3 pb-4 border-b border-muted last:border-0 last:pb-0"
						>
							<div className="flex items-start gap-3">
								<div className="flex-shrink-0 mt-0.5">
									{getDeadlineIcon(deadline.type)}
								</div>
								<div className="flex-1 min-w-0">
									<h4 className="font-medium text-sm leading-tight mb-1 truncate">
										{deadline.title}
									</h4>
									<p className="text-xs text-muted-foreground mb-2 truncate">
										{deadline.provider}
									</p>

									<div className="flex items-center gap-2 mb-2">
										<Badge variant="outline" className="text-xs">
											{deadline.category}
										</Badge>
										{deadline.priority === "critical" && (
											<Badge variant="destructive" className="text-xs">
												Critical
											</Badge>
										)}
									</div>

									<div className="space-y-1 text-xs">
										<div className="flex items-center gap-1">
											<Calendar className="h-3 w-3" />
											<span>
												{new Date(deadline.date).toLocaleDateString()}
											</span>
										</div>
										<div className="flex items-center gap-1">
											<Clock className="h-3 w-3" />
											<span
												className={getPriorityColor(
													deadline.priority,
													deadline.daysLeft,
												)}
											>
												{deadline.daysLeft <= 0
													? "Overdue"
													: `${deadline.daysLeft} days left`}
											</span>
										</div>
									</div>

									<div className="flex gap-1 mt-3">
										<Button
											variant="outline"
											size="sm"
											className="h-7 text-xs flex-1 bg-transparent"
											asChild
										>
											<Link href={`/applications/${deadline.applicationId}`}>
												View
											</Link>
										</Button>
										<Button variant="ghost" size="sm" className="h-7 w-7 p-0">
											<Bell className="h-3 w-3" />
										</Button>
									</div>
								</div>
							</div>
						</div>
					))
				)}

				{deadlines.length > 0 && (
					<Button variant="outline" className="w-full bg-transparent" asChild>
						<Link href="/calendar">
							<ExternalLink className="mr-2 h-4 w-4" />
							View All Deadlines
						</Link>
					</Button>
				)}
			</CardContent>
		</Card>
	);
}
