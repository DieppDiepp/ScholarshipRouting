"use client";

import type React from "react";

import type { OnboardingData } from "@/app/onboarding/page";
import { Button } from "@/core/components/ui/button";
import { Input } from "@/core/components/ui/input";
import { Label } from "@/core/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import { FileText, Upload } from "lucide-react";

interface AcademicStepProps {
	data: OnboardingData;
	updateData: (data: Partial<OnboardingData>) => void;
}

const gpaScales = ["4.0", "10.0", "100"];

const majors = [
	"Computer Science",
	"Data Science",
	"Engineering",
	"Business Administration",
	"Economics",
	"Medicine",
	"Law",
	"Psychology",
	"Biology",
	"Chemistry",
	"Physics",
	"Mathematics",
	"Literature",
	"History",
	"Art",
	"Other",
];

export function AcademicStep({ data, updateData }: AcademicStepProps) {
	const handleTranscriptUpload = (
		event: React.ChangeEvent<HTMLInputElement>,
	) => {
		const file = event.target.files?.[0];
		if (file) {
			updateData({ transcriptFile: file });
		}
	};

	return (
		<div className="space-y-6">
			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div className="space-y-2">
					<Label htmlFor="gpa">GPA *</Label>
					<Input
						id="gpa"
						type="number"
						step="0.01"
						placeholder="3.50"
						value={data.gpa}
						onChange={(e) => updateData({ gpa: e.target.value })}
					/>
				</div>

				<div className="space-y-2">
					<Label htmlFor="gpaScale">GPA Scale *</Label>
					<Select
						value={data.gpaScale}
						onValueChange={(value) => updateData({ gpaScale: value })}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select GPA scale" />
						</SelectTrigger>
						<SelectContent>
							{gpaScales.map((scale) => (
								<SelectItem key={scale} value={scale}>
									{scale} Scale
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>

				<div className="space-y-2 md:col-span-2">
					<Label htmlFor="major">Field of Study / Major *</Label>
					<Select
						value={data.major}
						onValueChange={(value) => updateData({ major: value })}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select your field of study" />
						</SelectTrigger>
						<SelectContent>
							{majors.map((major) => (
								<SelectItem key={major} value={major}>
									{major}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>
			</div>

			<div className="space-y-4">
				<Label>Transcript Upload (Optional)</Label>
				<div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-6">
					<div className="text-center">
						<Upload className="mx-auto h-12 w-12 text-muted-foreground/50" />
						<div className="mt-4">
							<Button variant="outline" asChild>
								<label htmlFor="transcript-upload" className="cursor-pointer">
									<FileText className="mr-2 h-4 w-4" />
									Upload Transcript
								</label>
							</Button>
							<input
								id="transcript-upload"
								type="file"
								accept=".pdf,.doc,.docx"
								onChange={handleTranscriptUpload}
								className="hidden"
							/>
						</div>
						<p className="mt-2 text-sm text-muted-foreground">
							PDF, DOC, or DOCX files up to 10MB
						</p>
						{data.transcriptFile && (
							<p className="mt-2 text-sm text-green-600">
								✓ {data.transcriptFile.name} uploaded
							</p>
						)}
					</div>
				</div>
			</div>

			<div className="text-sm text-muted-foreground">
				Your GPA will be used to filter scholarships with minimum GPA
				requirements.
			</div>
		</div>
	);
}
