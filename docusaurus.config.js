// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A fast, simple, high-quality learning resource',
  favicon: 'img/favicon.ico',
  url: 'https://yourusername.github.io',
  baseUrl: '/AIGENBOOK/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ur'],
  },
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/yourusername/AIGENBOOK/tree/main/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],
  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/social-card.png',
      navbar: {
        title: 'AIGENBOOK',
        logo: {
          alt: 'AIGENBOOK Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Textbook',
          },
          {to: '/chatbot', label: 'AI Chatbot', position: 'left'},
          {
            type: 'localeDropdown',
            position: 'right',
          },
          {
            type: 'html',
            position: 'right',
            value: '<button id="personalize-btn" class="personalize-btn" onclick="openPersonalizeModal()">Personalize</button>',
          },
        ],
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      // RAG Chatbot configuration
      // For production: set apiEndpoint to your deployed backend URL
      ragConfig: {
        apiEndpoint: 'http://localhost:8000',
        vectorDb: 'qdrant',
      },
    }),
};

export default config;
