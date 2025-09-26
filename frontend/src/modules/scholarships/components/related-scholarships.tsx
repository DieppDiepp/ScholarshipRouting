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
import { Calendar, DollarSign, MapPin } from "lucide-react";
import Link from "next/link";

interface RelatedScholarshipsProps {
	currentScholarshipId: string;
}

// Mock related scholarships
const mockRelatedScholarships = [
	{
		id: "s2",
		title: "MIT Graduate Fellowship",
		provider: "Massachusetts Institute of Technology",
		country: "United States",
		amount: "Full tuition + $40,000 stipend",
		deadline: "2024-02-01",
		matchScore: 72,
		tags: ["PhD", "Research", "Technology"],
	},
	{
		id: "s3",
		title: "DAAD Study Scholarship",
		provider: "German Academic Exchange Service",
		country: "Germany",
		amount: "€850/month + tuition coverage",
		deadline: "2024-04-30",
		matchScore: 91,
		tags: ["Europe", "Living Allowance", "Cultural Exchange"],
	},
	{
		id: "s4",
		title: "Cambridge Gates Scholarship",
		provider: "University of Cambridge",
		country: "United Kingdom",
		amount: "Full funding + living costs",
		deadline: "2024-01-15",
		matchScore: 88,
		tags: ["Prestigious", "Full Funding", "Leadership"],
	},
];

export function RelatedScholarships({
	currentScholarshipId,
}: RelatedScholarshipsProps) {
	const relatedScholarships = mockRelatedScholarships.filter(
		(s) => s.id !== currentScholarshipId,
	);

	const getDaysUntilDeadline = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	};

	return (
		<div className="space-y-6">
			<Card>
				<CardHeader>
					<CardTitle>Similar Scholarships</CardTitle>
					<CardDescription>
						Other scholarships that might match your profile and interests
					</CardDescription>
				</CardHeader>
			</Card>

			<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
				{relatedScholarships.map((scholarship) => {
					const daysLeft = getDaysUntilDeadline(scholarship.deadline);
					const isUrgent = daysLeft <= 30;
					const isExpired = daysLeft < 0;

					return (
						<Card
							key={scholarship.id}
							className="hover:shadow-lg transition-shadow"
						>
							<CardHeader className="pb-3">
								<div className="flex justify-between items-start">
									<div className="flex-1">
										<div className="flex items-center gap-2 mb-2">
											<CardTitle className="text-lg">
												{scholarship.title}
											</CardTitle>
											{isUrgent && !isExpired && (
												<Badge variant="destructive" className="text-xs">
													Urgent
												</Badge>
											)}
										</div>
										<CardDescription className="flex items-center gap-4">
											<span className="font-medium">
												{scholarship.provider}
											</span>
											<span className="flex items-center gap-1">
												<MapPin className="h-3 w-3" />
												{scholarship.country}
											</span>
										</CardDescription>
									</div>
									<div className="text-center">
										<div className="text-xl font-bold text-green-600">
											{scholarship.matchScore}%
										</div>
										<div className="text-xs text-muted-foreground">Match</div>
									</div>
								</div>

								<div className="flex flex-wrap gap-1 mt-2">
									{scholarship.tags.map((tag) => (
										<Badge key={tag} variant="outline" className="text-xs">
											{tag}
										</Badge>
									))}
								</div>
							</CardHeader>

							<CardContent className="space-y-4">
								<div className="grid grid-cols-1 gap-3 text-sm">
									<div className="flex items-center gap-2">
										<DollarSign className="h-4 w-4 text-green-600" />
										<span className="text-muted-foreground">
											{scholarship.amount}
										</span>
									</div>
									<div className="flex items-center gap-2">
										<Calendar className="h-4 w-4 text-blue-600" />
										<span
											className={`${isUrgent && !isExpired ? "text-orange-600" : "text-muted-foreground"}`}
										>
											{new Date(scholarship.deadline).toLocaleDateString()}
											{!isExpired && (
												<span className="ml-1">
													({daysLeft} day{daysLeft !== 1 ? "s" : ""} left)
												</span>
											)}
										</span>
									</div>
								</div>

								<div className="flex gap-2">
									<Button asChild className="flex-1">
										<Link href={`/scholarships/${scholarship.id}`}>
											View Details
										</Link>
									</Button>
									<Button variant="outline">Compare</Button>
								</div>
							</CardContent>
						</Card>
					);
				})}
			</div>

			<Card className="text-center py-8">
				<CardContent>
					<h3 className="text-lg font-semibold mb-2">
						Looking for More Options?
					</h3>
					<p className="text-muted-foreground mb-4">
						Explore our full database of scholarships to find more opportunities
						that match your profile.
					</p>
					<Button asChild>
						<Link href="/scholarships">Browse All Scholarships</Link>
					</Button>
				</CardContent>
			</Card>
		</div>
	);
}
