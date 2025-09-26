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
import { BookOpen, ExternalLink, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

interface PublicationsTabProps {
	isEditMode: boolean;
}

interface Publication {
	id: string;
	title: string;
	authors: string;
	journal: string;
	year: string;
	type: "journal" | "conference" | "workshop" | "preprint" | "thesis";
	status: "published" | "accepted" | "under-review" | "draft";
	doi: string;
	abstract: string;
	url: string;
}

export function PublicationsTab({ isEditMode }: PublicationsTabProps) {
	const [publications, setPublications] = useState<Publication[]>([
		{
			id: "1",
			title:
				"Deep Learning Approaches for Natural Language Processing in Educational Applications",
			authors: "John Doe, Jane Smith, Prof. Wilson",
			journal: "International Conference on AI in Education",
			year: "2023",
			type: "conference",
			status: "published",
			doi: "10.1000/182",
			abstract:
				"This paper presents novel deep learning approaches for natural language processing specifically designed for educational applications...",
			url: "https://example.com/paper1",
		},
		{
			id: "2",
			title: "Machine Learning Models for Student Performance Prediction",
			authors: "John Doe, Dr. Brown",
			journal: "Journal of Educational Technology",
			year: "2024",
			type: "journal",
			status: "under-review",
			doi: "",
			abstract:
				"We propose a comprehensive framework for predicting student performance using various machine learning techniques...",
			url: "",
		},
	]);

	const addPublication = () => {
		const newPublication: Publication = {
			id: Date.now().toString(),
			title: "",
			authors: "",
			journal: "",
			year: "",
			type: "journal",
			status: "draft",
			doi: "",
			abstract: "",
			url: "",
		};
		setPublications([...publications, newPublication]);
	};

	const removePublication = (id: string) => {
		setPublications(publications.filter((pub) => pub.id !== id));
	};

	const updatePublication = (
		id: string,
		field: keyof Publication,
		value: string,
	) => {
		setPublications(
			publications.map((pub) =>
				pub.id === id ? { ...pub, [field]: value } : pub,
			),
		);
	};

	const getTypeColor = (type: string) => {
		switch (type) {
			case "journal":
				return "default";
			case "conference":
				return "secondary";
			case "workshop":
				return "outline";
			case "preprint":
				return "outline";
			case "thesis":
				return "outline";
			default:
				return "outline";
		}
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case "published":
				return "default";
			case "accepted":
				return "secondary";
			case "under-review":
				return "outline";
			case "draft":
				return "outline";
			default:
				return "outline";
		}
	};

	return (
		<div className="space-y-6">
			<div className="flex justify-between items-center">
				<div>
					<h3 className="text-lg font-semibold">Publications & Research</h3>
					<p className="text-sm text-muted-foreground">
						Your academic publications and research work
					</p>
				</div>
				{isEditMode && (
					<Button
						onClick={addPublication}
						size="sm"
						className="flex items-center"
					>
						<Plus className="mr-2 h-4 w-4" />
						Add Publication
					</Button>
				)}
			</div>

			<div className="space-y-4">
				{publications.map((publication) => (
					<Card key={publication.id}>
						<CardHeader className="pb-3">
							<div className="flex justify-between items-start">
								<div className="flex items-start space-x-2 flex-1">
									<BookOpen className="h-5 w-5 text-muted-foreground mt-0.5" />
									<div className="flex-1">
										<CardTitle className="text-base leading-tight">
											{publication.title || "New Publication"}
										</CardTitle>
										<p className="text-sm text-muted-foreground mt-1">
											{publication.authors}
										</p>
									</div>
								</div>
								<div className="flex items-center space-x-2 ml-4">
									<Badge variant={getTypeColor(publication.type)}>
										{publication.type}
									</Badge>
									<Badge variant={getStatusColor(publication.status)}>
										{publication.status.replace("-", " ")}
									</Badge>
									{isEditMode && (
										<Button
											variant="ghost"
											size="sm"
											onClick={() => removePublication(publication.id)}
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
								<div className="space-y-2 md:col-span-2">
									<Label>Title</Label>
									{isEditMode ? (
										<Input
											value={publication.title}
											onChange={(e) =>
												updatePublication(
													publication.id,
													"title",
													e.target.value,
												)
											}
											placeholder="Publication title"
										/>
									) : (
										<div className="p-2 text-sm">{publication.title}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Authors</Label>
									{isEditMode ? (
										<Input
											value={publication.authors}
											onChange={(e) =>
												updatePublication(
													publication.id,
													"authors",
													e.target.value,
												)
											}
											placeholder="Author 1, Author 2, Author 3"
										/>
									) : (
										<div className="p-2 text-sm">{publication.authors}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Journal/Conference</Label>
									{isEditMode ? (
										<Input
											value={publication.journal}
											onChange={(e) =>
												updatePublication(
													publication.id,
													"journal",
													e.target.value,
												)
											}
											placeholder="Publication venue"
										/>
									) : (
										<div className="p-2 text-sm">{publication.journal}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Year</Label>
									{isEditMode ? (
										<Input
											value={publication.year}
											onChange={(e) =>
												updatePublication(
													publication.id,
													"year",
													e.target.value,
												)
											}
											placeholder="2024"
										/>
									) : (
										<div className="p-2 text-sm">{publication.year}</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Type</Label>
									{isEditMode ? (
										<select
											value={publication.type}
											onChange={(e) =>
												updatePublication(
													publication.id,
													"type",
													e.target.value,
												)
											}
											className="w-full p-2 border rounded-md"
										>
											<option value="journal">Journal</option>
											<option value="conference">Conference</option>
											<option value="workshop">Workshop</option>
											<option value="preprint">Preprint</option>
											<option value="thesis">Thesis</option>
										</select>
									) : (
										<div className="p-2 text-sm capitalize">
											{publication.type}
										</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>Status</Label>
									{isEditMode ? (
										<select
											value={publication.status}
											onChange={(e) =>
												updatePublication(
													publication.id,
													"status",
													e.target.value,
												)
											}
											className="w-full p-2 border rounded-md"
										>
											<option value="published">Published</option>
											<option value="accepted">Accepted</option>
											<option value="under-review">Under Review</option>
											<option value="draft">Draft</option>
										</select>
									) : (
										<div className="p-2 text-sm capitalize">
											{publication.status.replace("-", " ")}
										</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>DOI</Label>
									{isEditMode ? (
										<Input
											value={publication.doi}
											onChange={(e) =>
												updatePublication(publication.id, "doi", e.target.value)
											}
											placeholder="10.1000/182"
										/>
									) : (
										<div className="p-2 text-sm">
											{publication.doi || "Not available"}
										</div>
									)}
								</div>

								<div className="space-y-2">
									<Label>URL</Label>
									{isEditMode ? (
										<Input
											value={publication.url}
											onChange={(e) =>
												updatePublication(publication.id, "url", e.target.value)
											}
											placeholder="https://example.com/paper"
										/>
									) : (
										<div className="p-2 text-sm">
											{publication.url ? (
												<a
													href={publication.url}
													target="_blank"
													rel="noopener noreferrer"
													className="text-blue-600 hover:underline flex items-center"
												>
													View Publication{" "}
													<ExternalLink className="ml-1 h-3 w-3" />
												</a>
											) : (
												"Not available"
											)}
										</div>
									)}
								</div>
							</div>

							<div className="space-y-2">
								<Label>Abstract</Label>
								{isEditMode ? (
									<Textarea
										value={publication.abstract}
										onChange={(e) =>
											updatePublication(
												publication.id,
												"abstract",
												e.target.value,
											)
										}
										placeholder="Brief abstract of the publication..."
										rows={3}
									/>
								) : (
									<div className="p-2 text-sm">{publication.abstract}</div>
								)}
							</div>
						</CardContent>
					</Card>
				))}
			</div>

			{publications.length === 0 && (
				<Card className="text-center py-8">
					<CardContent>
						<BookOpen className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
						<h3 className="text-lg font-semibold mb-2">No Publications Yet</h3>
						<p className="text-muted-foreground mb-4">
							Add your research publications to strengthen your scholarship
							applications
						</p>
						{isEditMode && (
							<Button onClick={addPublication}>
								Add Your First Publication
							</Button>
						)}
					</CardContent>
				</Card>
			)}
		</div>
	);
}
