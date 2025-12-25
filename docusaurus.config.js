import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'A fast, simple, high-quality learning resource',
  favicon: 'img/favicon.ico',
  url: 'https://imranq74s-projects.vercel.app',
  baseUrl: '/',
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
          editUrl: 'https://github.com/ImranQ74/AIGENBOOK/tree/main/',
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
          {
            type: 'html',
            position: 'left',
            value: '<a href="#" class="chatbot-nav-link" onclick="toggleChatbot(); return false;">AI Chatbot</a>',
          },
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
