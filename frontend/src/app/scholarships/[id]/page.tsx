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
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@/core/components/ui/tabs";
import { ApplicationTimeline } from "@/modules/scholarships/components/application-timeline";
import { DocumentsChecklist } from "@/modules/scholarships/components/documents-checklist";
import { EligibilityPanel } from "@/modules/scholarships/components/eligibility-panel";
import { RelatedScholarships } from "@/modules/scholarships/components/related-scholarships";
import {
	ArrowLeft,
	Award,
	BookmarkPlus,
	Calendar,
	CheckCircle,
	DollarSign,
	ExternalLink,
	FileText,
	MapPin,
	Users,
} from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

// Mock scholarship data - in real app this would come from API
const mockScholarshipData = {
	s1: {
		id: "s1",
		title: "University of Oxford Graduate Scholarship",
		provider: "University of Oxford",
		country: "United Kingdom",
		degreeLevel: "Master's",
		amount: "Full tuition + £15,000 stipend",
		deadline: "2024-03-15",
		applicationOpenDate: "2023-10-01",
		hardConditions: {
			minGpa: 3.5,
			minIelts: 7.0,
			requiredField: ["Computer Science", "Engineering", "Data Science"],
			allowedNationalities: ["Vietnam", "Thailand", "Malaysia", "Singapore"],
			additionalRequirements: [
				"Bachelor's degree in relevant field",
				"Minimum 2 years work experience",
				"Strong research background",
			],
		},
		softWeights: {
			gpa: 0.3,
			publication: 0.3,
			experience: 0.2,
			extracurricular: 0.2,
		},
		requiredDocuments: [
			{
				name: "CV/Resume",
				required: true,
				description: "Comprehensive academic and professional CV",
				template: true,
			},
			{
				name: "Academic Transcripts",
				required: true,
				description: "Official transcripts from all universities attended",
				template: false,
			},
			{
				name: "Personal Statement",
				required: true,
				description: "2-page statement outlining your goals and motivation",
				template: true,
			},
			{
				name: "Reference Letters",
				required: true,
				description: "2 academic references from professors or supervisors",
				template: true,
			},
			{
				name: "Research Proposal",
				required: false,
				description: "Detailed research proposal for PhD applicants",
				template: true,
			},
			{
				name: "Portfolio",
				required: false,
				description: "Portfolio of relevant work (for creative fields)",
				template: false,
			},
		],
		link: "https://oxford.edu/scholarships",
		matchScore: 85,
		hardConditionsPassed: true,
		failedConditions: [],
		description:
			"The University of Oxford Graduate Scholarship is a prestigious award designed to support outstanding international students pursuing graduate studies. This comprehensive scholarship covers full tuition fees and provides a generous living stipend, enabling recipients to focus entirely on their academic and research pursuits.",
		detailedDescription: `
      The scholarship is awarded based on academic excellence, research potential, and leadership qualities. Recipients join a vibrant community of scholars and have access to world-class facilities, renowned faculty, and extensive networking opportunities.

      The program particularly welcomes applications from students in STEM fields who demonstrate exceptional promise in research and innovation. Successful candidates typically have strong academic records, relevant research experience, and clear career goals aligned with their chosen field of study.
    `,
		benefits: [
			"Full tuition fee coverage",
			"£15,000 annual living stipend",
			"Access to college accommodation",
			"Research funding up to £2,000",
			"Mentorship program",
			"Career development workshops",
			"Alumni network access",
		],
		selectionCriteria: [
			"Academic excellence (minimum 3.5 GPA)",
			"English proficiency (IELTS 7.0 or equivalent)",
			"Research potential and experience",
			"Leadership and extracurricular activities",
			"Clear career goals and motivation",
			"Contribution to diversity and inclusion",
		],
		applicationProcess: [
			{
				step: 1,
				title: "Prepare Documents",
				description:
					"Gather all required documents including transcripts, CV, and references",
				deadline: "2024-02-01",
				status: "pending",
			},
			{
				step: 2,
				title: "Submit Online Application",
				description:
					"Complete the online application form with all supporting documents",
				deadline: "2024-03-01",
				status: "pending",
			},
			{
				step: 3,
				title: "Interview Round",
				description:
					"Selected candidates will be invited for virtual or in-person interviews",
				deadline: "2024-04-15",
				status: "pending",
			},
			{
				step: 4,
				title: "Final Decision",
				description:
					"Scholarship recipients will be notified of the final decision",
				deadline: "2024-05-01",
				status: "pending",
			},
		],
		tags: ["STEM", "Research", "Full Funding", "Prestigious"],
		contactInfo: {
			email: "scholarships@ox.ac.uk",
			phone: "+44 1865 270000",
			website:
				"https://www.ox.ac.uk/admissions/graduate/fees-and-funding/fees-funding-and-scholarship-search",
		},
		statistics: {
			totalApplicants: 2500,
			awardsAvailable: 50,
			successRate: "2%",
			averageGpa: 3.8,
		},
	},
};

