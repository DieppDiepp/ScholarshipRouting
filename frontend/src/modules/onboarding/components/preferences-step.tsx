"use client";

import type { OnboardingData } from "@/app/onboarding/page";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Checkbox } from "@/core/components/ui/checkbox";
import { Label } from "@/core/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";

interface PreferencesStepProps {
	data: OnboardingData;
	updateData: (data: Partial<OnboardingData>) => void;
}

const countries = [
	"United States",
	"United Kingdom",
	"Canada",
	"Australia",
	"Germany",
	"Netherlands",
	"Sweden",
	"Norway",
	"Denmark",
	"Switzerland",
	"France",
	"Japan",
	"South Korea",
	"Singapore",
	"New Zealand",
];

const degreeTypes = [
	"Master's Degree",
	"PhD",
	"Professional Degree",
	"Research Fellowship",
];

const scholarshipAmounts = [
	"Partial Tuition",
	"Full Tuition",
	"Full Tuition + Living Expenses",
	"Any Amount",
];

export function PreferencesStep({ data, updateData }: PreferencesStepProps) {
	const handleCountryChange = (country: string, checked: boolean) => {
		const updatedCountries = checked
			? [...data.desiredCountries, country]
			: data.desiredCountries.filter((c) => c !== country);
		updateData({ desiredCountries: updatedCountries });
	};

	return (
		<div className="space-y-6">
			<Card>
				<CardHeader>
					<CardTitle className="text-lg">Study Destinations</CardTitle>
					<CardDescription>
						Select countries where you'd like to study (select multiple)
					</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="grid grid-cols-2 md:grid-cols-3 gap-3">
						{countries.map((country) => (
							<div key={country} className="flex items-center space-x-2">
								<Checkbox
									id={country}
									checked={data.desiredCountries.includes(country)}
									onCheckedChange={(checked) =>
										handleCountryChange(country, checked as boolean)
									}
								/>
								<Label
									htmlFor={country}
									className="text-sm font-normal cursor-pointer"
								>
									{country}
								</Label>
							</div>
						))}
					</div>
				</CardContent>
			</Card>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div className="space-y-2">
					<Label htmlFor="desiredDegree">Desired Degree Type *</Label>
					<Select
						value={data.desiredDegree}
						onValueChange={(value) => updateData({ desiredDegree: value })}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select degree type" />
						</SelectTrigger>
						<SelectContent>
							{degreeTypes.map((degree) => (
								<SelectItem key={degree} value={degree}>
									{degree}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>

				<div className="space-y-2">
					<Label htmlFor="scholarshipAmount">Scholarship Coverage *</Label>
					<Select
						value={data.scholarshipAmount}
						onValueChange={(value) => updateData({ scholarshipAmount: value })}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select preferred coverage" />
						</SelectTrigger>
						<SelectContent>
							{scholarshipAmounts.map((amount) => (
								<SelectItem key={amount} value={amount}>
									{amount}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>
			</div>

			<div className="bg-green-50 border border-green-200 rounded-lg p-4">
				<p className="text-sm text-green-800">
					<strong>Smart Matching:</strong> We'll use these preferences to
					prioritize scholarships that best match your goals, but you'll still
					see all relevant opportunities.
				</p>
			</div>
		</div>
	);
}
