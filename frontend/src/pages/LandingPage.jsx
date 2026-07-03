import Navbar from "../components/landing/Navbar";
import Hero from "../components/landing/Hero";
import Features from "../components/landing/Features";
import DSASection from "../components/landing/DSASection";
import TechStack from "../components/landing/TechStack";
import Screenshots from "../components/landing/Screenshots";
import Stats from "../components/landing/Stats";
import CTA from "../components/landing/CTA";
import Footer from "../components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-950">
      <Navbar />
      <Hero />
      <Features />
      <DSASection />
      <TechStack />
      <Screenshots />
      <Stats />
      <CTA />
      <Footer />
    </div>
  );
}
