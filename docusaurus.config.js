const {themes: prismThemes} = require('prism-react-renderer');

const siteConfig = {};

siteConfig.title = 'Physical AI & Humanoid Robotics';
siteConfig.tagline = 'A fast, simple, high-quality learning resource';
siteConfig.favicon = 'img/favicon.ico';
siteConfig.url = 'https://imranq74s-projects.vercel.app';
siteConfig.baseUrl = '/';
siteConfig.onBrokenLinks = 'throw';
siteConfig.onBrokenMarkdownLinks = 'warn';

siteConfig.i18n = {
  defaultLocale: 'en',
  locales: ['en', 'ur'],
};

siteConfig.presets = [
  [
    '@docusaurus/preset-classic',
    {
      docs: {
        sidebarPath: './sidebars.js',
        editUrl: 'https://github.com/ImranQ74/AIGENBOOK/tree/main/',
      },
      theme: {
        customCss: './src/css/custom.css',
      },
    },
  ],
];

siteConfig.themeConfig = {};

siteConfig.themeConfig.image = 'img/social-card.png';

siteConfig.themeConfig.navbar = {
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
};

siteConfig.themeConfig.prism = {
  theme: prismThemes.github,
  darkTheme: prismThemes.dracula,
};

module.exports = siteConfig;
