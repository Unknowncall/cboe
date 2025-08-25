import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import SearchForm from '../SearchForm';

// Mock props
const mockProps = {
	message: '',
	setMessage: vi.fn(),
	onSubmit: vi.fn(),
	isStreaming: false,
	showToolTrace: false,
	setShowToolTrace: vi.fn(),
	selectedAgent: 'custom',
	setSelectedAgent: vi.fn(),
};

const renderWithRouter = (component: React.ReactElement) => {
	return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('SearchForm', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	it('should render search form with all required elements', () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		expect(screen.getByLabelText(/what kind of trail adventure/i)).toBeInTheDocument();
		expect(screen.getByRole('textbox')).toBeInTheDocument();
		expect(screen.getByRole('button', { name: /discover trails/i })).toBeInTheDocument();
		expect(screen.getByLabelText(/select ai agent type/i)).toBeInTheDocument();
	});

	it('should validate minimum query length', async () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		const textarea = screen.getByRole('textbox');
		const submitButton = screen.getByRole('button', { name: /discover trails/i });

		fireEvent.change(textarea, { target: { value: 'ab' } });
		fireEvent.click(submitButton);

		await waitFor(() => {
			expect(screen.getByText(/must be at least 3 characters/)).toBeInTheDocument();
		});
	});

	it('should validate maximum query length', async () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		const textarea = screen.getByRole('textbox');
		const longText = 'a'.repeat(501); // Exceeds 500 character limit

		fireEvent.change(textarea, { target: { value: longText } });

		await waitFor(() => {
			expect(screen.getByText(/must be less than 500 characters/)).toBeInTheDocument();
		});
	});

	it('should call onSubmit with correct data when form is valid', async () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		const textarea = screen.getByRole('textbox');
		const submitButton = screen.getByRole('button', { name: /discover trails/i });

		fireEvent.change(textarea, { target: { value: 'Easy trail near Chicago' } });
		fireEvent.click(submitButton);

		await waitFor(() => {
			expect(mockProps.onSubmit).toHaveBeenCalledWith({
				query: 'Easy trail near Chicago',
				showToolTrace: false,
				agentType: 'custom'
			});
		});
	});

	it('should disable submit button when streaming', () => {
		renderWithRouter(<SearchForm {...mockProps} isStreaming={true} />);

		const submitButton = screen.getByRole('button');
		expect(submitButton).toBeDisabled();
		expect(screen.getByText(/exploring trails/i)).toBeInTheDocument();
	});

	it('should allow keyboard submission with Enter key', async () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		const textarea = screen.getByRole('textbox');
		fireEvent.change(textarea, { target: { value: 'Test query for trails' } });
		fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter' });

		await waitFor(() => {
			expect(mockProps.onSubmit).toHaveBeenCalled();
		});
	});

	it('should prevent submission with Shift+Enter', () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		const textarea = screen.getByRole('textbox');
		fireEvent.change(textarea, { target: { value: 'Test query' } });
		fireEvent.keyDown(textarea, { key: 'Enter', code: 'Enter', shiftKey: true });

		expect(mockProps.onSubmit).not.toHaveBeenCalled();
	});

	it('should update character counter as user types', () => {
		renderWithRouter(<SearchForm {...mockProps} />);

		const textarea = screen.getByRole('textbox');
		fireEvent.change(textarea, { target: { value: 'Hello' } });

		expect(screen.getByText('5/500')).toBeInTheDocument();
	});
});
