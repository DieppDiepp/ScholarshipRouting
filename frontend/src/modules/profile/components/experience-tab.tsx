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
import { Textarea } from "@/core/components/ui/textarea";
import { Briefcase, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

interface ExperienceTabProps {
	isEditMode: boolean;
}

interface Experience {
	id: string;
	role: string;
	company: string;
	type: "internship" | "full-time" | "part-time" | "volunteer" | "research";
	startDate: string;
	endDate: string;
	current: boolean;
	description: string;
	skills: string[];
}

export function ExperienceTab({ isEditMode }: ExperienceTabProps) {
	const [experiences, setExperiences] = useState<Experience[]>([
		{
			id: "1",
			role: "Machine Learning Intern",
			company: "Tech Startup Inc.",
			type: "internship",
			startDate: "2023-06",
			endDate: "2023-08",
			current: false,
			description:
				"Developed ML models for customer behavior prediction using Python and TensorFlow. Improved model accuracy by 15% through feature engineering and hyperparameter tuning.",
			skills: ["Python", "TensorFlow", "Machine Learning", "Data Analysis"],
		},
		{
			id: "2",
			role: "Research Assistant",
			company: "University AI Lab",
			type: "research",
			startDate: "2023-01",
			endDate: "",
			current: true,
			description:
				"Conducting research on natural language processing and deep learning. Published 2 papers in international conferences.",
			skills: ["NLP", "Deep Learning", "PyTorch", "Research"],
		},
	]);

	const addExperience = () => {
		const newExperience: Experience = {
			id: Date.now().toString(),
			role: "",
			company: "",
			type: "internship",
			startDate: "",
			endDate: "",
			current: false,
			description: "",
			skills: [],
		};
		setExperiences([...experiences, newExperience]);
	};

	const removeExperience = (id: string) => {
		setExperiences(experiences.filter((exp) => exp.id !== id));
	};

	const updateExperience = (
		id: string,
		field: keyof Experience,
		value: any,
	) => {
		setExperiences(
			experiences.map((exp) =>
				exp.id === id ? { ...exp, [field]: value } : exp,
			),
		);
	};

	const getTypeColor = (type: string) => {
		switch (type) {
			case "full-time":
				return "default";
			case "internship":
				return "secondary";
			case "research":
				return "outline";
			case "volunteer":
				return "outline";
			default:
				return "outline";
		}
	};

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h3 className="text-lg font-semibold">Work Experience</h3>
					<p className="text-sm text-muted-foreground">
						Your professional and research experience
					</p>
				</div>
				{isEditMode && (
					<Button
						onClick={addExperience}
						size="sm"
						className="flex items-center"
					>
						<Plus className="mr-2 h-4 w-4" />
						Add Experience
					</Button>
				)}
			</div>

			<div className="space-y-4">
				{experiences.map((experience) => (
					<Card key={experience.id}>
						<CardHeader className="pb-3">
							<div className="flex justify-between items-start">
								<div className="flex items-center space-x-2">
									<Briefcase className="h-5 w-5 text-muted-foreground" />
									<div>
										<CardTitle className="text-base">
											{experience.role || "New Position"}
										</CardTitle>
										<p className="text-sm text-muted-foreground">
											{experience.company}
										</p>
									</div>
								</div>
								<div className="flex items-center space-x-2">
									<Badge variant={getTypeColor(experience.type)}>
										{experience.type.replace("-", " ")}
									</Badge>
									{isEditMode && (
										<Button
											variant="ghost"
											size="sm"
											onClick={() => removeExperience(experience.id)}
											className="text-destructive hover:text-destructive"
										>
											<Trash2 className="h-4 w-4" />
										</Button>
									)}
								</div>
							</div>
						</CardHeader>
						<CardContent className="space-y-4">
							<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
								<div className="space-y-2">
									<Label>Job Title</Label>
									{isEditMode ? (
										<Input
											value={experience.role}
											onChange={(e) =>
												updateExperience(experience.id, "role", e.target.value)
											}
											placeholder="Software Engineer"
										/>
									) : (
										<div className="p-2 text-sm">{experience.role}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Company/Organization</Label>
									{isEditMode ? (
										<Input
											value={experience.company}
											onChange={(e) =>
												updateExperience(
													experience.id,
													"company",
													e.target.value,
												)
											}
											placeholder="Company name"
										/>
									) : (
										<div className="p-2 text-sm">{experience.company}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Type</Label>
									{isEditMode ? (
										<select
											value={experience.type}
											onChange={(e) =>
												updateExperience(experience.id, "type", e.target.value)
											}
											className="w-full p-2 border rounded-md"
										>
											<option value="internship">Internship</option>
											<option value="full-time">Full-time</option>
											<option value="part-time">Part-time</option>
											<option value="volunteer">Volunteer</option>
											<option value="research">Research</option>
										</select>
									) : (
										<div className="p-2 text-sm capitalize">
											{experience.type.replace("-", " ")}
										</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Duration</Label>
									{isEditMode ? (
										<div className="space-y-2">
											<div className="flex space-x-2">
												<Input
													type="month"
													value={experience.startDate}
													onChange={(e) =>
														updateExperience(
															experience.id,
															"startDate",
															e.target.value,
														)
													}
													className="flex-1"
												/>
												<Input
													type="month"
													value={experience.endDate}
													onChange={(e) =>
														updateExperience(
															experience.id,
															"endDate",
															e.target.value,
														)
													}
													className="flex-1"
													disabled={experience.current}
												/>
											</div>
											<label className="flex items-center space-x-2 text-sm">
												<input
													type="checkbox"
													checked={experience.current}
													onChange={(e) =>
														updateExperience(
															experience.id,
															"current",
															e.target.checked,
														)
													}
												/>
												<span>Currently working here</span>
											</label>
										</div>
									) : (
										<div className="p-2 text-sm">
											{experience.startDate} -{" "}
											{experience.current ? "Present" : experience.endDate}
										</div>
									)}
								</div>
							</div>

							<div className="space-y-2">
								<Label>Description</Label>
								{isEditMode ? (
									<Textarea
										value={experience.description}
										onChange={(e) =>
											updateExperience(
												experience.id,
												"description",
												e.target.value,
											)
										}
										placeholder="Describe your responsibilities and achievements..."
										rows={3}
									/>
								) : (
									<div className="p-2 text-sm">{experience.description}</div>
								)}
							</div>

							<div className="space-y-2">
								<Label>Skills</Label>
								<div className="flex flex-wrap gap-2">
									{experience.skills.map((skill, index) => (
										<Badge key={index} variant="secondary">
											{skill}
										</Badge>
									))}
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</div>
		</div>
	);
}
