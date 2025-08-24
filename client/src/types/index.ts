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

	// Enhanced location information
	city?: string;
	county?: string;
	state?: string;
	region?: string;
	country?: string;

	// Amenities and access information
	parking_available?: boolean;
	parking_type?: string;
	restrooms?: boolean;
	water_available?: boolean;
	picnic_areas?: boolean;
	camping_available?: boolean;

	// Access and permit information
	entry_fee?: boolean;
	permit_required?: boolean;
	seasonal_access?: string;
	accessibility?: string;

	// Trail characteristics
	surface_type?: string;
	trail_markers?: boolean;
	loop_trail?: boolean;

	// Contact and website
	managing_agency?: string;
	website_url?: string;
	phone_number?: string;
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
	result_count?: number;
	input_parameters?: Record<string, any>;
	reasoning?: string;
	function_call?: {
		name: string;
		arguments: Record<string, any>;
		extraction_confidence?: number;
	};
	search_filters?: Record<string, any>;
	database_query?: string;
	ai_confidence?: number;
	processing_steps?: string[];
	errors?: string[];
	success: boolean;
}

export interface StreamEvent {
	type: 'start' | 'token' | 'tool_trace' | 'done';
	request_id?: string;
	content?: string;
	results?: Trail[];
	parsed_filters?: ParsedFilters;
	tool_traces?: ToolTrace[];
	tool_trace?: ToolTrace;
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
