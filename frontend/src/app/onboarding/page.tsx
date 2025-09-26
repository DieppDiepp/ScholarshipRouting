"use client";

import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Progress } from "@/core/components/ui/progress";
import { AcademicStep } from "@/modules/onboarding/components/academic-step";
import { BasicInfoStep } from "@/modules/onboarding/components/basic-info-step";
import { LanguageTestsStep } from "@/modules/onboarding/components/language-tests-step";
import { PreferencesStep } from "@/modules/onboarding/components/preferences-step";
import { ReviewStep } from "@/modules/onboarding/components/review-step";
import { ArrowLeft, ArrowRight, CheckCircle } from "lucide-react";
import { useState } from "react";

export interface OnboardingData {
	// Basic Info
	name: string;
	email: string;
	nationality: string;
	currentLevel: string;

	// Academic
	gpa: string;
	gpaScale: string;
	major: string;
	transcriptFile?: File;

	// Language & Tests
	ieltsScore: string;
	toeflScore: string;
	greScore: string;
	gmatScore: string;

	// Preferences
	desiredCountries: string[];
	desiredDegree: string;
	scholarshipAmount: string;

	// CV
	cvFile?: File;
}

const steps = [
	{ id: 1, title: "Basic Info", description: "Personal details" },
	{ id: 2, title: "Academic", description: "Education background" },
	{ id: 3, title: "Tests", description: "Language & standardized tests" },
	{ id: 4, title: "Preferences", description: "Study preferences" },
	{ id: 5, title: "Review", description: "Confirm details" },
];

export default function OnboardingPage() {
	const [currentStep, setCurrentStep] = useState(1);
	const [data, setData] = useState<OnboardingData>({
		name: "",
		email: "",
		nationality: "",
		currentLevel: "",
		gpa: "",
		gpaScale: "4.0",
		major: "",
		ieltsScore: "",
		toeflScore: "",
		greScore: "",
		gmatScore: "",
		desiredCountries: [],
		desiredDegree: "",
		scholarshipAmount: "",
	});

	const updateData = (newData: Partial<OnboardingData>) => {
		setData((prev) => ({ ...prev, ...newData }));
	};

	const nextStep = () => {
		if (currentStep < steps.length) {
			setCurrentStep(currentStep + 1);
		}
	};

	const prevStep = () => {
		if (currentStep > 1) {
			setCurrentStep(currentStep - 1);
		}
	};

	const progress = (currentStep / steps.length) * 100;

	const renderStep = () => {
		switch (currentStep) {
			case 1:
				return <BasicInfoStep data={data} updateData={updateData} />;
			case 2:
				return <AcademicStep data={data} updateData={updateData} />;
			case 3:
				return <LanguageTestsStep data={data} updateData={updateData} />;
			case 4:
				return <PreferencesStep data={data} updateData={updateData} />;
			case 5:
				return <ReviewStep data={data} updateData={updateData} />;
			default:
				return <BasicInfoStep data={data} updateData={updateData} />;
		}
	};

	const isStepValid = () => {
		switch (currentStep) {
			case 1:
				return data.name && data.email && data.nationality && data.currentLevel;
			case 2:
				return data.gpa && data.gpaScale && data.major;
			case 3:
				return data.ieltsScore || data.toeflScore; // At least one language test
			case 4:
				return (
					data.desiredCountries.length > 0 &&
					data.desiredDegree &&
					data.scholarshipAmount
				);
			case 5:
				return true;
			default:
				return false;
		}
	};

	return (
		<div className="min-h-screen bg-background py-8">
			<div className="container mx-auto max-w-4xl px-4">
				{/* Header */}
				<div className="text-center mb-8">
					<h1 className="text-3xl font-bold mb-2">Welcome to ScholarSearch</h1>
					<p className="text-muted-foreground">
						Let's set up your profile to find the perfect scholarships for you
					</p>
				</div>

				{/* Progress */}
				<div className="mb-8">
					<div className="flex justify-between items-center mb-4">
						<span className="text-sm font-medium">
							Step {currentStep} of {steps.length}
						</span>
						<span className="text-sm text-muted-foreground">
							{Math.round(progress)}% complete
						</span>
					</div>
					<Progress value={progress} className="h-2" />
				</div>

				{/* Steps Navigation */}
				<div className="flex justify-center mb-8">
					<div className="flex items-center space-x-4 overflow-x-auto pb-2">
						{steps.map((step, index) => (
							<div key={step.id} className="flex items-center">
								<div className="flex flex-col items-center min-w-0">
									<div
										className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
											step.id < currentStep
												? "bg-primary border-primary text-primary-foreground"
												: step.id === currentStep
													? "border-primary text-primary"
													: "border-muted-foreground/30 text-muted-foreground"
										}`}
									>
										{step.id < currentStep ? (
											<CheckCircle className="h-5 w-5" />
										) : (
											<span className="text-sm font-medium">{step.id}</span>
										)}
									</div>
									<div className="mt-2 text-center">
										<div className="text-sm font-medium">{step.title}</div>
										<div className="text-xs text-muted-foreground hidden sm:block">
											{step.description}
										</div>
									</div>
								</div>
								{index < steps.length - 1 && (
									<div className="w-12 h-px bg-muted-foreground/30 mx-4 mt-[-20px]" />
								)}
							</div>
						))}
					</div>
				</div>

				{/* Step Content */}
				<Card className="mb-8">
					<CardHeader>
						<CardTitle>{steps[currentStep - 1].title}</CardTitle>
						<CardDescription>
							{steps[currentStep - 1].description}
						</CardDescription>
					</CardHeader>
					<CardContent>{renderStep()}</CardContent>
				</Card>

				{/* Navigation Buttons */}
				<div className="flex justify-between">
					<Button
						variant="outline"
						onClick={prevStep}
						disabled={currentStep === 1}
						className="flex items-center bg-transparent"
					>
						<ArrowLeft className="mr-2 h-4 w-4" />
						Previous
					</Button>

					{currentStep === steps.length ? (
						<Button className="flex items-center" disabled={!isStepValid()}>
							Complete Setup
							<CheckCircle className="ml-2 h-4 w-4" />
						</Button>
					) : (
						<Button
							onClick={nextStep}
							disabled={!isStepValid()}
							className="flex items-center"
						>
							Next
							<ArrowRight className="ml-2 h-4 w-4" />
						</Button>
					)}
				</div>
			</div>
		</div>
	);
}
