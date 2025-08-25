import { z } from 'zod';
import {
	SEARCH_QUERY_MAX_LENGTH,
	SEARCH_QUERY_MIN_LENGTH,
	CONTACT_MESSAGE_MAX_LENGTH,
	CONTACT_MESSAGE_MIN_LENGTH,
	CONTACT_NAME_MAX_LENGTH,
	CONTACT_NAME_MIN_LENGTH,
	EMAIL_MAX_LENGTH,
	TRAIL_REVIEW_MAX_LENGTH
} from '../constants/validation';

// Contact form schema
export const contactSchema = z.object({
	name: z.string()
		.min(CONTACT_NAME_MIN_LENGTH, `Name must be at least ${CONTACT_NAME_MIN_LENGTH} characters`)
		.max(CONTACT_NAME_MAX_LENGTH, `Name must be less than ${CONTACT_NAME_MAX_LENGTH} characters`)
		.regex(/^[a-zA-Z\s'-]+$/, 'Name can only contain letters, spaces, hyphens, and apostrophes'),
	email: z.string()
		.email('Please enter a valid email address')
		.max(EMAIL_MAX_LENGTH, `Email must be less than ${EMAIL_MAX_LENGTH} characters`),
	subject: z.string()
		.min(1, 'Please select a subject'),
	message: z.string()
		.min(CONTACT_MESSAGE_MIN_LENGTH, `Message must be at least ${CONTACT_MESSAGE_MIN_LENGTH} characters`)
		.max(CONTACT_MESSAGE_MAX_LENGTH, `Message must be less than ${CONTACT_MESSAGE_MAX_LENGTH} characters`)
		.trim()
});

export type ContactFormData = z.infer<typeof contactSchema>;

// Search form schema (for the trail search)
export const searchSchema = z.object({
	query: z.string()
		.min(SEARCH_QUERY_MIN_LENGTH, `Search query must be at least ${SEARCH_QUERY_MIN_LENGTH} characters`)
		.max(SEARCH_QUERY_MAX_LENGTH, `Search query must be less than ${SEARCH_QUERY_MAX_LENGTH} characters`)
		.trim(),
	agentType: z.string(),
	showToolTrace: z.boolean()
});

export type SearchFormData = z.infer<typeof searchSchema>;

// Newsletter subscription schema
export const newsletterSchema = z.object({
	email: z.string()
		.email('Please enter a valid email address')
		.max(EMAIL_MAX_LENGTH, `Email must be less than ${EMAIL_MAX_LENGTH} characters`)
});

export type NewsletterFormData = z.infer<typeof newsletterSchema>;

// Trail rating schema
export const trailRatingSchema = z.object({
	trailId: z.string().min(1, 'Trail ID is required'),
	rating: z.number()
		.min(1, 'Rating must be at least 1 star')
		.max(5, 'Rating cannot exceed 5 stars'),
	review: z.string()
		.max(TRAIL_REVIEW_MAX_LENGTH, `Review must be less than ${TRAIL_REVIEW_MAX_LENGTH} characters`)
		.optional(),
	difficulty: z.enum(['easy', 'moderate', 'difficult', 'expert']).optional(),
	conditions: z.enum(['excellent', 'good', 'fair', 'poor']).optional()
});

export type TrailRatingFormData = z.infer<typeof trailRatingSchema>;
