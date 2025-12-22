import { themes as prismThemes } from 'prism-react-renderer';
import type { Config } from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// ================================
// CHANGE: Use environment variables to determine deployment platform
// Set DEPLOY_ENV=GITHUB for GitHub Pages, otherwise Vercel is assumed
const isGithubPages = process.env.DEPLOY_ENV === 'GITHUB';
// ================================

const config: Config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Master the Future of Embodied Intelligence',
  favicon: 'img/favicon.ico',

  // ================================
  // CHANGE: Dynamic URL and baseUrl based on deployment platform
  url: isGithubPages
    ? 'https://salmansalim1.github.io'
    : 'https://physical-ai-textbook-jade.vercel.app/',
  baseUrl: isGithubPages ? '/physical-ai-textbook/' : '/',
  // ================================

  organizationName: 'salmansalim1',
  projectName: 'physical-ai-textbook',

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    navbar: {
      title: 'Physical AI',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          href: 'https://github.com/salmansalim1/physical-ai-textbook',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Built for Panaversity Hackathon ${new Date().getFullYear()}`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'cpp'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
