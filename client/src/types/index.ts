export interface Trail {
	id: number;
	name: string;
	distance_miles: number;
	elevation_gain_m: number;
	difficulty: string;
	dogs_allowed: boolean;
	route_type: string;
	features: string[];
	latitude: number;
	longitude: number;
	description_snippet: string;
	why: string;
}

export interface ParsedFilters {
	distance_cap_miles?: number;
	elevation_cap_m?: number;
	difficulty?: string;
	route_type?: string;
	features?: string[];
	dogs_allowed?: boolean;
	radius_miles?: number;
	center_lat?: number;
	center_lng?: number;
}

export interface ToolTrace {
	tool: string;
	duration_ms: number;
	result_count: number;
}

export interface StreamEvent {
	type: 'start' | 'token' | 'done';
	request_id?: string;
	content?: string;
	results?: Trail[];
	parsed_filters?: ParsedFilters;
	tool_traces?: ToolTrace[];
	errors?: string[];
}

export interface TrailDetails {
	id: number;
	name: string;
	distance_miles: number;
	elevation_gain_m: number;
	difficulty: string;
	dogs_allowed: boolean;
	route_type: string;
	features: string[];
	latitude: number;
	longitude: number;
	description: string;
}
