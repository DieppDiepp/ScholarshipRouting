"use client";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Progress } from "@/core/components/ui/progress";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@/core/components/ui/tabs";
import { Textarea } from "@/core/components/ui/textarea";
import { ApplicationDocuments } from "@/modules/applications/components/application-documents";
import { ApplicationReminders } from "@/modules/applications/components/application-reminders";
import { ApplicationTimeline } from "@/modules/applications/components/application-timeline";
import {
	ArrowLeft,
	Bell,
	Calendar,
	CheckCircle,
	Download,
	Edit,
	ExternalLink,
	FileText,
	History,
	MessageSquare,
	Upload,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

// Mock application data - in real app this would come from API
const mockApplicationData = {
	app1: {
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
			required: [
				{
					name: "CV/Resume",
					status: "uploaded",
					uploadDate: "2024-01-12",
					fileSize: "245 KB",
					fileName: "John_Doe_CV.pdf",
				},
				{
					name: "Academic Transcripts",
					status: "uploaded",
					uploadDate: "2024-01-15",
					fileSize: "1.2 MB",
					fileName: "Transcripts_Official.pdf",
				},
				{
					name: "Personal Statement",
					status: "pending",
					uploadDate: null,
					fileSize: null,
					fileName: null,
				},
				{
					name: "Reference Letters",
					status: "pending",
					uploadDate: null,
					fileSize: null,
					fileName: null,
				},
			],
		},
		timeline: [
			{
				date: "2024-01-10",
				action: "Application started",
				type: "info",
				description: "Added scholarship to applications list",
			},
			{
				date: "2024-01-12",
				action: "CV uploaded",
				type: "success",
				description: "Successfully uploaded CV document",
			},
			{
				date: "2024-01-15",
				action: "Transcript uploaded",
				type: "success",
				description: "Official transcripts uploaded and verified",
			},
		],
		reminders: [
			{
				id: "r1",
				date: "2024-02-01",
				message: "Personal Statement due in 2 weeks",
				type: "deadline",
				isActive: true,
			},
			{
				id: "r2",
				date: "2024-02-15",
				message: "Reference letters due in 4 weeks",
				type: "deadline",
				isActive: true,
			},
		],
		notes:
			"Focus on research experience in personal statement. Contact Prof. Smith for reference letter.",
		applicationUrl: "https://oxford.edu/apply/12345",
	},
};

