import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import TrailList from '../TrailList';
import type { Trail } from '../../types';

// Mock trail data
const mockTrails: Trail[] = [
	{
		id: 1,
		name: 'Test Trail',
		distance_miles: 3.5,
		elevation_gain_m: 150,
		difficulty: 'easy',
		dogs_allowed: true,
		route_type: 'loop',
		features: ['waterfall', 'lake', 'forest'],
		latitude: 41.8781,
		longitude: -87.6298,
		description_snippet: 'A beautiful test trail',
		why: 'Great for beginners',
		city: 'Chicago',
		state: 'IL',
	},
	{
		id: 2,
		name: 'Another Trail',
		distance_miles: 5.2,
		elevation_gain_m: 300,
		difficulty: 'moderate',
		dogs_allowed: false,
		route_type: 'out and back',
		features: ['prairie', 'boardwalk'],
		latitude: 41.9781,
		longitude: -87.7298,
		description_snippet: 'A moderate test trail',
		why: 'Good workout',
		city: 'Evanston',
		state: 'IL',
	},
];

// Mock window.open
Object.defineProperty(window, 'open', {
	writable: true,
	value: vi.fn(),
});

describe('TrailList', () => {
	it('should render nothing when no trails provided', () => {
		const { container } = render(<TrailList trails={[]} />);
		expect(container.firstChild).toBeNull();
	});

	it('should render trail results heading with correct count', () => {
		render(<TrailList trails={mockTrails} />);

		expect(screen.getByText('🏔️ Trail Results')).toBeInTheDocument();
		expect(screen.getByText('Found 2 amazing trails for your next adventure')).toBeInTheDocument();
	});

	it('should render all trail information correctly', () => {
		render(<TrailList trails={mockTrails} />);

		// Check trail names
		expect(screen.getByText('Test Trail')).toBeInTheDocument();
		expect(screen.getByText('Another Trail')).toBeInTheDocument();

		// Check distances
		expect(screen.getByText('3.5 mi')).toBeInTheDocument();
		expect(screen.getByText('5.2 mi')).toBeInTheDocument();

		// Check locations
		expect(screen.getByText('Chicago, IL')).toBeInTheDocument();
		expect(screen.getByText('Evanston, IL')).toBeInTheDocument();

		// Check difficulty badges
		expect(screen.getByText('easy')).toBeInTheDocument();
		expect(screen.getByText('moderate')).toBeInTheDocument();
	});

	it('should render features with unique keys', () => {
		render(<TrailList trails={mockTrails} />);

		// Check that features are rendered
		expect(screen.getByText('waterfall')).toBeInTheDocument();
		expect(screen.getByText('lake')).toBeInTheDocument();
		expect(screen.getByText('forest')).toBeInTheDocument();
		expect(screen.getByText('prairie')).toBeInTheDocument();
		expect(screen.getByText('boardwalk')).toBeInTheDocument();
	});

	it('should show "more" indicator when trail has more than 4 features', () => {
		const trailWithManyFeatures: Trail = {
			...mockTrails[0],
			features: ['waterfall', 'lake', 'forest', 'prairie', 'boardwalk', 'beach'],
		};

		render(<TrailList trails={[trailWithManyFeatures]} />);

		expect(screen.getByText('+2 more')).toBeInTheDocument();
	});

	it('should show correct dog allowance indicators', () => {
		render(<TrailList trails={mockTrails} />);

		const dogAllowedCells = screen.getAllByText('Yes');
		const dogNotAllowedCells = screen.getAllByText('No');

		expect(dogAllowedCells).toHaveLength(1);
		expect(dogNotAllowedCells).toHaveLength(1);
	});

	it('should render View on Map buttons for all trails', () => {
		render(<TrailList trails={mockTrails} />);

		const mapButtons = screen.getAllByText('View on Map');
		expect(mapButtons).toHaveLength(2);
	});

	it('should convert elevation from meters to feet correctly', () => {
		render(<TrailList trails={mockTrails} />);

		// 150m = ~492ft, 300m = ~984ft
		expect(screen.getByText('492 ft')).toBeInTheDocument();
		expect(screen.getByText('984 ft')).toBeInTheDocument();
	});
});
