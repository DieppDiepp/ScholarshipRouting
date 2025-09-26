"use client";

import { Button } from "@/core/components/ui/button";
import { Card, CardContent } from "@/core/components/ui/card";
import { Input } from "@/core/components/ui/input";
import { Progress } from "@/core/components/ui/progress";
import { Separator } from "@/core/components/ui/separator";
import {
	Sheet,
	SheetContent,
	SheetHeader,
	SheetTitle,
	SheetTrigger,
} from "@/core/components/ui/sheet";
import { ScholarshipCard } from "@/modules/scholarships/components/scholarship-card";
import { ScholarshipFilters } from "@/modules/scholarships/components/scholarship-filters";
import { ScholarshipSort } from "@/modules/scholarships/components/scholarship-sort";
import { Filter, Search } from "lucide-react";
import { useState } from "react";

// Mock scholarship data
const mockScholarships = [
	{
		id: "s1",
		title: "University of Oxford Graduate Scholarship",
		provider: "University of Oxford",
		country: "United Kingdom",
		degreeLevel: "Master's",
		amount: "Full tuition + £15,000 stipend",
		deadline: "2024-03-15",
		hardConditions: {
			minGpa: 3.5,
			minIelts: 7.0,
			requiredField: ["Computer Science", "Engineering"],
			allowedNationalities: ["Vietnam", "Thailand", "Malaysia"],
		},
		softWeights: {
			gpa: 0.3,
			publication: 0.3,
			experience: 0.2,
			extracurricular: 0.2,
		},
		requiredDocuments: [
			"CV",
			"Transcript",
			"Personal Statement",
			"Reference Letters",
		],
		link: "https://oxford.edu/scholarships",
		matchScore: 85,
		hardConditionsPassed: true,
		failedConditions: [],
		description:
			"Prestigious scholarship for outstanding graduate students in STEM fields.",
		tags: ["STEM", "Research", "Full Funding"],
	},
	{
		id: "s2",
		title: "MIT Graduate Fellowship",
		provider: "Massachusetts Institute of Technology",
		country: "United States",
		degreeLevel: "PhD",
		amount: "Full tuition + $40,000 stipend",
		deadline: "2024-02-01",
		hardConditions: {
			minGpa: 3.7,
			minIelts: 7.5,
			requiredField: ["Computer Science", "Data Science", "AI"],
			allowedNationalities: ["Any"],
		},
		softWeights: {
			gpa: 0.25,
			publication: 0.4,
			experience: 0.2,
			extracurricular: 0.15,
		},
		requiredDocuments: [
			"CV",
			"Transcript",
			"Research Proposal",
			"Reference Letters",
		],
		link: "https://mit.edu/fellowships",
		matchScore: 72,
		hardConditionsPassed: false,
		failedConditions: ["GPA 3.4 < min 3.7"],
		description:
			"Elite fellowship for PhD students in cutting-edge technology research.",
		tags: ["PhD", "Research", "Technology"],
	},
	{
		id: "s3",
		title: "DAAD Study Scholarship",
		provider: "German Academic Exchange Service",
		country: "Germany",
		degreeLevel: "Master's",
		amount: "€850/month + tuition coverage",
		deadline: "2024-04-30",
		hardConditions: {
			minGpa: 3.0,
			minIelts: 6.5,
			requiredField: ["Any"],
			allowedNationalities: ["Vietnam", "Thailand", "Indonesia"],
		},
		softWeights: {
			gpa: 0.2,
			publication: 0.2,
			experience: 0.3,
			extracurricular: 0.3,
		},
		requiredDocuments: [
			"CV",
			"Transcript",
			"Motivation Letter",
			"Language Certificate",
		],
		link: "https://daad.de/scholarships",
		matchScore: 91,
		hardConditionsPassed: true,
		failedConditions: [],
		description:
			"Comprehensive scholarship program for international students in Germany.",
		tags: ["Europe", "Living Allowance", "Cultural Exchange"],
	},
];

interface ScholarFilter {
	countries: string[];
	degreeLevel: string;
	minAmount: string;
	maxGpa: string;
	minIelts: string;
	fields: string[];
	deadlineRange: string;
	onlyPassed: boolean;
}

