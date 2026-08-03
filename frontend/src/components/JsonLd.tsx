import { SITE_URL } from "@/lib/site";

export function JsonLd() {
  const software = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "AstroOS",
    applicationCategory: "LifestyleApplication",
    operatingSystem: "Web",
    url: SITE_URL,
    description:
      "Vedic Astrology Operating System with Evidence → Rule → Classical Source → AI Explanation → Confidence. AI never invents predictions.",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "INR",
    },
  };

  const faq = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: "What is AstroOS?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "AstroOS is a Vedic astrology operating system that matches classical rules to chart evidence and explains conclusions with sources and confidence. AI never invents predictions.",
        },
      },
      {
        "@type": "Question",
        name: "Does AstroOS invent predictions with AI?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "No. AstroOS only explains matched evidence, YAML rules, and classical text references. Every conclusion is auditable.",
        },
      },
      {
        "@type": "Question",
        name: "What is Gun Milan on AstroOS?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "Gun Milan uses the traditional 36-guna Ashtakoot system plus modern compatibility dimensions for kundali matching.",
        },
      },
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(software) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faq) }}
      />
    </>
  );
}
