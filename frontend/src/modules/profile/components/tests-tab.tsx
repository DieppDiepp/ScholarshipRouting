"use client";

import { Badge } from "@/core/components/ui/badge";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Input } from "@/core/components/ui/input";
import { Label } from "@/core/components/ui/label";
import { Progress } from "@/core/components/ui/progress";
import { useState } from "react";

interface TestsTabProps {
	isEditMode: boolean;
}

interface TestScore {
	type: string;
	score: string;
	maxScore: number;
	date: string;
	status: "valid" | "expired" | "pending";
}

export function TestsTab({ isEditMode }: TestsTabProps) {
	const [testScores, setTestScores] = useState<TestScore[]>([
		{
			type: "IELTS",
			score: "7.0",
			maxScore: 9,
			date: "2023-08-15",
			status: "valid",
		},
		{
			type: "TOEFL iBT",
			score: "",
			maxScore: 120,
			date: "",
			status: "pending",
		},
		{
			type: "GRE",
			score: "320",
			maxScore: 340,
			date: "2023-06-20",
			status: "valid",
		},
		{
			type: "GMAT",
			score: "",
			maxScore: 800,
			date: "",
			status: "pending",
		},
	]);

	const updateTestScore = (
		index: number,
		field: keyof TestScore,
		value: string,
	) => {
		const updated = [...testScores];
		updated[index] = { ...updated[index], [field]: value };
		setTestScores(updated);
	};

	const getScorePercentage = (score: string, maxScore: number) => {
		const numScore = Number.parseFloat(score);
		return isNaN(numScore) ? 0 : (numScore / maxScore) * 100;
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case "valid":
				return "default";
			case "expired":
				return "destructive";
			case "pending":
				return "outline";
			default:
				return "outline";
		}
	};

	const getScoreColor = (percentage: number) => {
		if (percentage >= 80) return "text-green-600";
		if (percentage >= 60) return "text-yellow-600";
		return "text-red-600";
	};

	return (
		<div className="space-y-6">
			<div>
				<h3 className="text-lg font-semibold">Test Scores</h3>
				<p className="text-sm text-muted-foreground">
					Your standardized test results for scholarship applications
				</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				{testScores.map((test, index) => (
					<Card key={test.type}>
						<CardHeader className="pb-3">
							<div className="flex justify-between items-center">
								<CardTitle className="text-base">{test.type}</CardTitle>
								<Badge variant={getStatusColor(test.status)}>
									{test.status}
								</Badge>
							</div>
							{test.type === "IELTS" && (
								<CardDescription>
									International English Language Testing System
								</CardDescription>
							)}
							{test.type === "TOEFL iBT" && (
								<CardDescription>
									Test of English as a Foreign Language
								</CardDescription>
							)}
							{test.type === "GRE" && (
								<CardDescription>Graduate Record Examination</CardDescription>
							)}
							{test.type === "GMAT" && (
								<CardDescription>
									Graduate Management Admission Test
								</CardDescription>
							)}
						</CardHeader>
						<CardContent className="space-y-4">
							<div className="space-y-2">
								<Label>Score</Label>
								{isEditMode ? (
									<Input
										type="number"
										value={test.score}
										onChange={(e) =>
											updateTestScore(index, "score", e.target.value)
										}
										placeholder={`Max: ${test.maxScore}`}
										step={test.type === "IELTS" ? "0.5" : "1"}
									/>
								) : (
									<div className="flex items-center space-x-2">
										<span
											className={`text-lg font-semibold ${getScoreColor(getScorePercentage(test.score, test.maxScore))}`}
										>
											{test.score || "Not taken"}
										</span>
										{test.score && (
											<span className="text-sm text-muted-foreground">
												/ {test.maxScore}
											</span>
										)}
									</div>
								)}
							</div>

							{test.score && (
								<div className="space-y-2">
									<div className="flex justify-between text-sm">
										<span>Performance</span>
										<span>
											{Math.round(
												getScorePercentage(test.score, test.maxScore),
											)}
											%
										</span>
									</div>
									<Progress
										value={getScorePercentage(test.score, test.maxScore)}
										className="h-2"
									/>
								</div>
							)}

							<div className="space-y-2">
								<Label>Test Date</Label>
								{isEditMode ? (
									<Input
										type="date"
										value={test.date}
										onChange={(e) =>
											updateTestScore(index, "date", e.target.value)
										}
									/>
								) : (
									<div className="p-2 text-sm">
										{test.date
											? new Date(test.date).toLocaleDateString()
											: "Not scheduled"}
									</div>
								)}
							</div>

							{test.date && (
								<div className="text-xs text-muted-foreground">
									{test.type === "IELTS" || test.type === "TOEFL iBT"
										? "Valid for 2 years from test date"
										: "Valid for 5 years from test date"}
								</div>
							)}
						</CardContent>
					</Card>
				))}
			</div>

			<Card className="bg-blue-50 border-blue-200">
				<CardContent className="pt-6">
					<div className="flex items-start space-x-3">
						<div className="text-blue-600 text-sm">💡</div>
						<div className="text-sm text-blue-800">
							<p className="font-medium mb-1">Test Score Tips:</p>
							<ul className="space-y-1 text-xs">
								<li>
									• IELTS/TOEFL scores are required for most international
									scholarships
								</li>
								<li>
									• GRE is often required for graduate programs in STEM fields
								</li>
								<li>
									• GMAT is typically required for business school applications
								</li>
								<li>
									• Higher scores increase your scholarship matching
									opportunities
								</li>
							</ul>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
