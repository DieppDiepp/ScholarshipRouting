"use client";

import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@/core/components/ui/select";
import { ArrowUpDown } from "lucide-react";

interface ScholarshipSortProps {
	sortBy: string;
	onSortChange: (sortBy: string) => void;
}

export function ScholarshipSort({
	sortBy,
	onSortChange,
}: ScholarshipSortProps) {
	return (
		<Select value={sortBy} onValueChange={onSortChange}>
			<SelectTrigger className="w-48">
				<ArrowUpDown className="mr-2 h-4 w-4" />
				<SelectValue />
			</SelectTrigger>
			<SelectContent>
				<SelectItem value="match-score">Best Match</SelectItem>
				<SelectItem value="deadline">Deadline (Soonest)</SelectItem>
				<SelectItem value="amount">Scholarship Amount</SelectItem>
				<SelectItem value="alphabetical">Alphabetical</SelectItem>
			</SelectContent>
		</Select>
	);
}
