"use client";
import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import { Card, CardContent } from "@/core/components/ui/card";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/core/components/ui/dropdown-menu";
import { Progress } from "@/core/components/ui/progress";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import {
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
} from "@/core/components/ui/table";
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

interface ApplicationTableProps {
	applications: Application[];
	onStatusChange: (appId: string, newStatus: string) => void;
}

const statusOptions = [
	{
		value: "not-started",
		label: "Not Started",
		color: "bg-gray-100 text-gray-800",
	},
	{
		value: "in-progress",
		label: "In Progress",
		color: "bg-blue-100 text-blue-800",
	},
	{
		value: "submitted",
		label: "Submitted",
		color: "bg-yellow-100 text-yellow-800",
	},
	{
		value: "interview",
		label: "Interview",
		color: "bg-purple-100 text-purple-800",
	},
	{ value: "result", label: "Result", color: "bg-green-100 text-green-800" },
];

export function ApplicationTable({
	applications,
	onStatusChange,
}: ApplicationTableProps) {
	const getDaysUntilDeadline = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	};

	const getStatusBadge = (status: string) => {
		const statusOption = statusOptions.find(
			(option) => option.value === status,
		);
		return statusOption ? (
			<Badge className={`${statusOption.color} border-0`}>
				{statusOption.label}
			</Badge>
		) : (
			<Badge variant="outline">{status}</Badge>
		);
	};

	return (
		<Card>
			<CardContent className="p-0">
				<Table>
					<TableHeader>
						<TableRow>
							<TableHead>Scholarship</TableHead>
							<TableHead>Status</TableHead>
							<TableHead>Progress</TableHead>
							<TableHead>Documents</TableHead>
							<TableHead>Deadline</TableHead>
							<TableHead>Amount</TableHead>
							<TableHead>Last Updated</TableHead>
							<TableHead className="w-12"></TableHead>
						</TableRow>
					</TableHeader>
					<TableBody>
						{applications.map((application) => {
							const daysLeft = getDaysUntilDeadline(application.deadline);
							const isUrgent = daysLeft <= 30 && daysLeft > 0;
							const isExpired = daysLeft < 0;

							return (
								<TableRow key={application.id} className="hover:bg-muted/50">
									<TableCell>
										<div>
											<div className="font-medium text-sm">
												{application.scholarshipTitle}
											</div>
											<div className="text-xs text-muted-foreground">
												{application.provider} • {application.country}
											</div>
										</div>
									</TableCell>

									<TableCell>
										<Select
											value={application.status}
											onValueChange={(value) =>
												onStatusChange(application.id, value)
											}
										>
											<SelectTrigger className="w-32 h-8">
												<SelectValue />
											</SelectTrigger>
											<SelectContent>
												{statusOptions.map((option) => (
													<SelectItem key={option.value} value={option.value}>
														{option.label}
													</SelectItem>
												))}
											</SelectContent>
										</Select>
									</TableCell>

									<TableCell>
										<div className="space-y-1 w-20">
											<div className="flex justify-between text-xs">
												<span>{application.progress}%</span>
											</div>
											<Progress
												value={application.progress}
												className="h-1.5"
											/>
										</div>
									</TableCell>

									<TableCell>
										<div className="flex items-center gap-2">
											<FileText className="h-4 w-4 text-muted-foreground" />
											<span className="text-sm">
												{application.documents.uploaded.length}/
												{application.documents.required.length}
											</span>
											{application.documents.pending.length > 0 && (
												<Badge variant="outline" className="text-xs">
													{application.documents.pending.length} pending
												</Badge>
											)}
										</div>
									</TableCell>

									<TableCell>
										<div className="flex items-center gap-2">
											<Calendar className="h-4 w-4 text-muted-foreground" />
											<div className="text-sm">
												<div
													className={`${isUrgent ? "text-orange-600" : isExpired ? "text-red-600" : ""}`}
												>
													{new Date(application.deadline).toLocaleDateString()}
												</div>
												{!isExpired && (
													<div className="text-xs text-muted-foreground">
														{daysLeft} day{daysLeft !== 1 ? "s" : ""} left
													</div>
												)}
											</div>
											{isUrgent && (
												<AlertTriangle className="h-4 w-4 text-orange-600" />
											)}
											{isExpired && (
												<AlertTriangle className="h-4 w-4 text-red-600" />
											)}
										</div>
									</TableCell>

									<TableCell>
										<div className="text-sm text-muted-foreground max-w-32 truncate">
											{application.amount}
										</div>
									</TableCell>

									<TableCell>
										<div className="text-sm text-muted-foreground">
											{new Date(application.lastUpdated).toLocaleDateString()}
										</div>
										{application.reminders.length > 0 && (
											<div className="flex items-center gap-1 text-xs text-orange-600 mt-1">
												<Bell className="h-3 w-3" />
												<span>{application.reminders.length}</span>
											</div>
										)}
									</TableCell>

									<TableCell>
										<DropdownMenu>
											<DropdownMenuTrigger asChild>
												<Button
													variant="ghost"
													size="sm"
													className="h-8 w-8 p-0"
												>
													<MoreHorizontal className="h-4 w-4" />
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
													<Link
														href={`/scholarships/${application.scholarshipId}`}
													>
														<ExternalLink className="mr-2 h-4 w-4" />
														View Scholarship
													</Link>
												</DropdownMenuItem>
											</DropdownMenuContent>
										</DropdownMenu>
									</TableCell>
								</TableRow>
							);
						})}
					</TableBody>
				</Table>
			</CardContent>
		</Card>
	);
}
