import React, { useMemo } from 'react';
import DOMPurify from 'dompurify';

interface StructuredDataProps {
	data: object;
}

const StructuredData: React.FC<StructuredDataProps> = ({ data }) => {
	const sanitizedData = useMemo(() => {
		const jsonString = JSON.stringify(data);
		return DOMPurify.sanitize(jsonString);
	}, [data]);

	return (
		<script
			type="application/ld+json"
			dangerouslySetInnerHTML={{ __html: sanitizedData }}
		/>
	);
};

export default StructuredData;
