import { useEffect } from 'react';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonicalUrl?: string;
  ogImage?: string;
}

const SEOHead: React.FC<SEOHeadProps> = ({
  title = "Chicago Trail Explorer - AI-Powered Hiking Trail Discovery",
  description = "Discover the best hiking trails in Chicago with our AI-powered trail explorer. Get personalized recommendations, detailed trail information, and real-time search results.",
  keywords = "Chicago trails, hiking, outdoor adventures, trail finder, AI recommendations, nature, walking paths, outdoor recreation",
  canonicalUrl = "https://chicago-trail-explorer.com",
  ogImage = "https://chicago-trail-explorer.com/og-image.jpg"
}) => {
  useEffect(() => {
    // Update document title
    document.title = title;

    // Update meta tags
    const updateMetaTag = (name: string, content: string, isProperty: boolean = false) => {
      const selector = isProperty ? `meta[property="${name}"]` : `meta[name="${name}"]`;
      let tag = document.querySelector(selector) as HTMLMetaElement;
      
      if (!tag) {
        tag = document.createElement('meta');
        if (isProperty) {
          tag.setAttribute('property', name);
        } else {
          tag.setAttribute('name', name);
        }
        document.head.appendChild(tag);
      }
      tag.setAttribute('content', content);
    };

    // Update basic meta tags
    updateMetaTag('description', description);
    updateMetaTag('keywords', keywords);

    // Update Open Graph meta tags
    updateMetaTag('og:title', title, true);
    updateMetaTag('og:description', description, true);
    updateMetaTag('og:url', canonicalUrl, true);
    updateMetaTag('og:image', ogImage, true);

    // Update Twitter meta tags
    updateMetaTag('twitter:title', title);
    updateMetaTag('twitter:description', description);
    updateMetaTag('twitter:image', ogImage);

    // Update canonical link
    let canonicalLink = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
    if (!canonicalLink) {
      canonicalLink = document.createElement('link');
      canonicalLink.setAttribute('rel', 'canonical');
      document.head.appendChild(canonicalLink);
    }
    canonicalLink.setAttribute('href', canonicalUrl);

  }, [title, description, keywords, canonicalUrl, ogImage]);

  return null;
};

export default SEOHead;
