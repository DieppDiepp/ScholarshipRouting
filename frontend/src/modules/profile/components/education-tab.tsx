"use client";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Input } from "@/core/components/ui/input";
import { Label } from "@/core/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import { Plus, Trash2 } from "lucide-react";
import { useState } from "react";

interface EducationTabProps {
	isEditMode: boolean;
}

interface Education {
	id: string;
	institution: string;
	degree: string;
	major: string;
	gpa: string;
	gpaScale: string;
	startDate: string;
	endDate: string;
	status: "completed" | "in-progress" | "planned";
}

const gpaScales = ["4.0", "10.0", "100"];
const degreeTypes = [
	"Bachelor's",
	"Master's",
	"PhD",
	"Professional",
	"Diploma",
	"Certificate",
];

export function EducationTab({ isEditMode }: EducationTabProps) {
	const [educations, setEducations] = useState<Education[]>([
		{
			id: "1",
			institution: "University of Technology",
			degree: "Bachelor's",
			major: "Computer Science",
			gpa: "3.4",
			gpaScale: "4.0",
			startDate: "2018-09",
			endDate: "2022-06",
			status: "completed",
		},
		{
			id: "2",
			institution: "National University",
			degree: "Master's",
			major: "Data Science",
			gpa: "3.7",
			gpaScale: "4.0",
			startDate: "2022-09",
			endDate: "2024-06",
			status: "in-progress",
		},
	]);

	const addEducation = () => {
		const newEducation: Education = {
			id: Date.now().toString(),
			institution: "",
			degree: "",
			major: "",
			gpa: "",
			gpaScale: "4.0",
			startDate: "",
			endDate: "",
			status: "planned",
		};
		setEducations([...educations, newEducation]);
	};

	const removeEducation = (id: string) => {
		setEducations(educations.filter((edu) => edu.id !== id));
	};

	const updateEducation = (
		id: string,
		field: keyof Education,
		value: string,
	) => {
		setEducations(
			educations.map((edu) =>
				edu.id === id ? { ...edu, [field]: value } : edu,
			),
		);
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case "completed":
				return "default";
			case "in-progress":
				return "secondary";
			case "planned":
				return "outline";
			default:
				return "outline";
		}
	};

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h3 className="text-lg font-semibold">Education History</h3>
					<p className="text-sm text-muted-foreground">
						Your academic background and qualifications
					</p>
				</div>
				{isEditMode && (
					<Button
						onClick={addEducation}
						size="sm"
						className="flex items-center"
					>
						<Plus className="mr-2 h-4 w-4" />
						Add Education
					</Button>
				)}
			</div>

			<div className="space-y-4">
				{educations.map((education) => (
					<Card key={education.id}>
						<CardHeader className="pb-3">
							<div className="flex justify-between items-start">
								<div className="flex items-center space-x-2">
									<CardTitle className="text-base">
										{education.institution || "New Institution"}
									</CardTitle>
									<Badge variant={getStatusColor(education.status)}>
										{education.status.replace("-", " ")}
									</Badge>
								</div>
								{isEditMode && (
									<Button
										variant="ghost"
										size="sm"
										onClick={() => removeEducation(education.id)}
										className="text-destructive hover:text-destructive"
									>
										<Trash2 className="h-4 w-4" />
									</Button>
								)}
							</div>
						</CardHeader>
						<CardContent className="space-y-4">
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div className="space-y-2">
									<Label>Institution</Label>
									{isEditMode ? (
										<Input
											value={education.institution}
											onChange={(e) =>
												updateEducation(
													education.id,
													"institution",
													e.target.value,
												)
											}
											placeholder="University name"
										/>
									) : (
										<div className="p-2 text-sm">{education.institution}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Degree Type</Label>
									{isEditMode ? (
										<Select
											value={education.degree}
											onValueChange={(value) =>
												updateEducation(education.id, "degree", value)
											}
										>
											<SelectTrigger>
												<SelectValue placeholder="Select degree" />
											</SelectTrigger>
											<SelectContent>
												{degreeTypes.map((degree) => (
													<SelectItem key={degree} value={degree}>
														{degree}
													</SelectItem>
												))}
											</SelectContent>
										</Select>
									) : (
										<div className="p-2 text-sm">{education.degree}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Major / Field of Study</Label>
									{isEditMode ? (
										<Input
											value={education.major}
											onChange={(e) =>
												updateEducation(education.id, "major", e.target.value)
											}
											placeholder="Computer Science"
										/>
									) : (
										<div className="p-2 text-sm">{education.major}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Status</Label>
									{isEditMode ? (
										<Select
											value={education.status}
											onValueChange={(value) =>
												updateEducation(
													education.id,
													"status",
													value as Education["status"],
												)
											}
										>
											<SelectTrigger>
												<SelectValue />
											</SelectTrigger>
											<SelectContent>
												<SelectItem value="completed">Completed</SelectItem>
												<SelectItem value="in-progress">In Progress</SelectItem>
												<SelectItem value="planned">Planned</SelectItem>
											</SelectContent>
										</Select>
									) : (
										<div className="p-2 text-sm capitalize">
											{education.status.replace("-", " ")}
										</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>GPA</Label>
									{isEditMode ? (
										<div className="flex space-x-2">
											<Input
												value={education.gpa}
												onChange={(e) =>
													updateEducation(education.id, "gpa", e.target.value)
												}
												placeholder="3.50"
												className="flex-1"
											/>
											<Select
												value={education.gpaScale}
												onValueChange={(value) =>
													updateEducation(education.id, "gpaScale", value)
												}
											>
												<SelectTrigger className="w-20">
													<SelectValue />
												</SelectTrigger>
												<SelectContent>
													{gpaScales.map((scale) => (
														<SelectItem key={scale} value={scale}>
															{scale}
														</SelectItem>
													))}
												</SelectContent>
											</Select>
										</div>
									) : (
										<div className="p-2 text-sm">
											{education.gpa} / {education.gpaScale}
										</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Duration</Label>
									{isEditMode ? (
										<div className="flex space-x-2">
											<Input
												type="month"
												value={education.startDate}
												onChange={(e) =>
													updateEducation(
														education.id,
														"startDate",
														e.target.value,
													)
												}
												className="flex-1"
											/>
											<Input
												type="month"
												value={education.endDate}
												onChange={(e) =>
													updateEducation(
														education.id,
														"endDate",
														e.target.value,
													)
												}
												className="flex-1"
											/>
										</div>
									) : (
										<div className="p-2 text-sm">
											{education.startDate} - {education.endDate || "Present"}
										</div>
									)}
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</div>
		</div>
	);
}