export default function ScholarshipsPage() {
	const [searchQuery, setSearchQuery] = useState("");
	const [showFilters, setShowFilters] = useState(false);
	const [sortBy, setSortBy] = useState("match-score");
	const [scholarships, setScholarships] = useState(mockScholarships);
	const [filters, setFilters] = useState<ScholarFilter>({
		countries: [],
		degreeLevel: "",
		minAmount: "",
		maxGpa: "",
		minIelts: "",
		fields: [],
		deadlineRange: "",
		onlyPassed: false,
	});

	const filteredScholarships = scholarships.filter((scholarship) => {
		// Search query filter
		if (searchQuery) {
			const query = searchQuery.toLowerCase();
			const searchableText =
				`${scholarship.title} ${scholarship.provider} ${scholarship.country} ${scholarship.description}`.toLowerCase();
			if (!searchableText.includes(query)) return false;
		}

		// Apply other filters here
		if (filters.onlyPassed && !scholarship.hardConditionsPassed) return false;
		if (filters.degreeLevel && scholarship.degreeLevel !== filters.degreeLevel)
			return false;
		if (
			filters.countries.length > 0 &&
			!filters.countries.includes(scholarship.country)
		)
			return false;

		return true;
	});

	const sortedScholarships = [...filteredScholarships].sort((a, b) => {
		switch (sortBy) {
			case "match-score":
				return b.matchScore - a.matchScore;
			case "deadline":
				return new Date(a.deadline).getTime() - new Date(b.deadline).getTime();
			case "amount":
				return b.title.localeCompare(a.title); // Simplified sorting
			default:
				return 0;
		}
	});

	const passedCount = filteredScholarships.filter(
		(s) => s.hardConditionsPassed,
	).length;
	const totalCount = filteredScholarships.length;

	return (
		<div className="min-h-screen bg-background">
			<div className="container mx-auto max-w-7xl px-4 py-8">
				{/* Header */}
				<div className="mb-8">
					<h1 className="text-2xl md:text-3xl font-bold mb-2">
						Scholarship Discovery
					</h1>
					<p className="text-muted-foreground text-sm md:text-base">
						Find scholarships that match your profile with AI-powered
						recommendations
					</p>
				</div>

				{/* Search and Controls */}
				<Card className="mb-6">
					<CardContent className="p-4 md:p-6">
						<div className="space-y-4">
							{/* Search Bar */}
							<div className="relative">
								<Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
								<Input
									placeholder="Search scholarships by name, university, country..."
									value={searchQuery}
									onChange={(e) => setSearchQuery(e.target.value)}
									className="pl-10 min-h-[44px]"
								/>
							</div>

							{/* Controls */}
							<div className="flex flex-col sm:flex-row gap-2">
								<div className="block lg:hidden">
									<Sheet>
										<SheetTrigger asChild>
											<Button
												variant="outline"
												className="w-full min-h-[44px] bg-transparent"
											>
												<Filter className="mr-2 h-4 w-4" />
												Filters
											</Button>
										</SheetTrigger>
										<SheetContent side="left" className="w-full sm:w-80">
											<SheetHeader>
												<SheetTitle>Filter Scholarships</SheetTitle>
											</SheetHeader>
											<div className="mt-6">
												<ScholarshipFilters
													filters={filters}
													onFiltersChange={setFilters}
												/>
											</div>
										</SheetContent>
									</Sheet>
								</div>

								<div className="hidden lg:block">
									<Button
										variant={showFilters ? "default" : "outline"}
										onClick={() => setShowFilters(!showFilters)}
										className="min-h-[44px]"
									>
										<Filter className="mr-2 h-4 w-4" />
										Filters
									</Button>
								</div>

								<div className="flex-1 sm:flex-none">
									<ScholarshipSort sortBy={sortBy} onSortChange={setSortBy} />
								</div>
							</div>

							{/* Results Summary */}
							<div className="space-y-4">
								<div className="flex flex-col sm:flex-row sm:items-center gap-4 text-sm text-muted-foreground">
									<div className="flex flex-wrap items-center gap-2 sm:gap-4">
										<span>{totalCount} scholarships found</span>
										<Separator
											orientation="vertical"
											className="h-4 hidden sm:block"
										/>
										<span className="text-green-600">
											{passedCount} match your profile
										</span>
										<Separator
											orientation="vertical"
											className="h-4 hidden sm:block"
										/>
										<span>{totalCount - passedCount} need improvement</span>
									</div>
								</div>
								<div className="flex items-center space-x-2">
									<span className="text-sm text-muted-foreground">
										Match Rate:
									</span>
									<Progress
										value={(passedCount / totalCount) * 100}
										className="flex-1 sm:w-20 h-2"
									/>
									<span className="text-sm font-medium">
										{Math.round((passedCount / totalCount) * 100)}%
									</span>
								</div>
							</div>
						</div>
					</CardContent>
				</Card>

				<div className="flex gap-6">
					{showFilters && (
						<div className="hidden lg:block w-80 flex-shrink-0">
							<ScholarshipFilters
								filters={filters}
								onFiltersChange={setFilters}
							/>
						</div>
					)}

					{/* Results */}
					<div className="flex-1 min-w-0">
						{sortedScholarships.length === 0 ? (
							<Card className="text-center py-12">
								<CardContent>
									<Search className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
									<h3 className="text-lg font-semibold mb-2">
										No scholarships found
									</h3>
									<p className="text-muted-foreground mb-4 text-sm md:text-base">
										Try adjusting your search criteria or filters to find more
										opportunities.
									</p>
									<Button
										variant="outline"
										className="min-h-[44px] bg-transparent"
										onClick={() =>
											setFilters({
												countries: [],
												degreeLevel: "",
												minAmount: "",
												maxGpa: "",
												minIelts: "",
												fields: [],
												deadlineRange: "",
												onlyPassed: false,
											})
										}
									>
										Clear All Filters
									</Button>
								</CardContent>
							</Card>
						) : (
							<div className="space-y-4">
								{sortedScholarships.map((scholarship) => (
									<ScholarshipCard
										key={scholarship.id}
										scholarship={scholarship}
									/>
								))}
							</div>
						)}
					</div>
				</div>
			</div>
		</div>
	);
}
