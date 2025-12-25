const {themes: prismThemes} = require('prism-react-renderer');

const siteConfig = {};

siteConfig.title = 'Physical AI & Humanoid Robotics';
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
      },
      theme: {
        customCss: './src/css/custom.css',
      },
    },
  ],
];

siteConfig.themeConfig = {};

siteConfig.themeConfig.navbar = {
  title: 'AIGENBOOK',
  items: [
    {
      type: 'docSidebar',
      sidebarId: 'tutorialSidebar',
      position: 'left',
      label: 'Textbook',
    },
  ],
};

siteConfig.themeConfig.prism = {
  theme: prismThemes.github,
  darkTheme: prismThemes.dracula,
};

module.exports = siteConfig;
