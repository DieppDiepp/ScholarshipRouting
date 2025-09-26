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
import { Checkbox } from "@/core/components/ui/checkbox";
import { Progress } from "@/core/components/ui/progress";
import {
	AlertCircle,
	CheckCircle,
	Download,
	ExternalLink,
	FileText,
	Upload,
} from "lucide-react";
import { useState } from "react";

interface DocumentsChecklistProps {
	scholarship: any;
}

export function DocumentsChecklist({ scholarship }: DocumentsChecklistProps) {
	const [checkedDocuments, setCheckedDocuments] = useState<string[]>([]);

	const toggleDocument = (docName: string) => {
		setCheckedDocuments((prev) =>
			prev.includes(docName)
				? prev.filter((name) => name !== docName)
				: [...prev, docName],
		);
	};

	const requiredDocs = scholarship.requiredDocuments.filter(
		(doc: any) => doc.required,
	);
	const optionalDocs = scholarship.requiredDocuments.filter(
		(doc: any) => !doc.required,
	);
	const completedRequired = requiredDocs.filter((doc: any) =>
		checkedDocuments.includes(doc.name),
	).length;
	const completionPercentage = (completedRequired / requiredDocs.length) * 100;

	return (
		<div className="space-y-6">
			{/* Progress Overview */}
			<Card>
				<CardHeader>
					<CardTitle>Document Preparation Progress</CardTitle>
					<CardDescription>
						Track your progress in gathering required application documents
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="flex justify-between items-center">
						<span className="text-sm font-medium">Required Documents</span>
						<span className="text-sm text-muted-foreground">
							{completedRequired} of {requiredDocs.length} completed
						</span>
					</div>
					<Progress value={completionPercentage} className="h-3" />
					<div className="text-center">
						<span className="text-2xl font-bold text-primary">
							{Math.round(completionPercentage)}%
						</span>
						<span className="text-sm text-muted-foreground ml-2">Complete</span>
					</div>
				</CardContent>
			</Card>

			{/* Required Documents */}
			<Card>
				<CardHeader>
					<CardTitle className="flex items-center gap-2">
						<AlertCircle className="h-5 w-5 text-red-600" />
						Required Documents
					</CardTitle>
					<CardDescription>
						These documents are mandatory for your application
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					{requiredDocs.map((doc: any, index: number) => (
						<div key={index} className="border rounded-lg p-4">
							<div className="flex items-start justify-between gap-4">
								<div className="flex items-start gap-3 flex-1">
									<Checkbox
										id={doc.name}
										checked={checkedDocuments.includes(doc.name)}
										onCheckedChange={() => toggleDocument(doc.name)}
										className="mt-1"
									/>
									<div className="flex-1">
										<div className="flex items-center gap-2 mb-1">
											<label
												htmlFor={doc.name}
												className="font-medium cursor-pointer"
											>
												{doc.name}
											</label>
											<Badge variant="destructive" className="text-xs">
												Required
											</Badge>
										</div>
										<p className="text-sm text-muted-foreground mb-3">
											{doc.description}
										</p>
										<div className="flex gap-2">
											{doc.template && (
												<Button
													variant="outline"
													size="sm"
													className="flex items-center bg-transparent"
												>
													<Download className="mr-2 h-3 w-3" />
													Template
												</Button>
											)}
											<Button
												variant="outline"
												size="sm"
												className="flex items-center bg-transparent"
											>
												<Upload className="mr-2 h-3 w-3" />
												Upload
											</Button>
											<Button
												variant="outline"
												size="sm"
												className="flex items-center bg-transparent"
											>
												<ExternalLink className="mr-2 h-3 w-3" />
												Guidelines
											</Button>
										</div>
									</div>
								</div>
								<div className="flex items-center">
									{checkedDocuments.includes(doc.name) ? (
										<CheckCircle className="h-5 w-5 text-green-600" />
									) : (
										<div className="h-5 w-5 border-2 border-muted-foreground/30 rounded-full" />
									)}
								</div>
							</div>
						</div>
					))}
				</CardContent>
			</Card>

			{/* Optional Documents */}
			{optionalDocs.length > 0 && (
				<Card>
					<CardHeader>
						<CardTitle className="flex items-center gap-2">
							<FileText className="h-5 w-5 text-blue-600" />
							Optional Documents
						</CardTitle>
						<CardDescription>
							These documents can strengthen your application
						</CardDescription>
					</CardHeader>
					<CardContent className="space-y-4">
						{optionalDocs.map((doc: any, index: number) => (
							<div key={index} className="border rounded-lg p-4">
								<div className="flex items-start justify-between gap-4">
									<div className="flex items-start gap-3 flex-1">
										<Checkbox
											id={`optional-${doc.name}`}
											checked={checkedDocuments.includes(doc.name)}
											onCheckedChange={() => toggleDocument(doc.name)}
											className="mt-1"
										/>
										<div className="flex-1">
											<div className="flex items-center gap-2 mb-1">
												<label
													htmlFor={`optional-${doc.name}`}
													className="font-medium cursor-pointer"
												>
													{doc.name}
												</label>
												<Badge variant="outline" className="text-xs">
													Optional
												</Badge>
											</div>
											<p className="text-sm text-muted-foreground mb-3">
												{doc.description}
											</p>
											<div className="flex gap-2">
												{doc.template && (
													<Button
														variant="outline"
														size="sm"
														className="flex items-center bg-transparent"
													>
														<Download className="mr-2 h-3 w-3" />
														Template
													</Button>
												)}
												<Button
													variant="outline"
													size="sm"
													className="flex items-center bg-transparent"
												>
													<Upload className="mr-2 h-3 w-3" />
													Upload
												</Button>
											</div>
										</div>
									</div>
									<div className="flex items-center">
										{checkedDocuments.includes(doc.name) ? (
											<CheckCircle className="h-5 w-5 text-green-600" />
										) : (
											<div className="h-5 w-5 border-2 border-muted-foreground/30 rounded-full" />
										)}
									</div>
								</div>
							</div>
						))}
					</CardContent>
				</Card>
			)}

			{/* Document Tips */}
			<Card className="bg-blue-50 border-blue-200">
				<CardContent className="pt-6">
					<div className="flex items-start gap-3">
						<FileText className="h-5 w-5 text-blue-600 mt-0.5" />
						<div className="text-sm text-blue-800">
							<p className="font-medium mb-2">Document Preparation Tips:</p>
							<ul className="space-y-1 text-xs">
								<li>
									• Start gathering documents early - some may take weeks to
									obtain
								</li>
								<li>
									• Ensure all documents are in English or include certified
									translations
								</li>
								<li>• Keep digital copies of all documents in PDF format</li>
								<li>
									• Check file size limits before uploading (usually 10MB max)
								</li>
								<li>
									• Use our templates to ensure proper formatting and content
								</li>
								<li>
									• Have documents reviewed by mentors or advisors before
									submission
								</li>
							</ul>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
