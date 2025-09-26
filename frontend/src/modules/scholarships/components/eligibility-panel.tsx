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
import { AlertTriangle, CheckCircle, Info, XCircle } from "lucide-react";

interface EligibilityPanelProps {
	scholarship: any;
}

// Mock user profile for eligibility checking
const mockUserProfile = {
	gpa: 3.4,
	gpaScale: 4.0,
	ielts: 7.0,
	nationality: "Vietnam",
	field: "Computer Science",
	experience: 2,
	publications: 1,
	extracurriculars: 3,
};

export function EligibilityPanel({ scholarship }: EligibilityPanelProps) {
	const checkEligibility = () => {
		const results = [];

		// GPA Check
		const gpaCheck = {
			requirement: `Minimum GPA: ${scholarship.hardConditions.minGpa}`,
			userValue: `Your GPA: ${mockUserProfile.gpa}/${mockUserProfile.gpaScale}`,
			passed: mockUserProfile.gpa >= scholarship.hardConditions.minGpa,
			type: "hard",
		};
		results.push(gpaCheck);

		// IELTS Check
		const ieltsCheck = {
			requirement: `Minimum IELTS: ${scholarship.hardConditions.minIelts}`,
			userValue: `Your IELTS: ${mockUserProfile.ielts}`,
			passed: mockUserProfile.ielts >= scholarship.hardConditions.minIelts,
			type: "hard",
		};
		results.push(ieltsCheck);

		// Nationality Check
		const nationalityCheck = {
			requirement: `Allowed Nationalities: ${scholarship.hardConditions.allowedNationalities.join(", ")}`,
			userValue: `Your Nationality: ${mockUserProfile.nationality}`,
			passed: scholarship.hardConditions.allowedNationalities.includes(
				mockUserProfile.nationality,
			),
			type: "hard",
		};
		results.push(nationalityCheck);

		// Field Check
		const fieldCheck = {
			requirement: `Required Fields: ${scholarship.hardConditions.requiredField.join(", ")}`,
			userValue: `Your Field: ${mockUserProfile.field}`,
			passed: scholarship.hardConditions.requiredField.includes(
				mockUserProfile.field,
			),
			type: "hard",
		};
		results.push(fieldCheck);

		return results;
	};

	const eligibilityResults = checkEligibility();
	const hardRequirementsPassed = eligibilityResults
		.filter((r) => r.type === "hard")
		.every((r) => r.passed);
	const passedCount = eligibilityResults.filter((r) => r.passed).length;
	const totalCount = eligibilityResults.length;

	const getSoftScoreBreakdown = () => {
		const weights = scholarship.softWeights;
		const scores = {
			gpa: Math.min((mockUserProfile.gpa / 4.0) * 100, 100),
			publication: Math.min(mockUserProfile.publications * 25, 100),
			experience: Math.min(mockUserProfile.experience * 20, 100),
			extracurricular: Math.min(mockUserProfile.extracurriculars * 15, 100),
		};

		const weightedScores = {
			gpa: scores.gpa * weights.gpa,
			publication: scores.publication * weights.publication,
			experience: scores.experience * weights.experience,
			extracurricular: scores.extracurricular * weights.extracurricular,
		};

		const totalScore = Object.values(weightedScores).reduce(
			(sum, score) => sum + score,
			0,
		);

		return {
			scores,
			weightedScores,
			totalScore,
			breakdown: [
				{
					name: "GPA",
					score: scores.gpa,
					weight: weights.gpa,
					weighted: weightedScores.gpa,
				},
				{
					name: "Publications",
					score: scores.publication,
					weight: weights.publication,
					weighted: weightedScores.publication,
				},
				{
					name: "Experience",
					score: scores.experience,
					weight: weights.experience,
					weighted: weightedScores.experience,
				},
				{
					name: "Extracurriculars",
					score: scores.extracurricular,
					weight: weights.extracurricular,
					weighted: weightedScores.extracurricular,
				},
			],
		};
	};

	const softScoreData = getSoftScoreBreakdown();

	return (
		<div className="space-y-6">
			{/* Hard Requirements */}
			<Card>
				<CardHeader>
					<div className="flex items-center justify-between">
						<div>
							<CardTitle className="flex items-center gap-2">
								{hardRequirementsPassed ? (
									<CheckCircle className="h-5 w-5 text-green-600" />
								) : (
									<XCircle className="h-5 w-5 text-red-600" />
								)}
								Hard Requirements
							</CardTitle>
							<CardDescription>
								Mandatory criteria that must be met to be eligible
							</CardDescription>
						</div>
						<Badge variant={hardRequirementsPassed ? "default" : "destructive"}>
							{passedCount}/{totalCount} Met
						</Badge>
					</div>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="space-y-3">
						{eligibilityResults.map((result, index) => (
							<div
								key={index}
								className="flex items-center justify-between p-3 rounded-lg border"
							>
								<div className="flex items-center gap-3">
									{result.passed ? (
										<CheckCircle className="h-5 w-5 text-green-600" />
									) : (
										<XCircle className="h-5 w-5 text-red-600" />
									)}
									<div>
										<div className="font-medium text-sm">
											{result.requirement}
										</div>
										<div
											className={`text-xs ${result.passed ? "text-green-600" : "text-red-600"}`}
										>
											{result.userValue}
										</div>
									</div>
								</div>
								<Badge variant={result.passed ? "default" : "destructive"}>
									{result.passed ? "Pass" : "Fail"}
								</Badge>
							</div>
						))}
					</div>

					{scholarship.hardConditions.additionalRequirements && (
						<div className="mt-4">
							<h4 className="font-medium text-sm mb-2">
								Additional Requirements:
							</h4>
							<ul className="space-y-1">
								{scholarship.hardConditions.additionalRequirements.map(
									(req: string, index: number) => (
										<li
											key={index}
											className="flex items-center gap-2 text-sm text-muted-foreground"
										>
											<AlertTriangle className="h-3 w-3" />
											{req}
										</li>
									),
								)}
							</ul>
						</div>
					)}
				</CardContent>
			</Card>

			{/* Soft Score Analysis */}
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<Info className="h-5 w-5 text-blue-600" />
						Competitive Score Analysis
					</CardTitle>
					<CardDescription>
						How your profile compares for this scholarship's soft criteria
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-6">
					<div className="text-center">
						<div className="text-3xl font-bold text-primary mb-2">
							{Math.round(softScoreData.totalScore)}%
						</div>
						<div className="text-sm text-muted-foreground">
							Overall Competitive Score
						</div>
						<Progress value={softScoreData.totalScore} className="mt-2" />
					</div>

					<div className="space-y-4">
						<h4 className="font-medium">Score Breakdown:</h4>
						{softScoreData.breakdown.map((item, index) => (
							<div key={index} className="space-y-2">
								<div className="flex justify-between items-center">
									<span className="text-sm font-medium">{item.name}</span>
									<div className="flex items-center gap-2">
										<span className="text-sm text-muted-foreground">
											Weight: {Math.round(item.weight * 100)}%
										</span>
										<Popover>
											<PopoverTrigger asChild>
												<Button
													variant="ghost"
													size="sm"
													className="h-6 w-6 p-0"
												>
													<Info className="h-3 w-3" />
												</Button>
											</PopoverTrigger>
											<PopoverContent className="w-64" align="end">
												<div className="space-y-2 text-sm">
													<div>Raw Score: {Math.round(item.score)}%</div>
													<div>Weight: {Math.round(item.weight * 100)}%</div>
													<div>
														Weighted Score: {Math.round(item.weighted)}%
													</div>
												</div>
											</PopoverContent>
										</Popover>
									</div>
								</div>
								<div className="flex items-center gap-2">
									<Progress value={item.score} className="flex-1 h-2" />
									<span className="text-sm font-medium w-12 text-right">
										{Math.round(item.score)}%
									</span>
								</div>
							</div>
						))}
					</div>

					<div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
						<div className="flex items-start gap-3">
							<Info className="h-5 w-5 text-blue-600 mt-0.5" />
							<div className="text-sm text-blue-800">
								<p className="font-medium mb-1">How to Improve Your Score:</p>
								<ul className="space-y-1 text-xs">
									{softScoreData.breakdown
										.filter((item) => item.score < 80)
										.map((item, index) => (
											<li key={index}>
												• Strengthen your {item.name.toLowerCase()} to boost
												your competitive advantage
											</li>
										))}
								</ul>
							</div>
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Recommendations */}
			<Card>
				<CardHeader>
					<CardTitle>Recommendations</CardTitle>
				</CardHeader>
				<CardContent>
					{hardRequirementsPassed ? (
						<div className="space-y-3">
							<div className="flex items-center gap-2 text-green-600">
								<CheckCircle className="h-5 w-5" />
								<span className="font-medium">
									You meet all hard requirements!
								</span>
							</div>
							<p className="text-sm text-muted-foreground">
								Focus on strengthening your soft criteria to improve your
								competitive position. Consider highlighting your unique
								experiences and achievements in your application.
							</p>
						</div>
					) : (
						<div className="space-y-3">
							<div className="flex items-center gap-2 text-red-600">
								<XCircle className="h-5 w-5" />
								<span className="font-medium">
									You don't meet all hard requirements
								</span>
							</div>
							<p className="text-sm text-muted-foreground">
								Work on meeting the failed requirements before applying.
								Consider retaking tests or gaining additional experience as
								needed.
							</p>
						</div>
					)}
				</CardContent>
			</Card>
		</div>
	);
}
