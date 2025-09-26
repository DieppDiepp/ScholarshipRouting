"use client";

import type { OnboardingData } from "@/app/onboarding/page";
import { Input } from "@/core/components/ui/input";
import { Label } from "@/core/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";

interface BasicInfoStepProps {
	data: OnboardingData;
	updateData: (data: Partial<OnboardingData>) => void;
}

const countries = [
	"Vietnam",
	"Thailand",
	"Singapore",
	"Malaysia",
	"Indonesia",
	"Philippines",
	"India",
	"China",
	"South Korea",
	"Japan",
	"Other",
];

const currentLevels = [
	"Bachelor's Degree",
	"Master's Degree",
	"PhD",
	"Professional Degree",
];

export function BasicInfoStep({ data, updateData }: BasicInfoStepProps) {
	return (
		<div className="space-y-6">
			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				<div className="space-y-2">
					<Label htmlFor="name">Full Name *</Label>
					<Input
						id="name"
						placeholder="Enter your full name"
						value={data.name}
						onChange={(e) => updateData({ name: e.target.value })}
					/>
				</div>

				<div className="space-y-2">
					<Label htmlFor="email">Email Address *</Label>
					<Input
						id="email"
						type="email"
						placeholder="your.email@example.com"
						value={data.email}
						onChange={(e) => updateData({ email: e.target.value })}
					/>
				</div>

				<div className="space-y-2">
					<Label htmlFor="nationality">Nationality *</Label>
					<Select
						value={data.nationality}
						onValueChange={(value) => updateData({ nationality: value })}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select your nationality" />
						</SelectTrigger>
						<SelectContent>
							{countries.map((country) => (
								<SelectItem key={country} value={country}>
									{country}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>

				<div className="space-y-2">
					<Label htmlFor="currentLevel">Current Education Level *</Label>
					<Select
						value={data.currentLevel}
						onValueChange={(value) => updateData({ currentLevel: value })}
					>
						<SelectTrigger>
							<SelectValue placeholder="Select your current level" />
						</SelectTrigger>
						<SelectContent>
							{currentLevels.map((level) => (
								<SelectItem key={level} value={level}>
									{level}
								</SelectItem>
							))}
						</SelectContent>
					</Select>
				</div>
			</div>

			<div className="text-sm text-muted-foreground">
				* Required fields. This information helps us match you with relevant
				scholarships.
			</div>
		</div>
	);
}
