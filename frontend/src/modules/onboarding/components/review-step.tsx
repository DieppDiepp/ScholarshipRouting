"use client";

import type React from "react";

import type { OnboardingData } from "@/app/onboarding/page";
import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Edit, FileText, Upload } from "lucide-react";

interface ReviewStepProps {
	data: OnboardingData;
	updateData: (data: Partial<OnboardingData>) => void;
}

export function ReviewStep({ data, updateData }: ReviewStepProps) {
	const handleCVUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
		const file = event.target.files?.[0];
		if (file) {
			updateData({ cvFile: file });
		}
	};

	return (
		<div className="space-y-6">
			<div className="text-center mb-6">
				<h3 className="text-lg font-semibold mb-2">Review Your Information</h3>
				<p className="text-muted-foreground">
					Please review your details before completing the setup. You can edit
					any section later.
				</p>
			</div>

			{/* Basic Information */}
			<Card>
				<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
					<div>
						<CardTitle className="text-base">Basic Information</CardTitle>
						<CardDescription>
							Personal details and education level
						</CardDescription>
					</div>
					<Button variant="ghost" size="sm">
						<Edit className="h-4 w-4" />
					</Button>
				</CardHeader>
				<CardContent className="space-y-2">
					<div className="grid grid-cols-2 gap-4 text-sm">
						<div>
							<span className="font-medium">Name:</span> {data.name}
						</div>
						<div>
							<span className="font-medium">Email:</span> {data.email}
						</div>
						<div>
							<span className="font-medium">Nationality:</span>{" "}
							{data.nationality}
						</div>
						<div>
							<span className="font-medium">Current Level:</span>{" "}
							{data.currentLevel}
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Academic Information */}
			<Card>
				<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
					<div>
						<CardTitle className="text-base">Academic Background</CardTitle>
						<CardDescription>GPA and field of study</CardDescription>
					</div>
					<Button variant="ghost" size="sm">
						<Edit className="h-4 w-4" />
					</Button>
				</CardHeader>
				<CardContent className="space-y-2">
					<div className="grid grid-cols-2 gap-4 text-sm">
						<div>
							<span className="font-medium">GPA:</span> {data.gpa} /{" "}
							{data.gpaScale}
						</div>
						<div>
							<span className="font-medium">Major:</span> {data.major}
						</div>
					</div>
					{data.transcriptFile && (
						<div className="text-sm">
							<span className="font-medium">Transcript:</span>{" "}
							{data.transcriptFile.name}
						</div>
					)}
				</CardContent>
			</Card>

			{/* Test Scores */}
			<Card>
				<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
					<div>
						<CardTitle className="text-base">Test Scores</CardTitle>
						<CardDescription>
							Language and standardized test results
						</CardDescription>
					</div>
					<Button variant="ghost" size="sm">
						<Edit className="h-4 w-4" />
					</Button>
				</CardHeader>
				<CardContent className="space-y-2">
					<div className="flex flex-wrap gap-2">
						{data.ieltsScore && (
							<Badge variant="secondary">IELTS: {data.ieltsScore}</Badge>
						)}
						{data.toeflScore && (
							<Badge variant="secondary">TOEFL: {data.toeflScore}</Badge>
						)}
						{data.greScore && (
							<Badge variant="outline">GRE: {data.greScore}</Badge>
						)}
						{data.gmatScore && (
							<Badge variant="outline">GMAT: {data.gmatScore}</Badge>
						)}
					</div>
				</CardContent>
			</Card>

			{/* Preferences */}
			<Card>
				<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
					<div>
						<CardTitle className="text-base">Study Preferences</CardTitle>
						<CardDescription>
							Desired destinations and degree type
						</CardDescription>
					</div>
					<Button variant="ghost" size="sm">
						<Edit className="h-4 w-4" />
					</Button>
				</CardHeader>
				<CardContent className="space-y-3">
					<div>
						<span className="font-medium text-sm">Countries:</span>
						<div className="flex flex-wrap gap-1 mt-1">
							{data.desiredCountries.map((country) => (
								<Badge key={country} variant="outline" className="text-xs">
									{country}
								</Badge>
							))}
						</div>
					</div>
					<div className="grid grid-cols-2 gap-4 text-sm">
						<div>
							<span className="font-medium">Degree:</span> {data.desiredDegree}
						</div>
						<div>
							<span className="font-medium">Coverage:</span>{" "}
							{data.scholarshipAmount}
						</div>
					</div>
				</CardContent>
			</Card>

			{/* CV Upload */}
			<Card>
				<CardHeader>
					<CardTitle className="text-base">CV Upload (Optional)</CardTitle>
					<CardDescription>
						Upload your CV for better profile matching
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6">
						<div className="text-center">
							<Upload className="mx-auto h-8 w-8 text-muted-foreground/50" />
							<div className="mt-4">
								<Button variant="outline" asChild>
									<label htmlFor="cv-upload" className="cursor-pointer">
										<FileText className="mr-2 h-4 w-4" />
										{data.cvFile ? "Replace CV" : "Upload CV"}
									</label>
								</Button>
								<input
									id="cv-upload"
									type="file"
									accept=".pdf,.doc,.docx"
									onChange={handleCVUpload}
									className="hidden"
								/>
							</div>
							<p className="mt-2 text-sm text-muted-foreground">
								PDF, DOC, or DOCX files up to 10MB
							</p>
							{data.cvFile && (
								<p className="mt-2 text-sm text-green-600">
									✓ {data.cvFile.name} uploaded
								</p>
							)}
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
