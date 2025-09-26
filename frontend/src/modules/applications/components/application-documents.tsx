"use client";

import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogHeader,
	DialogTitle,
	DialogTrigger,
} from "@/core/components/ui/dialog";
import { Progress } from "@/core/components/ui/progress";
import {
	AlertTriangle,
	CheckCircle,
	Clock,
	Download,
	Eye,
	FileText,
	Upload,
} from "lucide-react";
import { useState } from "react";

interface ApplicationDocumentsProps {
	application: any;
}

export function ApplicationDocuments({
	application,
}: ApplicationDocumentsProps) {
	const [uploadProgress, setUploadProgress] = useState<{
		[key: string]: number;
	}>({});

	const getDocumentStatusIcon = (status: string) => {
		switch (status) {
			case "uploaded":
				return <CheckCircle className="h-4 w-4 text-green-600" />;
			case "pending":
				return <Clock className="h-4 w-4 text-orange-600" />;
			case "required":
				return <AlertTriangle className="h-4 w-4 text-red-600" />;
			default:
				return <FileText className="h-4 w-4 text-muted-foreground" />;
		}
	};

	const getDocumentStatusBadge = (status: string) => {
		switch (status) {
			case "uploaded":
				return (
					<Badge className="bg-green-100 text-green-800 border-0">
						Uploaded
					</Badge>
				);
			case "pending":
				return (
					<Badge className="bg-orange-100 text-orange-800 border-0">
						Pending
					</Badge>
				);
			case "required":
				return (
					<Badge className="bg-red-100 text-red-800 border-0">Required</Badge>
				);
			default:
				return <Badge variant="outline">{status}</Badge>;
		}
	};

	const handleFileUpload = (documentName: string, file: File) => {
		// Simulate upload progress
		setUploadProgress((prev) => ({ ...prev, [documentName]: 0 }));

		const interval = setInterval(() => {
			setUploadProgress((prev) => {
				const currentProgress = prev[documentName] || 0;
				if (currentProgress >= 100) {
					clearInterval(interval);
					return { ...prev, [documentName]: 100 };
				}
				return { ...prev, [documentName]: currentProgress + 10 };
			});
		}, 200);
	};

	const uploadedCount = application.documents.required.filter(
		(doc: any) => doc.status === "uploaded",
	).length;
	const totalCount = application.documents.required.length;
	const completionPercentage = Math.round((uploadedCount / totalCount) * 100);

	return (
		<div className="space-y-6">
			{/* Documents Overview */}
			<Card>
				<CardHeader>
					<CardTitle>Document Upload Progress</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="space-y-4">
						<div className="flex justify-between items-center">
							<span className="text-sm font-medium">Overall Progress</span>
							<span className="text-sm text-muted-foreground">
								{uploadedCount}/{totalCount} documents
							</span>
						</div>
						<Progress value={completionPercentage} className="h-2" />
						<div className="flex justify-between text-xs text-muted-foreground">
							<span>{uploadedCount} uploaded</span>
							<span>{totalCount - uploadedCount} remaining</span>
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Document List */}
			<div className="grid gap-4">
				{application.documents.required.map((document: any, index: number) => (
					<Card
						key={index}
						className={`${document.status === "uploaded" ? "border-green-200" : document.status === "required" ? "border-red-200" : ""}`}
					>
						<CardContent className="p-6">
							<div className="flex items-center justify-between">
								<div className="flex items-center gap-4">
									{getDocumentStatusIcon(document.status)}
									<div>
										<h3 className="font-medium">{document.name}</h3>
										{document.status === "uploaded" && (
											<div className="text-sm text-muted-foreground">
												{document.fileName} • {document.fileSize} • Uploaded{" "}
												{new Date(document.uploadDate).toLocaleDateString()}
											</div>
										)}
										{document.status === "pending" && (
											<div className="text-sm text-muted-foreground">
												Required document - not yet uploaded
											</div>
										)}
									</div>
								</div>

								<div className="flex items-center gap-2">
									{getDocumentStatusBadge(document.status)}

									{document.status === "uploaded" ? (
										<div className="flex gap-1">
											<Button variant="outline" size="sm">
												<Eye className="h-4 w-4 mr-1" />
												View
											</Button>
											<Button variant="outline" size="sm">
												<Download className="h-4 w-4 mr-1" />
												Download
											</Button>
											<Button variant="outline" size="sm">
												<Upload className="h-4 w-4 mr-1" />
												Replace
											</Button>
										</div>
									) : (
										<Dialog>
											<DialogTrigger asChild>
												<Button size="sm">
													<Upload className="h-4 w-4 mr-1" />
													Upload
												</Button>
											</DialogTrigger>
											<DialogContent>
												<DialogHeader>
													<DialogTitle>Upload {document.name}</DialogTitle>
													<DialogDescription>
														Select the file you want to upload for this document
														requirement.
													</DialogDescription>
												</DialogHeader>
												<div className="space-y-4">
													<div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
														<Upload className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
														<p className="text-sm text-muted-foreground mb-2">
															Drag and drop your file here, or click to browse
														</p>
														<Button variant="outline">Choose File</Button>
													</div>

													{uploadProgress[document.name] !== undefined && (
														<div className="space-y-2">
															<div className="flex justify-between text-sm">
																<span>Uploading...</span>
																<span>{uploadProgress[document.name]}%</span>
															</div>
															<Progress
																value={uploadProgress[document.name]}
																className="h-2"
															/>
														</div>
													)}
												</div>
											</DialogContent>
										</Dialog>
									)}
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</div>

			{/* Upload Tips */}
			<Card>
				<CardHeader>
					<CardTitle>Upload Guidelines</CardTitle>
				</CardHeader>
				<CardContent>
					<div className="space-y-2 text-sm text-muted-foreground">
						<p>• Accepted formats: PDF, DOC, DOCX (max 10MB per file)</p>
						<p>
							• Ensure all documents are clearly readable and properly formatted
						</p>
						<p>• Official transcripts should be sealed or certified copies</p>
						<p>• Reference letters must be on official letterhead</p>
						<p>
							• Personal statements should follow the specified word count
							limits
						</p>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
