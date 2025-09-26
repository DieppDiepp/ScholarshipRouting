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
import { Award, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

interface ExtracurricularsTabProps {
	isEditMode: boolean;
}

interface Activity {
	id: string;
	title: string;
	organization: string;
	role: string;
	type:
		| "volunteer"
		| "leadership"
		| "competition"
		| "club"
		| "sports"
		| "arts"
		| "community";
	startDate: string;
	endDate: string;
	current: boolean;
	description: string;
	achievements: string[];
}

export function ExtracurricularsTab({ isEditMode }: ExtracurricularsTabProps) {
	const [activities, setActivities] = useState<Activity[]>([
		{
			id: "1",
			title: "Volunteer Teaching Program",
			organization: "Local Community Center",
			role: "Math Tutor",
			type: "volunteer",
			startDate: "2022-09",
			endDate: "2023-06",
			current: false,
			description:
				"Provided free math tutoring to underprivileged high school students, helping improve their academic performance and college readiness.",
			achievements: [
				"Tutored 25+ students",
				"Improved average test scores by 30%",
				"Organized study groups",
			],
		},
		{
			id: "2",
			title: "Student Government Association",
			organization: "University",
			role: "Vice President",
			type: "leadership",
			startDate: "2023-01",
			endDate: "",
			current: true,
			description:
				"Leading student initiatives and representing student interests in university policy discussions.",
			achievements: [
				"Led 3 major campus initiatives",
				"Increased student engagement by 40%",
			],
		},
	]);

	const addActivity = () => {
		const newActivity: Activity = {
			id: Date.now().toString(),
			title: "",
			organization: "",
			role: "",
			type: "volunteer",
			startDate: "",
			endDate: "",
			current: false,
			description: "",
			achievements: [],
		};
		setActivities([...activities, newActivity]);
	};

	const removeActivity = (id: string) => {
		setActivities(activities.filter((activity) => activity.id !== id));
	};

	const updateActivity = (id: string, field: keyof Activity, value: any) => {
		setActivities(
			activities.map((activity) =>
				activity.id === id ? { ...activity, [field]: value } : activity,
			),
		);
	};

	const getTypeColor = (type: string) => {
		switch (type) {
			case "leadership":
				return "default";
			case "volunteer":
				return "secondary";
			case "competition":
				return "outline";
			case "club":
				return "outline";
			case "sports":
				return "outline";
			case "arts":
				return "outline";
			case "community":
				return "outline";
			default:
				return "outline";
		}
	};

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h3 className="text-lg font-semibold">Extracurricular Activities</h3>
					<p className="text-sm text-muted-foreground">
						Your leadership, volunteer work, and other activities
					</p>
				</div>
				{isEditMode && (
					<Button onClick={addActivity} size="sm" className="flex items-center">
						<Plus className="mr-2 h-4 w-4" />
						Add Activity
					</Button>
				)}
			</div>

			<div className="space-y-4">
				{activities.map((activity) => (
					<Card key={activity.id}>
						<CardHeader className="pb-3">
							<div className="flex justify-between items-start">
								<div className="flex items-center space-x-2">
									<Award className="h-5 w-5 text-muted-foreground" />
									<div>
										<CardTitle className="text-base">
											{activity.title || "New Activity"}
										</CardTitle>
										<p className="text-sm text-muted-foreground">
											{activity.organization}
										</p>
									</div>
								</div>
								<div className="flex items-center space-x-2">
									<Badge variant={getTypeColor(activity.type)}>
										{activity.type}
									</Badge>
									{isEditMode && (
										<Button
											variant="ghost"
											size="sm"
											onClick={() => removeActivity(activity.id)}
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
									<Label>Activity Title</Label>
									{isEditMode ? (
										<Input
											value={activity.title}
											onChange={(e) =>
												updateActivity(activity.id, "title", e.target.value)
											}
											placeholder="Activity name"
										/>
									) : (
										<div className="p-2 text-sm">{activity.title}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Organization</Label>
									{isEditMode ? (
										<Input
											value={activity.organization}
											onChange={(e) =>
												updateActivity(
													activity.id,
													"organization",
													e.target.value,
												)
											}
											placeholder="Organization name"
										/>
									) : (
										<div className="p-2 text-sm">{activity.organization}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Your Role</Label>
									{isEditMode ? (
										<Input
											value={activity.role}
											onChange={(e) =>
												updateActivity(activity.id, "role", e.target.value)
											}
											placeholder="President, Member, Volunteer, etc."
										/>
									) : (
										<div className="p-2 text-sm">{activity.role}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Type</Label>
									{isEditMode ? (
										<select
											value={activity.type}
											onChange={(e) =>
												updateActivity(activity.id, "type", e.target.value)
											}
											className="w-full p-2 border rounded-md"
										>
											<option value="volunteer">Volunteer</option>
											<option value="leadership">Leadership</option>
											<option value="competition">Competition</option>
											<option value="club">Club</option>
											<option value="sports">Sports</option>
											<option value="arts">Arts</option>
											<option value="community">Community</option>
										</select>
									) : (
										<div className="p-2 text-sm capitalize">
											{activity.type}
										</div>
									)}
								</div>

								<div className="space-y-2 md:col-span-2">
									<Label>Duration</Label>
									{isEditMode ? (
										<div className="space-y-2">
											<div className="flex space-x-2">
												<Input
													type="month"
													value={activity.startDate}
													onChange={(e) =>
														updateActivity(
															activity.id,
															"startDate",
															e.target.value,
														)
													}
													className="flex-1"
												/>
												<Input
													type="month"
													value={activity.endDate}
													onChange={(e) =>
														updateActivity(
															activity.id,
															"endDate",
															e.target.value,
														)
													}
													className="flex-1"
													disabled={activity.current}
												/>
											</div>
											<label className="flex items-center space-x-2 text-sm">
												<input
													type="checkbox"
													checked={activity.current}
													onChange={(e) =>
														updateActivity(
															activity.id,
															"current",
															e.target.checked,
														)
													}
												/>
												<span>Currently active</span>
											</label>
										</div>
									) : (
										<div className="p-2 text-sm">
											{activity.startDate} -{" "}
											{activity.current ? "Present" : activity.endDate}
										</div>
									)}
								</div>
							</div>

							<div className="space-y-2">
								<Label>Description</Label>
								{isEditMode ? (
									<Textarea
										value={activity.description}
										onChange={(e) =>
											updateActivity(activity.id, "description", e.target.value)
										}
										placeholder="Describe your role and responsibilities..."
										rows={3}
									/>
								) : (
									<div className="p-2 text-sm">{activity.description}</div>
								)}
							</div>

							<div className="space-y-2">
								<Label>Key Achievements</Label>
								<div className="flex flex-wrap gap-2">
									{activity.achievements.map((achievement, index) => (
										<Badge key={index} variant="secondary">
											{achievement}
										</Badge>
									))}
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</div>

			{activities.length === 0 && (
				<Card className="text-center py-8">
					<CardContent>
						<Award className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
						<h3 className="text-lg font-semibold mb-2">No Activities Yet</h3>
						<p className="text-muted-foreground mb-4">
							Add your extracurricular activities to showcase your leadership
							and community involvement
						</p>
						{isEditMode && (
							<Button onClick={addActivity}>Add Your First Activity</Button>
						)}
					</CardContent>
				</Card>
			)}
		</div>
	);
}