export default function ScholarshipDetailPage() {
	const params = useParams();
	const scholarshipId = params.id as string;
	const scholarship =
		mockScholarshipData[scholarshipId as keyof typeof mockScholarshipData];

	const [isSaved, setIsSaved] = useState(false);
	const [activeTab, setActiveTab] = useState("overview");

	if (!scholarship) {
		return (
			<div className="min-h-screen bg-background flex items-center justify-center">
				<Card className="max-w-md">
					<CardContent className="text-center py-8">
						<h2 className="text-xl font-semibold mb-2">
							Scholarship Not Found
						</h2>
						<p className="text-muted-foreground mb-4">
							The scholarship you're looking for doesn't exist.
						</p>
						<Button asChild>
							<Link href="/scholarships">Back to Search</Link>
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

	const daysLeft = getDaysUntilDeadline(scholarship.deadline);
	const isUrgent = daysLeft <= 30;
	const isExpired = daysLeft < 0;

	return (
		<div className="min-h-screen bg-background">
			<div className="container mx-auto max-w-6xl px-4 py-8">
				{/* Back Navigation */}
				<div className="mb-6">
					<Button variant="ghost" asChild className="mb-4">
						<Link href="/scholarships" className="flex items-center">
							<ArrowLeft className="mr-2 h-4 w-4" />
							Back to Search
						</Link>
					</Button>
				</div>

				{/* Header */}
				<Card className="mb-8">
					<CardHeader>
						<div className="flex flex-col lg:flex-row justify-between items-start gap-6">
							<div className="flex-1">
								<div className="flex items-center gap-2 mb-3">
									<CardTitle className="text-2xl lg:text-3xl">
										{scholarship.title}
									</CardTitle>
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
										{scholarship.provider}
									</span>
									<span className="flex items-center gap-1">
										<MapPin className="h-4 w-4" />
										{scholarship.country}
									</span>
									<Badge variant="outline">{scholarship.degreeLevel}</Badge>
								</div>

								<div className="flex flex-wrap gap-2">
									{scholarship.tags.map((tag) => (
										<Badge key={tag} variant="secondary" className="text-xs">
											{tag}
										</Badge>
									))}
								</div>
							</div>

							{/* Match Score & Actions */}
							<div className="flex flex-col items-center gap-4">
								<div className="text-center">
									<div className="text-3xl font-bold text-green-600">
										{scholarship.matchScore}%
									</div>
									<div className="text-sm text-muted-foreground">
										Match Score
									</div>
								</div>

								<div className="flex gap-2">
									<Button
										variant={isSaved ? "default" : "outline"}
										onClick={() => setIsSaved(!isSaved)}
										className="flex items-center"
									>
										<BookmarkPlus className="mr-2 h-4 w-4" />
										{isSaved ? "Saved" : "Save"}
									</Button>
									<Button variant="outline" asChild>
										<a
											href={scholarship.link}
											target="_blank"
											rel="noopener noreferrer"
											className="flex items-center"
										>
											<ExternalLink className="mr-2 h-4 w-4" />
											Official Site
										</a>
									</Button>
								</div>
							</div>
						</div>
					</CardHeader>

					<CardContent>
						{/* Key Information */}
						<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
							<div className="flex items-center gap-3">
								<div className="p-2 bg-green-100 rounded-lg">
									<DollarSign className="h-5 w-5 text-green-600" />
								</div>
								<div>
									<div className="font-medium">Scholarship Amount</div>
									<div className="text-sm text-muted-foreground">
										{scholarship.amount}
									</div>
								</div>
							</div>

							<div className="flex items-center gap-3">
								<div className="p-2 bg-blue-100 rounded-lg">
									<Calendar className="h-5 w-5 text-blue-600" />
								</div>
								<div>
									<div className="font-medium">Application Deadline</div>
									<div
										className={`text-sm ${isUrgent && !isExpired ? "text-orange-600" : "text-muted-foreground"}`}
									>
										{new Date(scholarship.deadline).toLocaleDateString()}
										{!isExpired && (
											<span className="ml-1">({daysLeft} days left)</span>
										)}
									</div>
								</div>
							</div>

							<div className="flex items-center gap-3">
								<div className="p-2 bg-purple-100 rounded-lg">
									<Users className="h-5 w-5 text-purple-600" />
								</div>
								<div>
									<div className="font-medium">Success Rate</div>
									<div className="text-sm text-muted-foreground">
										{scholarship.statistics.successRate} (
										{scholarship.statistics.awardsAvailable} awards)
									</div>
								</div>
							</div>
						</div>

						{/* Quick Actions */}
						<div className="flex flex-col sm:flex-row gap-3">
							<Button size="lg" className="flex-1" disabled={isExpired}>
								{isExpired ? "Application Closed" : "Start Application"}
							</Button>
							<Button variant="outline" size="lg">
								Contact Provider
							</Button>
							<Button variant="outline" size="lg">
								Download Info Sheet
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
						<TabsTrigger value="eligibility">Eligibility</TabsTrigger>
						<TabsTrigger value="documents">Documents</TabsTrigger>
						<TabsTrigger value="process">Process</TabsTrigger>
						<TabsTrigger value="related">Similar</TabsTrigger>
					</TabsList>

					<TabsContent value="overview" className="space-y-6">
						<Card>
							<CardHeader>
								<CardTitle>About This Scholarship</CardTitle>
							</CardHeader>
							<CardContent className="space-y-4">
								<p className="text-muted-foreground">
									{scholarship.description}
								</p>
								<div className="whitespace-pre-line text-sm">
									{scholarship.detailedDescription}
								</div>
							</CardContent>
						</Card>

						<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
							<Card>
								<CardHeader>
									<CardTitle className="flex items-center gap-2">
										<Award className="h-5 w-5" />
										Benefits & Support
									</CardTitle>
								</CardHeader>
								<CardContent>
									<ul className="space-y-2">
										{scholarship.benefits.map((benefit, index) => (
											<li
												key={index}
												className="flex items-center gap-2 text-sm"
											>
												<CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
												{benefit}
											</li>
										))}
									</ul>
								</CardContent>
							</Card>

							<Card>
								<CardHeader>
									<CardTitle className="flex items-center gap-2">
										<FileText className="h-5 w-5" />
										Selection Criteria
									</CardTitle>
								</CardHeader>
								<CardContent>
									<ul className="space-y-2">
										{scholarship.selectionCriteria.map((criteria, index) => (
											<li
												key={index}
												className="flex items-center gap-2 text-sm"
											>
												<CheckCircle className="h-4 w-4 text-blue-600 flex-shrink-0" />
												{criteria}
											</li>
										))}
									</ul>
								</CardContent>
							</Card>
						</div>

						<Card>
							<CardHeader>
								<CardTitle>Application Statistics</CardTitle>
							</CardHeader>
							<CardContent>
								<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
									<div className="text-center">
										<div className="text-2xl font-bold text-primary">
											{scholarship.statistics.totalApplicants}
										</div>
										<div className="text-sm text-muted-foreground">
											Total Applicants
										</div>
									</div>
									<div className="text-center">
										<div className="text-2xl font-bold text-green-600">
											{scholarship.statistics.awardsAvailable}
										</div>
										<div className="text-sm text-muted-foreground">
											Awards Available
										</div>
									</div>
									<div className="text-center">
										<div className="text-2xl font-bold text-orange-600">
											{scholarship.statistics.successRate}
										</div>
										<div className="text-sm text-muted-foreground">
											Success Rate
										</div>
									</div>
									<div className="text-center">
										<div className="text-2xl font-bold text-purple-600">
											{scholarship.statistics.averageGpa}
										</div>
										<div className="text-sm text-muted-foreground">
											Average GPA
										</div>
									</div>
								</div>
							</CardContent>
						</Card>
					</TabsContent>

					<TabsContent value="eligibility">
						<EligibilityPanel scholarship={scholarship} />
					</TabsContent>

					<TabsContent value="documents">
						<DocumentsChecklist scholarship={scholarship} />
					</TabsContent>

					<TabsContent value="process">
						<ApplicationTimeline scholarship={scholarship} />
					</TabsContent>

					<TabsContent value="related">
						<RelatedScholarships currentScholarshipId={scholarship.id} />
					</TabsContent>
				</Tabs>
			</div>
		</div>
	);
}
