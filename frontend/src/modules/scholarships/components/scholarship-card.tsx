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
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@/core/components/ui/popover";
import { Progress } from "@/core/components/ui/progress";
import { Separator } from "@/core/components/ui/separator";
import {
	BookmarkPlus,
	Calendar,
	CheckCircle,
	DollarSign,
	ExternalLink,
	Info,
	MapPin,
	XCircle,
} from "lucide-react";
import Link from "next/link";

interface Scholarship {
	id: string;
	title: string;
	provider: string;
	country: string;
	degreeLevel: string;
	amount: string;
	deadline: string;
	matchScore: number;
	hardConditionsPassed: boolean;
	failedConditions: string[];
	description: string;
	tags: string[];
	link: string;
}

interface ScholarshipCardProps {
	scholarship: Scholarship;
}

export function ScholarshipCard({ scholarship }: ScholarshipCardProps) {
	const getMatchScoreColor = (score: number) => {
		if (score >= 80) return "text-green-600";
		if (score >= 60) return "text-yellow-600";
		return "text-red-600";
	};

	const getMatchScoreVariant = (score: number) => {
		if (score >= 80) return "default";
		if (score >= 60) return "secondary";
		return "outline";
	};

	const getDaysUntilDeadline = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	};

	const daysLeft = getDaysUntilDeadline(scholarship.deadline);
	const isUrgent = daysLeft <= 30;
	const isExpired = daysLeft < 0;

	return (
		<Card
			className={`hover:shadow-lg transition-shadow ${isUrgent && !isExpired ? "border-orange-200" : ""}`}
		>
			<CardHeader className="pb-3">
				<div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
					<div className="flex-1">
						<div className="flex flex-col sm:flex-row sm:items-center gap-2 mb-2">
							<CardTitle className="text-lg leading-tight">
								{scholarship.title}
							</CardTitle>
							<div className="flex gap-2">
								{isUrgent && !isExpired && (
									<Badge variant="destructive" className="text-xs">
										Urgent
									</Badge>
								)}
								{isExpired && (
									<Badge
										variant="outline"
										className="text-xs text-muted-foreground"
									>
										Expired
									</Badge>
								)}
							</div>
						</div>
						<CardDescription className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm">
							<span className="font-medium">{scholarship.provider}</span>
							<span className="flex items-center gap-1">
								<MapPin className="h-3 w-3" />
								{scholarship.country}
							</span>
						</CardDescription>
					</div>

					{/* Match Score */}
					<div className="text-center sm:text-right">
						<div
							className={`text-2xl font-bold ${getMatchScoreColor(scholarship.matchScore)}`}
						>
							{scholarship.matchScore}%
						</div>
						<div className="text-xs text-muted-foreground">Match</div>
					</div>
				</div>

				{/* Tags */}
				<div className="flex flex-wrap gap-1 mt-2">
					{scholarship.tags.map((tag) => (
						<Badge key={tag} variant="outline" className="text-xs">
							{tag}
						</Badge>
					))}
				</div>
			</CardHeader>

			<CardContent className="space-y-4">
				{/* Description */}
				<p className="text-sm text-muted-foreground line-clamp-2">
					{scholarship.description}
				</p>

				{/* Key Info */}
				<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
					<div className="flex items-center gap-2">
						<DollarSign className="h-4 w-4 text-green-600 flex-shrink-0" />
						<div className="min-w-0">
							<div className="font-medium">Amount</div>
							<div className="text-muted-foreground truncate">
								{scholarship.amount}
							</div>
						</div>
					</div>
					<div className="flex items-center gap-2">
						<Calendar className="h-4 w-4 text-blue-600 flex-shrink-0" />
						<div className="min-w-0">
							<div className="font-medium">Deadline</div>
							<div
								className={`${isUrgent && !isExpired ? "text-orange-600" : "text-muted-foreground"}`}
							>
								<div className="truncate">
									{new Date(scholarship.deadline).toLocaleDateString()}
								</div>
								{!isExpired && (
									<div className="text-xs">
										({daysLeft} day{daysLeft !== 1 ? "s" : ""} left)
									</div>
								)}
							</div>
						</div>
					</div>
					<div className="flex items-center gap-2 sm:col-span-2 lg:col-span-1">
						<Badge variant="outline" className="text-xs">
							{scholarship.degreeLevel}
						</Badge>
					</div>
				</div>

				<Separator />

				{/* Match Analysis */}
				<div className="space-y-3">
					<div className="flex items-center justify-between">
						<span className="text-sm font-medium">Eligibility Status</span>
						<div className="flex items-center gap-2">
							{scholarship.hardConditionsPassed ? (
								<>
									<CheckCircle className="h-4 w-4 text-green-600" />
									<span className="text-sm text-green-600">
										All requirements met
									</span>
								</>
							) : (
								<>
									<XCircle className="h-4 w-4 text-red-600" />
									<span className="text-sm text-red-600">
										Requirements not met
									</span>
								</>
							)}
							<Popover>
								<PopoverTrigger asChild>
									<Button variant="ghost" size="sm" className="h-6 w-6 p-0">
										<Info className="h-3 w-3" />
									</Button>
								</PopoverTrigger>
								<PopoverContent className="w-80" align="end">
									<div className="space-y-2">
										<h4 className="font-medium text-sm">Match Breakdown</h4>
										{scholarship.hardConditionsPassed ? (
											<div className="text-sm text-green-600">
												✓ All hard requirements satisfied
											</div>
										) : (
											<div className="space-y-1">
												<div className="text-sm text-red-600 font-medium">
													Failed Requirements:
												</div>
												{scholarship.failedConditions.map(
													(condition, index) => (
														<div key={index} className="text-sm text-red-600">
															• {condition}
														</div>
													),
												)}
											</div>
										)}
										<div className="text-xs text-muted-foreground mt-2">
											Soft factors contribute to the overall match score based
											on your profile strength.
										</div>
									</div>
								</PopoverContent>
							</Popover>
						</div>
					</div>

					{/* Match Score Progress */}
					<div className="space-y-1">
						<div className="flex justify-between text-xs">
							<span>Overall Match Score</span>
							<span className={getMatchScoreColor(scholarship.matchScore)}>
								{scholarship.matchScore}%
							</span>
						</div>
						<Progress value={scholarship.matchScore} className="h-2" />
					</div>
				</div>

				<Separator />

				{/* Actions */}
				<div className="flex flex-col gap-2">
					<Button asChild className="w-full min-h-[44px]">
						<Link href={`/scholarships/${scholarship.id}`}>View Details</Link>
					</Button>
					<div className="flex flex-col sm:flex-row gap-2">
						<Button
							variant="outline"
							className="flex-1 min-h-[44px] bg-transparent"
						>
							<BookmarkPlus className="mr-2 h-4 w-4" />
							Save
						</Button>
						<Button
							variant="outline"
							asChild
							className="flex-1 min-h-[44px] bg-transparent"
						>
							<a
								href={scholarship.link}
								target="_blank"
								rel="noopener noreferrer"
								className="flex items-center justify-center"
							>
								<ExternalLink className="mr-2 h-4 w-4" />
								Official Site
							</a>
						</Button>
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
