import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    {
      type: "category",
      label: "AI Usage in Daily Life",
      collapsed: false,
      items: [
        "ai-usage-in-daily-life/introduction",
        "ai-usage-in-daily-life/ai-at-home",
        "ai-usage-in-daily-life/ai-in-schools",
        "ai-usage-in-daily-life/ai-in-hospitals",
        "ai-usage-in-daily-life/ai-in-business",
        "ai-usage-in-daily-life/ai-in-entertainment",
        "ai-usage-in-daily-life/benefits-of-ai",
        "ai-usage-in-daily-life/future-impact-of-ai",
        "ai-usage-in-daily-life/conclusion",
      ]
    }
  ]
};

export default sidebars;
