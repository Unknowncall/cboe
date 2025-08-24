import React, { useState } from 'react';
import { ChevronDown, ChevronUp, HelpCircle, Search, MapPin, Shield, Clock } from 'lucide-react';

interface FAQItem {
	question: string;
	answer: string;
	category: string;
}

const FAQ: React.FC = () => {
	const [openItems, setOpenItems] = useState<Set<number>>(new Set());

	const toggleItem = (index: number) => {
		const newOpenItems = new Set(openItems);
		if (newOpenItems.has(index)) {
			newOpenItems.delete(index);
		} else {
			newOpenItems.add(index);
		}
		setOpenItems(newOpenItems);
	};

	const faqData: FAQItem[] = [
		{
			category: "Getting Started",
			question: "How do I search for trails?",
			answer: "Simply type what you're looking for in natural language! You can say things like 'easy trails near downtown', 'challenging hikes with waterfalls', or 'dog-friendly paths under 3 miles'. Our AI will understand your request and provide personalized recommendations."
		},
		{
			category: "Getting Started",
			question: "Is Chicago Trail Explorer free to use?",
			answer: "Yes! Chicago Trail Explorer is completely free to use. We believe everyone should have access to discover amazing outdoor spaces in the Chicago area."
		},
		{
			category: "Trail Information",
			question: "How accurate is the trail information?",
			answer: "Our trail database is regularly updated and includes information from official sources, park services, and verified community contributors. We strive for accuracy but always recommend checking current trail conditions before your visit."
		},
		{
			category: "Trail Information",
			question: "What areas does Chicago Trail Explorer cover?",
			answer: "We cover the greater Chicago metropolitan area, including trails within the city limits and surrounding suburbs. This includes forest preserves, lakefront paths, urban trails, and nature areas within about 50 miles of downtown Chicago."
		},
		{
			category: "Trail Information",
			question: "Can I find trails suitable for different skill levels?",
			answer: "Absolutely! Our AI can recommend trails for all skill levels, from easy walks suitable for families to challenging hikes for experienced adventurers. Just specify your preferred difficulty level in your search."
		},
		{
			category: "Features",
			question: "What makes the AI search special?",
			answer: "Our AI understands context and preferences in natural language. Instead of using filters and checkboxes, you can describe exactly what you want: 'quiet trails for bird watching', 'paved paths for wheelchair access', or 'scenic routes for photography'. The AI matches your description to the perfect trails."
		},
		{
			category: "Features",
			question: "Can I save my favorite trails?",
			answer: "Currently, we don't have user accounts or saved favorites, but this feature is coming soon! For now, you can bookmark the trail pages or take screenshots of the recommendations you like."
		},
		{
			category: "Technical",
			question: "Do I need to create an account?",
			answer: "No account required! You can start searching for trails immediately. We're working on optional user accounts that will add features like saved searches and personalized recommendations."
		},
		{
			category: "Technical",
			question: "Does the site work on mobile devices?",
			answer: "Yes! Chicago Trail Explorer is fully responsive and works great on phones, tablets, and desktop computers. Take it with you on your adventures!"
		},
		{
			category: "Safety",
			question: "Are the trails safe?",
			answer: "Trail safety varies by location and conditions. We provide safety information when available, but always research current conditions, check weather, tell someone your plans, and carry appropriate gear. Some trails may have specific safety considerations noted in their descriptions."
		},
		{
			category: "Safety",
			question: "Should I check trail conditions before visiting?",
			answer: "Absolutely! Always check current conditions, weather, and any trail closures before heading out. Contact local park services or check official websites for the most up-to-date information."
		}
	];

	const categories = Array.from(new Set(faqData.map(item => item.category)));

	const getCategoryIcon = (category: string) => {
		switch (category) {
			case "Getting Started": return Search;
			case "Trail Information": return MapPin;
			case "Features": return HelpCircle;
			case "Technical": return Clock;
			case "Safety": return Shield;
			default: return HelpCircle;
		}
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50">
			{/* Hero Section */}
			<div className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white">
				<div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8 text-center">
					<HelpCircle className="h-16 w-16 mx-auto mb-6 text-emerald-200" />
					<h1 className="text-4xl md:text-5xl font-bold mb-4">
						Frequently Asked Questions
					</h1>
					<p className="text-xl max-w-3xl mx-auto">
						Find answers to common questions about Chicago Trail Explorer
					</p>
				</div>
			</div>

			<div className="max-w-4xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
				{/* Quick Links */}
				<div className="mb-12">
					<h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Navigation</h2>
					<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
						{categories.map((category) => {
							const IconComponent = getCategoryIcon(category);
							return (
								<a
									key={category}
									href={`#${category.toLowerCase().replace(' ', '-')}`}
									className="flex items-center space-x-3 bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow"
								>
									<IconComponent className="h-5 w-5 text-emerald-600" />
									<span className="font-medium text-gray-900">{category}</span>
								</a>
							);
						})}
					</div>
				</div>

				{/* FAQ Sections */}
				{categories.map((category) => {
					const categoryItems = faqData.filter(item => item.category === category);
					const IconComponent = getCategoryIcon(category);

					return (
						<div key={category} id={category.toLowerCase().replace(' ', '-')} className="mb-12">
							<div className="flex items-center space-x-3 mb-6">
								<IconComponent className="h-6 w-6 text-emerald-600" />
								<h2 className="text-2xl font-bold text-gray-900">{category}</h2>
							</div>

							<div className="space-y-4">
								{categoryItems.map((item, itemIndex) => {
									const globalIndex = faqData.indexOf(item);
									const isOpen = openItems.has(globalIndex);

									return (
										<div key={itemIndex} className="bg-white rounded-lg shadow-md overflow-hidden">
											<button
												onClick={() => toggleItem(globalIndex)}
												className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
											>
												<span className="font-medium text-gray-900 pr-4">{item.question}</span>
												{isOpen ? (
													<ChevronUp className="h-5 w-5 text-emerald-600 flex-shrink-0" />
												) : (
													<ChevronDown className="h-5 w-5 text-emerald-600 flex-shrink-0" />
												)}
											</button>

											{isOpen && (
												<div className="px-6 pb-4">
													<div className="text-gray-700 leading-relaxed">
														{item.answer}
													</div>
												</div>
											)}
										</div>
									);
								})}
							</div>
						</div>
					);
				})}

				{/* Contact Section */}
				<div className="bg-gradient-to-r from-emerald-600 to-blue-600 rounded-2xl p-8 text-center text-white">
					<h2 className="text-2xl font-bold mb-4">Still Have Questions?</h2>
					<p className="text-lg mb-6 opacity-90">
						Can't find what you're looking for? We'd love to help!
					</p>
					<a
						href="/contact"
						className="inline-block bg-white text-emerald-600 font-bold py-3 px-6 rounded-full hover:bg-gray-100 transition-colors"
					>
						Contact Us
					</a>
				</div>
			</div>
		</div>
	);
};

export default FAQ;
