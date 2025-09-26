"use client";

import { Badge } from "@/core/components/ui/badge";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { AlertTriangle, CheckCircle, Clock, Info } from "lucide-react";

interface ApplicationTimelineProps {
	application: any;
}

export function ApplicationTimeline({ application }: ApplicationTimelineProps) {
	const getEventIcon = (type: string) => {
		switch (type) {
			case "success":
				return <CheckCircle className="h-5 w-5 text-green-600" />;
			case "warning":
				return <AlertTriangle className="h-5 w-5 text-orange-600" />;
			case "info":
				return <Info className="h-5 w-5 text-blue-600" />;
			default:
				return <Clock className="h-5 w-5 text-muted-foreground" />;
		}
	};

	const getEventColor = (type: string) => {
		switch (type) {
			case "success":
				return "border-green-200 bg-green-50";
			case "warning":
				return "border-orange-200 bg-orange-50";
			case "info":
				return "border-blue-200 bg-blue-50";
			default:
				return "border-muted bg-muted/50";
		}
	};

	return (
		<Card>
			<CardHeader>
				<CardTitle>Application History</CardTitle>
			</CardHeader>
			<CardContent>
				<div className="space-y-4">
					{application.timeline.map((event: any, index: number) => (
						<div key={index} className="flex gap-4">
							{/* Timeline Line */}
							<div className="flex flex-col items-center">
								<div className="flex-shrink-0">{getEventIcon(event.type)}</div>
								{index < application.timeline.length - 1 && (
									<div className="w-px h-12 bg-muted-foreground/30 mt-2" />
								)}
							</div>

							{/* Event Content */}
							<div
								className={`flex-1 p-4 rounded-lg border ${getEventColor(event.type)}`}
							>
								<div className="flex items-center justify-between mb-2">
									<h3 className="font-medium">{event.action}</h3>
									<Badge variant="outline" className="text-xs">
										{new Date(event.date).toLocaleDateString()}
									</Badge>
								</div>
								{event.description && (
									<p className="text-sm text-muted-foreground">
										{event.description}
									</p>
								)}
							</div>
						</div>
					))}
				</div>
			</CardContent>
		</Card>
	);
}
