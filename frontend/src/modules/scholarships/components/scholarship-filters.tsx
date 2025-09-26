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
import { Input } from "@/core/components/ui/input";
import { Label } from "@/core/components/ui/label";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import { Slider } from "@/core/components/ui/slider";
import { X } from "lucide-react";

interface Filters {
	countries: string[];
	degreeLevel: string;
	minAmount: string;
	maxGpa: string;
	minIelts: string;
	fields: string[];
	deadlineRange: string;
	onlyPassed: boolean;
}

interface ScholarshipFiltersProps {
	filters: Filters;
	onFiltersChange: (filters: Filters) => void;
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
];

const fields = [
	"Computer Science",
	"Data Science",
	"Engineering",
	"Business Administration",
	"Economics",
	"Medicine",
	"Law",
	"Psychology",
	"Biology",
	"Chemistry",
	"Physics",
	"Mathematics",
];

const degreeLevels = ["Bachelor's", "Master's", "PhD", "Professional Degree"];

export function ScholarshipFilters({
	filters,
	onFiltersChange,
}: ScholarshipFiltersProps) {
	const updateFilter = (key: keyof Filters, value: any) => {
		onFiltersChange({ ...filters, [key]: value });
	};

	const toggleCountry = (country: string) => {
		const updated = filters.countries.includes(country)
			? filters.countries.filter((c) => c !== country)
			: [...filters.countries, country];
		updateFilter("countries", updated);
	};

	const toggleField = (field: string) => {
		const updated = filters.fields.includes(field)
			? filters.fields.filter((f) => f !== field)
			: [...filters.fields, field];
		updateFilter("fields", updated);
	};

	const clearAllFilters = () => {
		onFiltersChange({
			countries: [],
			degreeLevel: "",
			minAmount: "",
			maxGpa: "",
			minIelts: "",
			fields: [],
			deadlineRange: "",
			onlyPassed: false,
		});
	};

	const hasActiveFilters = Object.values(filters).some((value) =>
		Array.isArray(value) ? value.length > 0 : Boolean(value),
	);

	return (
		<div className="space-y-4">
			{/* Filter Header */}
			<Card>
				<CardHeader className="pb-3">
					<div className="flex justify-between items-center">
						<CardTitle className="text-base">Filters</CardTitle>
						{hasActiveFilters && (
							<Button variant="ghost" size="sm" onClick={clearAllFilters}>
								Clear All
							</Button>
						)}
					</div>
				</CardHeader>
			</Card>

			{/* Hard Conditions */}
			<Card>
				<CardHeader className="pb-3">
					<CardTitle className="text-base">Hard Requirements</CardTitle>
					<CardDescription>
						Filter by minimum eligibility criteria
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="flex items-center space-x-2">
						<Checkbox
							id="onlyPassed"
							checked={filters.onlyPassed}
							onCheckedChange={(checked) => updateFilter("onlyPassed", checked)}
						/>
						<Label htmlFor="onlyPassed" className="text-sm">
							Only show scholarships I qualify for
						</Label>
					</div>

					<div className="space-y-2">
						<Label className="text-sm">Degree Level</Label>
						<Select
							value={filters.degreeLevel}
							onValueChange={(value) => updateFilter("degreeLevel", value)}
						>
							<SelectTrigger>
								<SelectValue placeholder="Any degree level" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="any">Any degree level</SelectItem>
								{degreeLevels.map((level) => (
									<SelectItem key={level} value={level}>
										{level}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>

					<div className="grid grid-cols-2 gap-2">
						<div className="space-y-2">
							<Label className="text-sm">Max GPA Required</Label>
							<Input
								type="number"
								step="0.1"
								placeholder="4.0"
								value={filters.maxGpa}
								onChange={(e) => updateFilter("maxGpa", e.target.value)}
							/>
						</div>
						<div className="space-y-2">
							<Label className="text-sm">Min IELTS Required</Label>
							<Input
								type="number"
								step="0.5"
								placeholder="6.5"
								value={filters.minIelts}
								onChange={(e) => updateFilter("minIelts", e.target.value)}
							/>
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Countries */}
			<Card>
				<CardHeader className="pb-3">
					<CardTitle className="text-base">Countries</CardTitle>
					<CardDescription>Select preferred study destinations</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="space-y-3">
						{filters.countries.length > 0 && (
							<div className="flex flex-wrap gap-1">
								{filters.countries.map((country) => (
									<Badge key={country} variant="secondary" className="text-xs">
										{country}
										<button
											onClick={() => toggleCountry(country)}
											className="ml-1 hover:bg-secondary-foreground/20 rounded-full p-0.5"
										>
											<X className="h-2 w-2" />
										</button>
									</Badge>
								))}
							</div>
						)}
						<div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto">
							{countries.map((country) => (
								<div key={country} className="flex items-center space-x-2">
									<Checkbox
										id={country}
										checked={filters.countries.includes(country)}
										onCheckedChange={() => toggleCountry(country)}
									/>
									<Label htmlFor={country} className="text-sm cursor-pointer">
										{country}
									</Label>
								</div>
							))}
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Fields of Study */}
			<Card>
				<CardHeader className="pb-3">
					<CardTitle className="text-base">Fields of Study</CardTitle>
					<CardDescription>Filter by academic disciplines</CardDescription>
				</CardHeader>
				<CardContent>
					<div className="space-y-3">
						{filters.fields.length > 0 && (
							<div className="flex flex-wrap gap-1">
								{filters.fields.map((field) => (
									<Badge key={field} variant="secondary" className="text-xs">
										{field}
										<button
											onClick={() => toggleField(field)}
											className="ml-1 hover:bg-secondary-foreground/20 rounded-full p-0.5"
										>
											<X className="h-2 w-2" />
										</button>
									</Badge>
								))}
							</div>
						)}
						<div className="grid grid-cols-1 gap-2 max-h-40 overflow-y-auto">
							{fields.map((field) => (
								<div key={field} className="flex items-center space-x-2">
									<Checkbox
										id={field}
										checked={filters.fields.includes(field)}
										onCheckedChange={() => toggleField(field)}
									/>
									<Label htmlFor={field} className="text-sm cursor-pointer">
										{field}
									</Label>
								</div>
							))}
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Deadline */}
			<Card>
				<CardHeader className="pb-3">
					<CardTitle className="text-base">Application Deadline</CardTitle>
					<CardDescription>Filter by deadline urgency</CardDescription>
				</CardHeader>
				<CardContent>
					<Select
						value={filters.deadlineRange}
						onValueChange={(value) => updateFilter("deadlineRange", value)}
					>
						<SelectTrigger>
							<SelectValue placeholder="Any deadline" />
						</SelectTrigger>
						<SelectContent>
							<SelectItem value="any">Any deadline</SelectItem>
							<SelectItem value="next-month">Next 30 days</SelectItem>
							<SelectItem value="next-3-months">Next 3 months</SelectItem>
							<SelectItem value="next-6-months">Next 6 months</SelectItem>
							<SelectItem value="next-year">Next year</SelectItem>
						</SelectContent>
					</Select>
				</CardContent>
			</Card>

			{/* Soft Weights Customization */}
			<Card>
				<CardHeader className="pb-3">
					<CardTitle className="text-base">Matching Preferences</CardTitle>
					<CardDescription>
						Adjust how we calculate your match score
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="space-y-3">
						<div className="space-y-2">
							<div className="flex justify-between text-sm">
								<Label>GPA Weight</Label>
								<span>30%</span>
							</div>
							<Slider
								defaultValue={[30]}
								max={100}
								step={5}
								className="w-full"
							/>
						</div>
						<div className="space-y-2">
							<div className="flex justify-between text-sm">
								<Label>Publications Weight</Label>
								<span>25%</span>
							</div>
							<Slider
								defaultValue={[25]}
								max={100}
								step={5}
								className="w-full"
							/>
						</div>
						<div className="space-y-2">
							<div className="flex justify-between text-sm">
								<Label>Experience Weight</Label>
								<span>25%</span>
							</div>
							<Slider
								defaultValue={[25]}
								max={100}
								step={5}
								className="w-full"
							/>
						</div>
						<div className="space-y-2">
							<div className="flex justify-between text-sm">
								<Label>Activities Weight</Label>
								<span>20%</span>
							</div>
							<Slider
								defaultValue={[20]}
								max={100}
								step={5}
								className="w-full"
							/>
						</div>
					</div>
					<div className="text-xs text-muted-foreground">
						Adjust these weights to prioritize what matters most for your
						scholarship matching.
					</div>
				</CardContent>
			</Card>
		</div>
	);
}
