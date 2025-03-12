// src/components/About.js
import React from 'react';
import '../styles/About.css'; // Ensure this CSS file exists
import Footer from './Footer'; // Reusing the Footer component

const About = () => {
  return (
    <div className="about-container">
      <header className="about-header">
        <h1>About RoutineSync</h1>
      </header>
      
      <main className="about-content">
        <section className="about-section">
          <h2>Our Mission</h2>
          <p>
            At RoutineSync, we believe that a balanced mind and body are the foundation of a fulfilling life. 
            Our mission is to help individuals stay on track with their personal health, mental well-being, and productivity goals. 
            By providing smart reminders and structured scheduling, we ensure that you never miss a self-care routine, a workout, 
            or an important task—helping you build consistency and achieve your best self.
          </p>
        </section>

        <section className="about-section">
          <h2>What We Offer</h2>
          <p>
            RoutineSync is more than just a task manager—it’s your personal wellness and productivity companion. 
            With our intuitive scheduling system, you can set reminders for meditation, exercise, hydration, journaling, and work tasks, 
            ensuring a holistic approach to daily efficiency. Features like flexible recurrence options, motivational nudges, and 
            progress tracking make it easy to stay committed to your goals, whether you're focusing on mental clarity, physical health, 
            or peak performance.
          </p>
        </section>

        <section className="about-section">
          <h2>Our Story</h2>
          <p>
            RoutineSync was founded in 2025 by a team passionate about self-improvement, mental resilience, and productivity. 
            We noticed that most task management apps lacked a human touch—they focused on deadlines and efficiency but 
            ignored the importance of well-being. So, we built a tool that not only keeps you on schedule but also nurtures 
            your mental and physical health. Today, thousands of users trust RoutineSync to create a balanced, productive lifestyle.
          </p>
        </section>

        <section className="about-section">
          <h2>Stay Connected</h2>
          <p>
            Your journey to a healthier, more productive life starts here! We'd love to hear your thoughts, suggestions, 
            or success stories. Reach out to us anytime at <a href="mailto:shivam.hireme@gmail.com">shivam.hireme@gmail.com</a>. 
            Let’s build a better routine together!
          </p>
        </section>
      </main>

      <Footer />
    </div>
  );
};

export default About;
