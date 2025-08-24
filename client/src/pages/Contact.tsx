import React, { useState } from 'react';
import { Mail, MessageSquare, MapPin, Clock, Send, CheckCircle } from 'lucide-react';

const Contact: React.FC = () => {
	const [formData, setFormData] = useState({
		name: '',
		email: '',
		subject: '',
		message: ''
	});
	const [isSubmitted, setIsSubmitted] = useState(false);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		// Here you would typically send the form data to your backend
		console.log('Form submitted:', formData);
		setIsSubmitted(true);

		// Reset form after a delay
		setTimeout(() => {
			setIsSubmitted(false);
			setFormData({
				name: '',
				email: '',
				subject: '',
				message: ''
			});
		}, 3000);
	};

	const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
		setFormData({
			...formData,
			[e.target.name]: e.target.value
		});
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-emerald-50 via-blue-50 to-indigo-50">
			{/* Hero Section */}
			<div className="bg-gradient-to-r from-emerald-600 to-blue-600 text-white">
				<div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8 text-center">
					<Mail className="h-16 w-16 mx-auto mb-6 text-emerald-200" />
					<h1 className="text-4xl md:text-5xl font-bold mb-4">
						Get in Touch
					</h1>
					<p className="text-xl max-w-3xl mx-auto">
						Have questions, feedback, or suggestions? We'd love to hear from you!
					</p>
				</div>
			</div>

			<div className="max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
				<div className="grid lg:grid-cols-2 gap-12">
					{/* Contact Information */}
					<div>
						<h2 className="text-3xl font-bold text-gray-900 mb-8">Let's Connect</h2>

						<div className="space-y-6 mb-8">
							<div className="flex items-start space-x-4">
								<div className="p-3 bg-emerald-100 rounded-lg">
									<MessageSquare className="h-6 w-6 text-emerald-600" />
								</div>
								<div>
									<h3 className="text-lg font-semibold text-gray-900 mb-2">General Inquiries</h3>
									<p className="text-gray-600">
										Questions about our platform, features, or trail information?
										We're here to help you make the most of your outdoor adventures.
									</p>
								</div>
							</div>

							<div className="flex items-start space-x-4">
								<div className="p-3 bg-blue-100 rounded-lg">
									<MapPin className="h-6 w-6 text-blue-600" />
								</div>
								<div>
									<h3 className="text-lg font-semibold text-gray-900 mb-2">Trail Information</h3>
									<p className="text-gray-600">
										Know of a trail that's missing from our database? Have updates
										on trail conditions? Help us keep our information accurate and complete.
									</p>
								</div>
							</div>

							<div className="flex items-start space-x-4">
								<div className="p-3 bg-purple-100 rounded-lg">
									<Clock className="h-6 w-6 text-purple-600" />
								</div>
								<div>
									<h3 className="text-lg font-semibold text-gray-900 mb-2">Response Time</h3>
									<p className="text-gray-600">
										We typically respond to all inquiries within 24-48 hours.
										For urgent trail safety issues, please contact local authorities.
									</p>
								</div>
							</div>
						</div>

						{/* Contact Methods */}
						<div className="bg-white rounded-2xl p-6 shadow-lg">
							<h3 className="text-xl font-bold text-gray-900 mb-4">Other Ways to Reach Us</h3>
							<div className="space-y-3">
								<div className="flex items-center space-x-3">
									<Mail className="h-5 w-5 text-emerald-600" />
									<span className="text-gray-700">hello@chicagotrailexplorer.com</span>
								</div>
								<div className="flex items-center space-x-3">
									<MessageSquare className="h-5 w-5 text-blue-600" />
									<span className="text-gray-700">Live chat (coming soon)</span>
								</div>
							</div>
						</div>
					</div>

					{/* Contact Form */}
					<div className="bg-white rounded-2xl p-8 shadow-lg">
						{!isSubmitted ? (
							<form onSubmit={handleSubmit} className="space-y-6">
								<h2 className="text-2xl font-bold text-gray-900 mb-6">Send us a Message</h2>

								<div className="grid sm:grid-cols-2 gap-4">
									<div>
										<label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
											Name *
										</label>
										<input
											type="text"
											id="name"
											name="name"
											required
											value={formData.name}
											onChange={handleChange}
											className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
											placeholder="Your name"
										/>
									</div>

									<div>
										<label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
											Email *
										</label>
										<input
											type="email"
											id="email"
											name="email"
											required
											value={formData.email}
											onChange={handleChange}
											className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
											placeholder="your@email.com"
										/>
									</div>
								</div>

								<div>
									<label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
										Subject *
									</label>
									<select
										id="subject"
										name="subject"
										required
										value={formData.subject}
										onChange={handleChange}
										className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
									>
										<option value="">Select a topic</option>
										<option value="general">General Question</option>
										<option value="trail-info">Trail Information</option>
										<option value="technical">Technical Issue</option>
										<option value="feature-request">Feature Request</option>
										<option value="partnership">Partnership/Business</option>
										<option value="other">Other</option>
									</select>
								</div>

								<div>
									<label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
										Message *
									</label>
									<textarea
										id="message"
										name="message"
										required
										value={formData.message}
										onChange={handleChange}
										rows={5}
										className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-colors"
										placeholder="Tell us how we can help..."
									/>
								</div>

								<button
									type="submit"
									className="w-full bg-gradient-to-r from-emerald-600 to-blue-600 text-white font-bold py-3 px-6 rounded-lg hover:from-emerald-700 hover:to-blue-700 transition-all duration-200 flex items-center justify-center space-x-2"
								>
									<Send className="h-5 w-5" />
									<span>Send Message</span>
								</button>
							</form>
						) : (
							<div className="text-center py-12">
								<CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
								<h3 className="text-2xl font-bold text-gray-900 mb-2">Message Sent!</h3>
								<p className="text-gray-600">
									Thank you for reaching out. We'll get back to you within 24-48 hours.
								</p>
							</div>
						)}
					</div>
				</div>

				{/* FAQ Link */}
				<div className="mt-16 text-center">
					<div className="bg-gray-100 rounded-2xl p-8">
						<h3 className="text-xl font-bold text-gray-900 mb-4">
							Looking for Quick Answers?
						</h3>
						<p className="text-gray-600 mb-6">
							Check out our FAQ section for answers to common questions.
						</p>
						<a
							href="/faq"
							className="inline-block bg-emerald-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-emerald-700 transition-colors"
						>
							View FAQ
						</a>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Contact;
