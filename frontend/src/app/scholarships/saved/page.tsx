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
	BookmarkCheck,
	Calendar,
	ExternalLink,
	MapPin,
	Trash2,
} from "lucide-react";
import { useState } from "react";

// Mock saved scholarships
const mockSavedScholarships = [
	{
		id: "s1",
		title: "University of Oxford Graduate Scholarship",
		provider: "University of Oxford",
		country: "United Kingdom",
		amount: "Full tuition + £15,000 stipend",
		deadline: "2024-03-15",
		savedDate: "2024-01-10",
		matchScore: 85,
		status: "saved",
	},
	{
		id: "s3",
		title: "DAAD Study Scholarship",
		provider: "German Academic Exchange Service",
		country: "Germany",
		amount: "€850/month + tuition coverage",
		deadline: "2024-04-30",
		savedDate: "2024-01-12",
		matchScore: 91,
		status: "applied",
	},
];

export default function SavedScholarshipsPage() {
	const [savedScholarships, setSavedScholarships] = useState(
		mockSavedScholarships,
	);

	const removeScholarship = (id: string) => {
		setSavedScholarships(savedScholarships.filter((s) => s.id !== id));
	};

	const getDaysUntilDeadline = (deadline: string) => {
		const deadlineDate = new Date(deadline);
		const today = new Date();
		const diffTime = deadlineDate.getTime() - today.getTime();
		const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
		return diffDays;
	};

	return (
		<div className="min-h-screen bg-background">
			<div className="container mx-auto max-w-4xl px-4 py-8">
				<div className="mb-8">
					<h1 className="text-3xl font-bold mb-2">Saved Scholarships</h1>
					<p className="text-muted-foreground">
						Scholarships you've bookmarked for future reference and applications
					</p>
				</div>

				{savedScholarships.length === 0 ? (
					<Card className="text-center py-12">
						<CardContent>
							<BookmarkCheck className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
							<h3 className="text-lg font-semibold mb-2">
								No saved scholarships
							</h3>
							<p className="text-muted-foreground mb-4">
								Start exploring scholarships and save the ones that interest
								you.
							</p>
							<Button asChild>
								<a href="/scholarships">Browse Scholarships</a>
							</Button>
						</CardContent>
					</Card>
				) : (
					<div className="space-y-4">
						{savedScholarships.map((scholarship) => {
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
													{scholarship.status === "applied" && (
														<Badge variant="secondary">Applied</Badge>
													)}
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
												<div className="text-xs text-muted-foreground">
													Match
												</div>
											</div>
										</div>
									</CardHeader>
									<CardContent className="space-y-4">
										<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
											<div>
												<div className="font-medium">Amount</div>
												<div className="text-muted-foreground">
													{scholarship.amount}
												</div>
											</div>
											<div>
												<div className="font-medium">Deadline</div>
												<div
													className={`flex items-center gap-1 ${isUrgent && !isExpired ? "text-orange-600" : "text-muted-foreground"}`}
												>
													<Calendar className="h-3 w-3" />
													{new Date(scholarship.deadline).toLocaleDateString()}
													{!isExpired && (
														<span className="ml-1">
															({daysLeft} day{daysLeft !== 1 ? "s" : ""} left)
														</span>
													)}
												</div>
											</div>
										</div>

										<div className="text-xs text-muted-foreground">
											Saved on{" "}
											{new Date(scholarship.savedDate).toLocaleDateString()}
										</div>

										<div className="flex gap-2">
											<Button asChild className="flex-1">
												<a href={`/scholarships/${scholarship.id}`}>
													View Details
												</a>
											</Button>
											{scholarship.status !== "applied" && (
												<Button variant="outline">Apply Now</Button>
											)}
											<Button variant="outline" size="icon">
												<ExternalLink className="h-4 w-4" />
											</Button>
											<Button
												variant="outline"
												size="icon"
												onClick={() => removeScholarship(scholarship.id)}
												className="text-destructive hover:text-destructive"
											>
												<Trash2 className="h-4 w-4" />
											</Button>
										</div>
									</CardContent>
								</Card>
							);
						})}
					</div>
				)}
			</div>
		</div>
	);
}
