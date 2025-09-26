import { Badge } from "@/core/components/ui/badge";
import { Button } from "@/core/components/ui/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
} from "@/core/components/ui/card";
import {
	ArrowRight,
	Calendar,
	CheckCircle,
	FileText,
	Globe,
	Search,
	Target,
	TrendingUp,
	Users,
} from "lucide-react";
import Link from "next/link";

export default function HomePage() {
	const features = [
		{
			icon: Search,
			title: "Smart Scholarship Discovery",
			description:
				"AI-powered matching based on your academic profile and preferences",
			color: "text-blue-600",
		},
		{
			icon: Target,
			title: "Application Assistant",
			description: "Grammar checking, SOP templates, and personalized guidance",
			color: "text-green-600",
		},
		{
			icon: Calendar,
			title: "Deadline Management",
			description:
				"Never miss a deadline with smart reminders and calendar integration",
			color: "text-orange-600",
		},
		{
			icon: FileText,
			title: "Progress Tracking",
			description:
				"Monitor your application status across multiple scholarships",
			color: "text-purple-600",
		},
	];

	const stats = [
		{ label: "Active Scholarships", value: "2,500+", icon: Globe },
		{ label: "Success Rate", value: "78%", icon: TrendingUp },
		{ label: "Students Helped", value: "15,000+", icon: Users },
		{ label: "Countries Covered", value: "45+", icon: CheckCircle },
	];

	return (
		<div className="flex flex-col">
			{/* Hero Section */}
			<section className="relative py-20 px-4 bg-gradient-to-br from-background to-muted">
				<div className="container mx-auto max-w-6xl">
					<div className="text-center space-y-6">
						<Badge variant="secondary" className="mb-4">
							🎓 Your Gateway to Global Education
						</Badge>
						<h1 className="text-4xl md:text-6xl font-bold text-balance">
							Find Your Perfect
							<span className="text-accent"> Scholarship</span>
						</h1>
						<p className="text-xl text-muted-foreground max-w-2xl mx-auto text-balance">
							Discover graduate study abroad scholarships tailored to your
							profile with AI-powered matching and comprehensive application
							support.
						</p>
						<div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
							<Button size="lg" asChild>
								<Link href="/onboarding">
									Get Started
									<ArrowRight className="ml-2 h-4 w-4" />
								</Link>
							</Button>
							<Button variant="outline" size="lg" asChild>
								<Link href="/scholarships">Browse Scholarships</Link>
							</Button>
						</div>
					</div>
				</div>
			</section>

			{/* Stats Section */}
			<section className="py-16 px-4 bg-card">
				<div className="container mx-auto max-w-6xl">
					<div className="grid grid-cols-2 md:grid-cols-4 gap-8">
						{stats.map((stat) => (
							<div key={stat.label} className="text-center">
								<div className="flex justify-center mb-2">
									<stat.icon className="h-8 w-8 text-accent" />
								</div>
								<div className="text-3xl font-bold text-foreground">
									{stat.value}
								</div>
								<div className="text-sm text-muted-foreground">
									{stat.label}
								</div>
							</div>
						))}
					</div>
				</div>
			</section>

			{/* Features Section */}
			<section className="py-20 px-4">
				<div className="container mx-auto max-w-6xl">
					<div className="text-center mb-16">
						<h2 className="text-3xl md:text-4xl font-bold mb-4">
							Everything You Need to Succeed
						</h2>
						<p className="text-xl text-muted-foreground max-w-2xl mx-auto">
							Our comprehensive platform guides you through every step of your
							scholarship journey.
						</p>
					</div>

					<div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
						{features.map((feature) => (
							<Card
								key={feature.title}
								className="text-center hover:shadow-lg transition-shadow"
							>
								<CardHeader>
									<div className="flex justify-center mb-4">
										<div className="p-3 rounded-lg bg-muted">
											<feature.icon className={`h-6 w-6 ${feature.color}`} />
										</div>
									</div>
									<CardTitle className="text-lg">{feature.title}</CardTitle>
								</CardHeader>
								<CardContent>
									<CardDescription>{feature.description}</CardDescription>
								</CardContent>
							</Card>
						))}
					</div>
				</div>
			</section>

			{/* CTA Section */}
			<section className="py-20 px-4 bg-primary text-primary-foreground">
				<div className="container mx-auto max-w-4xl text-center">
					<h2 className="text-3xl md:text-4xl font-bold mb-4">
						Ready to Start Your Journey?
					</h2>
					<p className="text-xl mb-8 opacity-90">
						Join thousands of students who have found their perfect scholarship
						match.
					</p>
					<Button size="lg" variant="secondary" asChild>
						<Link href="/onboarding">
							Create Your Profile
							<ArrowRight className="ml-2 h-4 w-4" />
						</Link>
					</Button>
				</div>
			</section>
		</div>
	);
}
