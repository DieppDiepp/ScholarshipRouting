"use client";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { AlertTriangle, Calendar, CheckCircle, Clock } from "lucide-react";

interface ApplicationTimelineProps {
	scholarship: any;
}

export function ApplicationTimeline({ scholarship }: ApplicationTimelineProps) {
	const getStepStatus = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const daysLeft = Math.ceil(
			(deadlineDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24),
		);

		if (daysLeft < 0) return "overdue";
		if (daysLeft <= 7) return "urgent";
		if (daysLeft <= 30) return "upcoming";
		return "future";
	};

	const getStatusIcon = (status: string) => {
		switch (status) {
			case "completed":
				return <CheckCircle className="h-5 w-5 text-green-600" />;
			case "urgent":
				return <AlertTriangle className="h-5 w-5 text-red-600" />;
			case "upcoming":
				return <Clock className="h-5 w-5 text-orange-600" />;
			default:
				return <Clock className="h-5 w-5 text-muted-foreground" />;
		}
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case "completed":
				return "default";
			case "urgent":
				return "destructive";
			case "upcoming":
				return "secondary";
			default:
				return "outline";
		}
	};

	return (
		<div className="space-y-6">
			{/* Timeline Overview */}
			<Card>
				<CardHeader>
					<CardTitle>Application Process Timeline</CardTitle>
					<CardDescription>
						Key milestones and deadlines for this scholarship application
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="space-y-6">
						{scholarship.applicationProcess.map((step: any, index: number) => {
							const stepStatus = getStepStatus(step.deadline);
							const daysLeft = Math.ceil(
								(new Date(step.deadline).getTime() - new Date().getTime()) /
									(1000 * 60 * 60 * 24),
							);

							return (
								<div key={index} className="flex gap-4">
									{/* Step Number & Icon */}
									<div className="flex flex-col items-center">
										<div
											className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
												step.status === "completed"
													? "bg-green-600 border-green-600 text-white"
													: stepStatus === "urgent"
														? "border-red-600 text-red-600"
														: stepStatus === "upcoming"
															? "border-orange-600 text-orange-600"
															: "border-muted-foreground text-muted-foreground"
											}`}
										>
											{step.status === "completed" ? (
												<CheckCircle className="h-5 w-5" />
											) : (
												<span className="text-sm font-medium">{step.step}</span>
											)}
										</div>
										{index < scholarship.applicationProcess.length - 1 && (
											<div className="w-px h-16 bg-muted-foreground/30 mt-2" />
										)}
									</div>

									{/* Step Content */}
									<div className="flex-1 pb-8">
										<div className="flex items-center justify-between mb-2">
											<h3 className="font-medium">{step.title}</h3>
											<div className="flex items-center gap-2">
												<Badge variant={getStatusColor(stepStatus)}>
													{stepStatus === "overdue"
														? "Overdue"
														: stepStatus === "urgent"
															? "Urgent"
															: stepStatus === "upcoming"
																? "Upcoming"
																: "Future"}
												</Badge>
												{step.status === "completed" && (
													<Badge variant="default">Completed</Badge>
												)}
											</div>
										</div>

										<p className="text-sm text-muted-foreground mb-3">
											{step.description}
										</p>

										<div className="flex items-center justify-between">
											<div className="flex items-center gap-2 text-sm">
												<Calendar className="h-4 w-4" />
												<span
													className={`${stepStatus === "urgent" ? "text-red-600" : "text-muted-foreground"}`}
												>
													Deadline:{" "}
													{new Date(step.deadline).toLocaleDateString()}
													{daysLeft >= 0 && (
														<span className="ml-1">
															({daysLeft} day{daysLeft !== 1 ? "s" : ""} left)
														</span>
													)}
												</span>
											</div>

											{step.status !== "completed" &&
												stepStatus !== "overdue" && (
													<Button variant="outline" size="sm">
														{stepStatus === "urgent"
															? "Complete Now"
															: "Prepare"}
													</Button>
												)}
										</div>
									</div>
								</div>
							);
						})}
					</div>
				</CardContent>
			</Card>

			{/* Important Dates */}
			<Card>
				<CardHeader>
					<CardTitle>Important Dates</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div className="flex items-center gap-3 p-3 border rounded-lg">
							<Calendar className="h-5 w-5 text-blue-600" />
							<div>
								<div className="font-medium text-sm">Application Opens</div>
								<div className="text-sm text-muted-foreground">
									{new Date(
										scholarship.applicationOpenDate,
									).toLocaleDateString()}
								</div>
							</div>
						</div>

						<div className="flex items-center gap-3 p-3 border rounded-lg">
							<AlertTriangle className="h-5 w-5 text-red-600" />
							<div>
								<div className="font-medium text-sm">Application Deadline</div>
								<div className="text-sm text-red-600">
									{new Date(scholarship.deadline).toLocaleDateString()}
								</div>
							</div>
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Contact Information */}
			<Card>
				<CardHeader>
					<CardTitle>Need Help?</CardTitle>
					<CardDescription>
						Contact the scholarship provider for questions
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="space-y-3">
						<div className="flex items-center gap-2 text-sm">
							<span className="font-medium">Email:</span>
							<a
								href={`mailto:${scholarship.contactInfo.email}`}
								className="text-blue-600 hover:underline"
							>
								{scholarship.contactInfo.email}
							</a>
						</div>
						<div className="flex items-center gap-2 text-sm">
							<span className="font-medium">Phone:</span>
							<span className="text-muted-foreground">
								{scholarship.contactInfo.phone}
							</span>
						</div>
						<div className="flex items-center gap-2 text-sm">
							<span className="font-medium">Website:</span>
							<a
								href={scholarship.contactInfo.website}
								target="_blank"
								rel="noopener noreferrer"
								className="text-blue-600 hover:underline"
							>
								Official Information Page
							</a>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
