import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

const chapters = [
  {
    title: 'Chapter 1: Introduction to Physical AI',
    description: 'Learn the fundamentals of embodied AI and the sensorimotor loop.',
    link: '/docs/chapter-01-physical-ai',
  },
  {
    title: 'Chapter 2: Basics of Humanoid Robotics',
    description: 'Explore robot anatomy, actuation systems, and locomotion.',
    link: '/docs/chapter-02-humanoid-robotics',
  },
  {
    title: 'Chapter 3: ROS 2 Fundamentals',
    description: 'Master nodes, topics, services, and actions in ROS 2.',
    link: '/docs/chapter-03-ros2-fundamentals',
  },
  {
    title: 'Chapter 4: Digital Twin Simulation',
    description: 'Build digital twins with Gazebo and NVIDIA Isaac Sim.',
    link: '/docs/chapter-04-digital-twin',
  },
  {
    title: 'Chapter 5: Vision-Language-Action Systems',
    description: 'Understand VLA models and multimodal AI for robotics.',
    link: '/docs/chapter-05-vla-systems',
  },
  {
    title: 'Chapter 6: Capstone Project',
    description: 'Build a complete AI-robot pipeline from perception to action.',
    link: '/docs/chapter-06-capstone',
  },
];

function ChapterCard({ title, description, link }) {
  return (
    <div className={styles.card}>
      <h3>{title}</h3>
      <p>{description}</p>
      <Link className={styles.cardLink} to={link}>
        Start Learning
      </Link>
    </div>
  );
}

export default function Home() {
  return (
    <Layout
      title="Physical AI & Humanoid Robotics"
      description="An interactive textbook for learning Physical AI and Humanoid Robotics"
    >
      <header className={styles.hero}>
        <div className={styles.heroContent}>
          <h1>Physical AI & Humanoid Robotics</h1>
          <p>
            An interactive textbook covering embodied AI, humanoid robotics,
            ROS 2, digital twins, and vision-language-action systems.
          </p>
          <Link className={styles.heroButton} to="/docs/chapter-01-physical-ai">
            Get Started
          </Link>
        </div>
      </header>
      <main className={styles.main}>
        <section className={styles.chapters}>
          <h2>Chapters</h2>
          <div className={styles.cardGrid}>
            {chapters.map((chapter, idx) => (
              <ChapterCard key={idx} {...chapter} />
            ))}
          </div>
        </section>
      </main>
    </Layout>
  );
}
