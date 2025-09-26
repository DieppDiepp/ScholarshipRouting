"use client";

import type React from "react";

import { Button } from "@/core/components/ui/button";
import { Card, CardContent } from "@/core/components/ui/card";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
} from "@/core/components/ui/dialog";
import { Progress } from "@/core/components/ui/progress";
import {
	AlertCircle,
	CheckCircle,
	FileText,
	Loader2,
	Upload,
} from "lucide-react";
import { useState } from "react";

interface CVUploadModalProps {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}

interface ParsedField {
	field: string;
	value: string;
	confidence: number;
}

export function CVUploadModal({ open, onOpenChange }: CVUploadModalProps) {
	const [uploadStatus, setUploadStatus] = useState<
		"idle" | "uploading" | "parsing" | "complete" | "error"
	>("idle");
	const [uploadProgress, setUploadProgress] = useState(0);
	const [parsedFields, setParsedFields] = useState<ParsedField[]>([]);
	const [selectedFile, setSelectedFile] = useState<File | null>(null);

	const mockParsedFields: ParsedField[] = [
		{ field: "Name", value: "John Doe", confidence: 95 },
		{ field: "Email", value: "john.doe@example.com", confidence: 98 },
		{ field: "Phone", value: "+84 123 456 789", confidence: 90 },
		{
			field: "Education",
			value: "Master's in Computer Science",
			confidence: 92,
		},
		{
			field: "Experience",
			value: "3 years software development",
			confidence: 88,
		},
		{
			field: "Skills",
			value: "Python, JavaScript, Machine Learning",
			confidence: 85,
		},
	];

	const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
		const file = event.target.files?.[0];
		if (file) {
			setSelectedFile(file);
			handleUpload(file);
		}
	};

	const handleUpload = async (file: File) => {
		setUploadStatus("uploading");
		setUploadProgress(0);

		// Simulate upload progress
		const uploadInterval = setInterval(() => {
			setUploadProgress((prev) => {
				if (prev >= 100) {
					clearInterval(uploadInterval);
					setUploadStatus("parsing");
					simulateParsing();
					return 100;
				}
				return prev + 10;
			});
		}, 200);
	};

	const simulateParsing = async () => {
		// Simulate parsing delay
		setTimeout(() => {
			setParsedFields(mockParsedFields);
			setUploadStatus("complete");
		}, 2000);
	};

	const handleAcceptFields = () => {
		// Here you would typically update the user's profile with the parsed fields
		console.log("Accepting parsed fields:", parsedFields);
		onOpenChange(false);
		resetModal();
	};

	const resetModal = () => {
		setUploadStatus("idle");
		setUploadProgress(0);
		setParsedFields([]);
		setSelectedFile(null);
	};

	const getConfidenceColor = (confidence: number) => {
		if (confidence >= 90) return "text-green-600";
		if (confidence >= 70) return "text-yellow-600";
		return "text-red-600";
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<DialogContent className="max-w-2xl">
				<DialogHeader>
					<DialogTitle>Upload & Parse CV</DialogTitle>
					<DialogDescription>
						Upload your CV and we'll automatically extract information to update
						your profile
					</DialogDescription>
				</DialogHeader>

				<div className="space-y-6">
					{uploadStatus === "idle" && (
						<div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8">
							<div className="text-center">
								<Upload className="mx-auto h-12 w-12 text-muted-foreground/50" />
								<div className="mt-4">
									<Button variant="outline" asChild>
										<label htmlFor="cv-file-upload" className="cursor-pointer">
											<FileText className="mr-2 h-4 w-4" />
											Choose CV File
										</label>
									</Button>
									<input
										id="cv-file-upload"
										type="file"
										accept=".pdf,.doc,.docx"
										onChange={handleFileSelect}
										className="hidden"
									/>
								</div>
								<p className="mt-2 text-sm text-muted-foreground">
									PDF, DOC, or DOCX files up to 10MB
								</p>
							</div>
						</div>
					)}

					{uploadStatus === "uploading" && (
						<Card>
							<CardContent className="p-6">
								<div className="text-center space-y-4">
									<Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
									<div>
										<h3 className="font-medium">Uploading CV...</h3>
										<p className="text-sm text-muted-foreground">
											{selectedFile?.name}
										</p>
									</div>
									<Progress value={uploadProgress} className="w-full" />
									<p className="text-sm text-muted-foreground">
										{uploadProgress}% complete
									</p>
								</div>
							</CardContent>
						</Card>
					)}

					{uploadStatus === "parsing" && (
						<Card>
							<CardContent className="p-6">
								<div className="text-center space-y-4">
									<Loader2 className="mx-auto h-8 w-8 animate-spin text-primary" />
									<div>
										<h3 className="font-medium">Parsing CV Content...</h3>
										<p className="text-sm text-muted-foreground">
											Extracting information from your CV using AI
										</p>
									</div>
								</div>
							</CardContent>
						</Card>
					)}

					{uploadStatus === "complete" && (
						<div className="space-y-4">
							<div className="flex items-center space-x-2 text-green-600">
								<CheckCircle className="h-5 w-5" />
								<h3 className="font-medium">CV Parsed Successfully!</h3>
							</div>

							<Card>
								<CardContent className="p-4">
									<h4 className="font-medium mb-3">Extracted Information</h4>
									<div className="space-y-3">
										{parsedFields.map((field, index) => (
											<div
												key={index}
												className="flex justify-between items-center p-2 bg-muted/50 rounded"
											>
												<div>
													<span className="font-medium text-sm">
														{field.field}:
													</span>
													<span className="ml-2 text-sm">{field.value}</span>
												</div>
												<div className="flex items-center space-x-2">
													<span
														className={`text-xs ${getConfidenceColor(field.confidence)}`}
													>
														{field.confidence}%
													</span>
													{field.confidence >= 90 ? (
														<CheckCircle className="h-4 w-4 text-green-600" />
													) : (
														<AlertCircle className="h-4 w-4 text-yellow-600" />
													)}
												</div>
											</div>
										))}
									</div>
								</CardContent>
							</Card>

							<div className="flex justify-end space-x-2">
								<Button variant="outline" onClick={() => onOpenChange(false)}>
									Cancel
								</Button>
								<Button onClick={handleAcceptFields}>
									Update Profile with Extracted Data
								</Button>
							</div>
						</div>
					)}

					{uploadStatus === "error" && (
						<Card>
							<CardContent className="p-6">
								<div className="text-center space-y-4">
									<AlertCircle className="mx-auto h-8 w-8 text-red-600" />
									<div>
										<h3 className="font-medium text-red-600">Upload Failed</h3>
										<p className="text-sm text-muted-foreground">
											There was an error processing your CV. Please try again.
										</p>
									</div>
									<Button onClick={resetModal}>Try Again</Button>
								</div>
							</CardContent>
						</Card>
					)}
				</div>
			</DialogContent>
		</Dialog>
	);
}
