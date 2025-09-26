"use client";

import type { OnboardingData } from "@/app/onboarding/page";
import { Badge } from "@/core/components/ui/badge";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import { Input } from "@/core/components/ui/input";
import { Label } from "@/core/components/ui/label";

interface LanguageTestsStepProps {
	data: OnboardingData;
	updateData: (data: Partial<OnboardingData>) => void;
}

export function LanguageTestsStep({
	data,
	updateData,
}: LanguageTestsStepProps) {
	return (
		<div className="space-y-6">
			<div className="text-sm text-muted-foreground mb-4">
				Please provide scores for at least one English proficiency test.
				Standardized tests are optional.
			</div>

			{/* English Proficiency Tests */}
			<Card>
				<CardHeader>
					<CardTitle className="text-lg">English Proficiency Tests</CardTitle>
					<CardDescription>
						Required for most international scholarships
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div className="space-y-2">
							<Label htmlFor="ielts">
								IELTS Score
								<Badge variant="secondary" className="ml-2">
									Overall Band
								</Badge>
							</Label>
							<Input
								id="ielts"
								type="number"
								step="0.5"
								min="0"
								max="9"
								placeholder="7.0"
								value={data.ieltsScore}
								onChange={(e) => updateData({ ieltsScore: e.target.value })}
							/>
							<p className="text-xs text-muted-foreground">Scale: 0-9</p>
						</div>

						<div className="space-y-2">
							<Label htmlFor="toefl">
								TOEFL Score
								<Badge variant="secondary" className="ml-2">
									iBT
								</Badge>
							</Label>
							<Input
								id="toefl"
								type="number"
								min="0"
								max="120"
								placeholder="100"
								value={data.toeflScore}
								onChange={(e) => updateData({ toeflScore: e.target.value })}
							/>
							<p className="text-xs text-muted-foreground">Scale: 0-120</p>
						</div>
					</div>
				</CardContent>
			</Card>

			{/* Standardized Tests */}
			<Card>
				<CardHeader>
					<CardTitle className="text-lg">Standardized Tests</CardTitle>
					<CardDescription>
						Optional - Required for some programs
					</CardDescription>
				</CardHeader>
				<CardContent className="space-y-4">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
						<div className="space-y-2">
							<Label htmlFor="gre">
								GRE Score
								<Badge variant="outline" className="ml-2">
									Optional
								</Badge>
							</Label>
							<Input
								id="gre"
								type="number"
								min="260"
								max="340"
								placeholder="320"
								value={data.greScore}
								onChange={(e) => updateData({ greScore: e.target.value })}
							/>
							<p className="text-xs text-muted-foreground">Scale: 260-340</p>
						</div>

						<div className="space-y-2">
							<Label htmlFor="gmat">
								GMAT Score
								<Badge variant="outline" className="ml-2">
									Optional
								</Badge>
							</Label>
							<Input
								id="gmat"
								type="number"
								min="200"
								max="800"
								placeholder="650"
								value={data.gmatScore}
								onChange={(e) => updateData({ gmatScore: e.target.value })}
							/>
							<p className="text-xs text-muted-foreground">Scale: 200-800</p>
						</div>
					</div>
				</CardContent>
			</Card>

			<div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
				<p className="text-sm text-blue-800">
					<strong>Tip:</strong> If you haven't taken these tests yet, you can
					update your scores later. We'll help you find scholarships that match
					your current qualifications.
				</p>
			</div>
		</div>
	);
}