export default function ApplicationDetailPage() {
	const params = useParams();
	const applicationId = params.id as string;
	const application =
		mockApplicationData[applicationId as keyof typeof mockApplicationData];

	const [notes, setNotes] = useState(application?.notes || "");
	const [activeTab, setActiveTab] = useState("overview");

	if (!application) {
		return (
			<div className="min-h-screen bg-background flex items-center justify-center">
				<Card className="max-w-md">
					<CardContent className="text-center py-8">
						<h2 className="text-xl font-semibold mb-2">
							Application Not Found
						</h2>
						<p className="text-muted-foreground mb-4">
							The application you're looking for doesn't exist.
						</p>
						<Button asChild>
							<Link href="/applications">Back to Applications</Link>
						</Button>
					</CardContent>
				</Card>
			</div>
		);
	}

	const getDaysUntilDeadline = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	};

	const daysLeft = getDaysUntilDeadline(application.deadline);
	const isUrgent = daysLeft <= 30 && daysLeft > 0;
	const isExpired = daysLeft < 0;

	const getStatusBadge = (status: string) => {
		const statusConfig = {
			"not-started": { label: "Not Started", variant: "outline" as const },
			"in-progress": { label: "In Progress", variant: "secondary" as const },
			submitted: { label: "Submitted", variant: "default" as const },
			interview: { label: "Interview", variant: "default" as const },
			result: { label: "Result", variant: "default" as const },
		};

		const config = statusConfig[status as keyof typeof statusConfig] || {
			label: status,
			variant: "outline" as const,
		};
		return <Badge variant={config.variant}>{config.label}</Badge>;
	};

	return (
		<div className="min-h-screen bg-background">
			<div className="container mx-auto max-w-6xl px-4 py-8">
				{/* Back Navigation */}
				<div className="mb-6">
					<Button variant="ghost" asChild className="mb-4">
						<Link href="/applications" className="flex items-center">
							<ArrowLeft className="mr-2 h-4 w-4" />
							Back to Applications
						</Link>
					</Button>
				</div>

				{/* Header */}
				<Card className="mb-8">
					<CardHeader>
						<div className="flex flex-col lg:flex-row justify-between items-start gap-6">
							<div className="flex-1">
								<div className="flex items-center gap-3 mb-3">
									<CardTitle className="text-2xl lg:text-3xl">
										{application.scholarshipTitle}
									</CardTitle>
									{getStatusBadge(application.status)}
									{isUrgent && !isExpired && (
										<Badge variant="destructive">Urgent</Badge>
									)}
									{isExpired && (
										<Badge variant="outline" className="text-muted-foreground">
											Expired
										</Badge>
									)}
								</div>

								<div className="flex flex-wrap items-center gap-4 text-muted-foreground mb-4">
									<span className="font-medium text-foreground">
										{application.provider}
									</span>
									<span>{application.country}</span>
									<span>{application.amount}</span>
								</div>
							</div>

							{/* Progress & Actions */}
							<div className="flex flex-col items-center gap-4">
								<div className="text-center">
									<div className="text-3xl font-bold text-primary">
										{application.progress}%
									</div>
									<div className="text-sm text-muted-foreground">Complete</div>
									<Progress
										value={application.progress}
										className="w-20 h-2 mt-1"
									/>
								</div>

								<div className="flex gap-2">
									<Button variant="outline" asChild>
										<Link href={`/scholarships/${application.scholarshipId}`}>
											<ExternalLink className="mr-2 h-4 w-4" />
											View Scholarship
										</Link>
									</Button>
									<Button>
										<Edit className="mr-2 h-4 w-4" />
										Edit Application
									</Button>
								</div>
							</div>
						</div>
					</CardHeader>

					<CardContent>
						{/* Key Information */}
						<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
							<div className="flex items-center gap-3">
								<div className="p-2 bg-blue-100 rounded-lg">
									<Calendar className="h-5 w-5 text-blue-600" />
								</div>
								<div>
									<div className="font-medium">Application Deadline</div>
									<div
										className={`text-sm ${isUrgent && !isExpired ? "text-orange-600" : "text-muted-foreground"}`}
									>
										{new Date(application.deadline).toLocaleDateString()}
										{!isExpired && (
											<span className="ml-1">({daysLeft} days left)</span>
										)}
									</div>
								</div>
							</div>

							<div className="flex items-center gap-3">
								<div className="p-2 bg-green-100 rounded-lg">
									<FileText className="h-5 w-5 text-green-600" />
								</div>
								<div>
									<div className="font-medium">Documents</div>
									<div className="text-sm text-muted-foreground">
										{
											application.documents.required.filter(
												(doc) => doc.status === "uploaded",
											).length
										}
										/{application.documents.required.length} uploaded
									</div>
								</div>
							</div>

							<div className="flex items-center gap-3">
								<div className="p-2 bg-orange-100 rounded-lg">
									<Bell className="h-5 w-5 text-orange-600" />
								</div>
								<div>
									<div className="font-medium">Active Reminders</div>
									<div className="text-sm text-muted-foreground">
										{application.reminders.filter((r) => r.isActive).length}{" "}
										pending
									</div>
								</div>
							</div>
						</div>

						{/* Quick Actions */}
						<div className="flex flex-col sm:flex-row gap-3">
							<Button size="lg" className="flex-1" disabled={isExpired}>
								{isExpired ? "Application Closed" : "Continue Application"}
							</Button>
							<Button variant="outline" size="lg">
								<Upload className="mr-2 h-4 w-4" />
								Upload Documents
							</Button>
							<Button variant="outline" size="lg">
								<Download className="mr-2 h-4 w-4" />
								Download Progress
							</Button>
						</div>
					</CardContent>
				</Card>

				{/* Main Content Tabs */}
				<Tabs
					value={activeTab}
					onValueChange={setActiveTab}
					className="space-y-6"
				>
					<TabsList className="grid w-full grid-cols-2 lg:grid-cols-5">
						<TabsTrigger value="overview">Overview</TabsTrigger>
						<TabsTrigger value="documents">Documents</TabsTrigger>
						<TabsTrigger value="timeline">Timeline</TabsTrigger>
						<TabsTrigger value="reminders">Reminders</TabsTrigger>
						<TabsTrigger value="notes">Notes</TabsTrigger>
					</TabsList>

					<TabsContent value="overview" className="space-y-6">
						<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
							{/* Progress Overview */}
							<Card>
								<CardHeader>
									<CardTitle className="flex items-center gap-2">
										<CheckCircle className="h-5 w-5" />
										Application Progress
									</CardTitle>
								</CardHeader>
								<CardContent className="space-y-4">
									<div className="space-y-2">
										<div className="flex justify-between text-sm">
											<span>Overall Completion</span>
											<span className="font-medium">
												{application.progress}%
											</span>
										</div>
										<Progress value={application.progress} className="h-2" />
									</div>

									<div className="space-y-2 text-sm">
										<div className="flex justify-between">
											<span>Documents Uploaded</span>
											<span>
												{
													application.documents.required.filter(
														(doc) => doc.status === "uploaded",
													).length
												}
												/{application.documents.required.length}
											</span>
										</div>
										<div className="flex justify-between">
											<span>Status</span>
											<span>{getStatusBadge(application.status)}</span>
										</div>
										<div className="flex justify-between">
											<span>Last Updated</span>
											<span>
												{new Date(application.lastUpdated).toLocaleDateString()}
											</span>
										</div>
									</div>
								</CardContent>
							</Card>

							{/* Recent Activity */}
							<Card>
								<CardHeader>
									<CardTitle className="flex items-center gap-2">
										<History className="h-5 w-5" />
										Recent Activity
									</CardTitle>
								</CardHeader>
								<CardContent>
									<div className="space-y-3">
										{application.timeline
											.slice(-3)
											.reverse()
											.map((event, index) => (
												<div key={index} className="flex items-start gap-3">
													<div
														className={`p-1 rounded-full ${
															event.type === "success"
																? "bg-green-100"
																: event.type === "warning"
																	? "bg-orange-100"
																	: "bg-blue-100"
														}`}
													>
														<div
															className={`w-2 h-2 rounded-full ${
																event.type === "success"
																	? "bg-green-600"
																	: event.type === "warning"
																		? "bg-orange-600"
																		: "bg-blue-600"
															}`}
														/>
													</div>
													<div className="flex-1">
														<div className="text-sm font-medium">
															{event.action}
														</div>
														<div className="text-xs text-muted-foreground">
															{event.description}
														</div>
														<div className="text-xs text-muted-foreground">
															{new Date(event.date).toLocaleDateString()}
														</div>
													</div>
												</div>
											))}
									</div>
								</CardContent>
							</Card>
						</div>
					</TabsContent>

					<TabsContent value="documents">
						<ApplicationDocuments application={application} />
					</TabsContent>

					<TabsContent value="timeline">
						<ApplicationTimeline application={application} />
					</TabsContent>

					<TabsContent value="reminders">
						<ApplicationReminders application={application} />
					</TabsContent>

					<TabsContent value="notes">
						<Card>
							<CardHeader>
								<CardTitle className="flex items-center gap-2">
									<MessageSquare className="h-5 w-5" />
									Application Notes
								</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="space-y-4">
									<Textarea
										placeholder="Add your notes about this application..."
										value={notes}
										onChange={(e) => setNotes(e.target.value)}
										className="min-h-32"
									/>
									<Button>Save Notes</Button>
								</div>
							</CardContent>
						</Card>
					</TabsContent>
				</Tabs>
			</div>
		</div>
	);
}
