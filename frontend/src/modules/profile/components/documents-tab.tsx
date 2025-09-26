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
import { Progress } from "@/core/components/ui/progress";
import {
	AlertCircle,
	CheckCircle,
	Download,
	Eye,
	FileText,
	Trash2,
	Upload,
} from "lucide-react";
import { useState } from "react";

interface DocumentsTabProps {
	isEditMode: boolean;
}

interface Document {
	id: string;
	name: string;
	type:
		| "cv"
		| "transcript"
		| "sop"
		| "recommendation"
		| "certificate"
		| "portfolio"
		| "other";
	status: "uploaded" | "processing" | "verified" | "rejected";
	uploadDate: string;
	size: string;
	url?: string;
}

export function DocumentsTab({ isEditMode }: DocumentsTabProps) {
	const [documents, setDocuments] = useState<Document[]>([
		{
			id: "1",
			name: "John_Doe_CV_2024.pdf",
			type: "cv",
			status: "verified",
			uploadDate: "2024-01-15",
			size: "2.3 MB",
			url: "#",
		},
		{
			id: "2",
			name: "Official_Transcript.pdf",
			type: "transcript",
			status: "verified",
			uploadDate: "2024-01-10",
			size: "1.8 MB",
			url: "#",
		},
		{
			id: "3",
			name: "Statement_of_Purpose.docx",
			type: "sop",
			status: "processing",
			uploadDate: "2024-01-20",
			size: "0.5 MB",
		},
	]);

	const documentTypes = [
		{ value: "cv", label: "CV/Resume", required: true },
		{ value: "transcript", label: "Academic Transcript", required: true },
		{ value: "sop", label: "Statement of Purpose", required: false },
		{
			value: "recommendation",
			label: "Recommendation Letter",
			required: false,
		},
		{ value: "certificate", label: "Certificate", required: false },
		{ value: "portfolio", label: "Portfolio", required: false },
		{ value: "other", label: "Other", required: false },
	];

	const getStatusIcon = (status: string) => {
		switch (status) {
			case "verified":
				return <CheckCircle className="h-4 w-4 text-green-600" />;
			case "processing":
				return <AlertCircle className="h-4 w-4 text-yellow-600" />;
			case "rejected":
				return <AlertCircle className="h-4 w-4 text-red-600" />;
			default:
				return <FileText className="h-4 w-4 text-muted-foreground" />;
		}
	};

	const getStatusColor = (status: string) => {
		switch (status) {
			case "verified":
				return "default";
			case "processing":
				return "secondary";
			case "rejected":
				return "destructive";
			default:
				return "outline";
		}
	};

	const getTypeLabel = (type: string) => {
		const docType = documentTypes.find((dt) => dt.value === type);
		return docType?.label || type;
	};

	const removeDocument = (id: string) => {
		setDocuments(documents.filter((doc) => doc.id !== id));
	};

	const requiredDocs = documentTypes.filter((dt) => dt.required);
	const uploadedRequiredDocs = requiredDocs.filter((rd) =>
		documents.some((doc) => doc.type === rd.value && doc.status === "verified"),
	);
	const completionPercentage =
		(uploadedRequiredDocs.length / requiredDocs.length) * 100;

	return (
		<div className="space-y-6">
			<div>
				<h3 className="text-lg font-semibold">Documents</h3>
				<p className="text-sm text-muted-foreground">
					Manage your application documents and certificates
				</p>
			</div>

			{/* Document Completion Status */}
			<Card>
				<CardHeader>
					<CardTitle className="text-base">Document Completion</CardTitle>
					<CardDescription>
						Required documents for scholarship applications
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="space-y-4">
						<div className="flex justify-between items-center">
							<span className="text-sm font-medium">Required Documents</span>
							<span className="text-sm text-muted-foreground">
								{uploadedRequiredDocs.length} of {requiredDocs.length} completed
							</span>
						</div>
						<Progress value={completionPercentage} className="h-2" />
						<div className="grid grid-cols-1 md:grid-cols-2 gap-2">
							{requiredDocs.map((docType) => {
								const isUploaded = documents.some(
									(doc) =>
										doc.type === docType.value && doc.status === "verified",
								);
								return (
									<div
										key={docType.value}
										className="flex items-center space-x-2"
									>
										{isUploaded ? (
											<CheckCircle className="h-4 w-4 text-green-600" />
										) : (
											<AlertCircle className="h-4 w-4 text-yellow-600" />
										)}
										<span className="text-sm">{docType.label}</span>
									</div>
								);
							})}
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Upload Area */}
			{isEditMode && (
				<Card>
					<CardHeader>
						<CardTitle className="text-base">Upload Documents</CardTitle>
						<CardDescription>Add new documents to your profile</CardDescription>
					</CardHeader>
					<CardContent>
						<div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8">
							<div className="text-center">
								<Upload className="mx-auto h-12 w-12 text-muted-foreground/50" />
								<div className="mt-4">
									<Button variant="outline">
										<FileText className="mr-2 h-4 w-4" />
										Choose Files
									</Button>
								</div>
								<p className="mt-2 text-sm text-muted-foreground">
									PDF, DOC, DOCX files up to 10MB each
								</p>
								<p className="text-xs text-muted-foreground mt-1">
									Drag and drop files here or click to browse
								</p>
							</div>
						</div>
					</CardContent>
				</Card>
			)}

			{/* Documents List */}
			<div className="space-y-4">
				<h4 className="font-medium">Uploaded Documents</h4>
				{documents.map((document) => (
					<Card key={document.id}>
						<CardContent className="p-4">
							<div className="flex items-center justify-between">
								<div className="flex items-center space-x-3">
									{getStatusIcon(document.status)}
									<div>
										<div className="font-medium text-sm">{document.name}</div>
										<div className="text-xs text-muted-foreground">
											{getTypeLabel(document.type)} • {document.size} • Uploaded{" "}
											{new Date(document.uploadDate).toLocaleDateString()}
										</div>
									</div>
								</div>
								<div className="flex items-center space-x-2">
									<Badge variant={getStatusColor(document.status)}>
										{document.status}
									</Badge>
									<div className="flex items-center space-x-1">
										{document.url && (
											<Button variant="ghost" size="sm">
												<Eye className="h-4 w-4" />
											</Button>
										)}
										<Button variant="ghost" size="sm">
											<Download className="h-4 w-4" />
										</Button>
										{isEditMode && (
											<Button
												variant="ghost"
												size="sm"
												onClick={() => removeDocument(document.id)}
												className="text-destructive hover:text-destructive"
											>
												<Trash2 className="h-4 w-4" />
											</Button>
										)}
									</div>
								</div>
							</div>
						</CardContent>
					</Card>
				))}
			</div>

			{documents.length === 0 && (
				<Card className="text-center py-8">
					<CardContent>
						<FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
						<h3 className="text-lg font-semibold mb-2">
							No Documents Uploaded
						</h3>
						<p className="text-muted-foreground mb-4">
							Upload your documents to complete your scholarship application
							profile
						</p>
						{isEditMode && <Button>Upload Your First Document</Button>}
					</CardContent>
				</Card>
			)}

			{/* Document Guidelines */}
			<Card className="bg-blue-50 border-blue-200">
				<CardContent className="pt-6">
					<div className="flex items-start space-x-3">
						<div className="text-blue-600 text-sm">📋</div>
						<div className="text-sm text-blue-800">
							<p className="font-medium mb-2">Document Guidelines:</p>
							<ul className="space-y-1 text-xs">
								<li>
									• CV/Resume should be up-to-date and professionally formatted
								</li>
								<li>
									• Transcripts must be official and include GPA information
								</li>
								<li>
									• All documents should be in English or include certified
									translations
								</li>
								<li>• File formats: PDF preferred, DOC/DOCX accepted</li>
								<li>• Maximum file size: 10MB per document</li>
							</ul>
						</div>
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
