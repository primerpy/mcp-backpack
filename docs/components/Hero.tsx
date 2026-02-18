import React from 'react';
import { Github, ArrowRight } from 'lucide-react';
import { InstallationBlock } from './InstallationBlock';

export const Hero: React.FC = () => {
  const scrollToHowItWorks = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const element = document.getElementById('how-it-works');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto flex flex-col items-center text-center">
      
      <div className="inline-flex items-center px-3 py-1 rounded-full border border-teal-200 bg-teal-50 text-teal-700 text-xs font-semibold uppercase tracking-wide mb-8 animate-fade-in">
        v0.1.2 Now Available
      </div>

      <h1 className="text-5xl sm:text-6xl md:text-7xl font-serif font-medium tracking-tight text-zinc-900 mb-6 max-w-4xl animate-slide-up leading-[1.1]">
        Persistent, Portable <br className="hidden sm:block" />
        Memory for <span className="italic text-teal-600">AI Agents</span>
      </h1>

      <p className="text-xl sm:text-2xl text-zinc-600 max-w-2xl mb-10 animate-slide-up leading-relaxed font-light" style={{ animationDelay: '0.1s' }}>
        Stop context amnesia. A lightweight memory layer that lets Claude Code remember across sessions — and share context across machines via Git.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 mb-16 w-full justify-center animate-slide-up" style={{ animationDelay: '0.15s' }}>
        <a 
          href="#how-it-works"
          onClick={scrollToHowItWorks}
          className="inline-flex items-center justify-center px-8 py-3 rounded-full bg-zinc-900 text-white font-medium hover:bg-zinc-800 transition-all shadow-sm hover:shadow-md cursor-pointer"
        >
          Get Started
          <ArrowRight className="w-4 h-4 ml-2" />
        </a>
        <a 
          href="https://github.com/primerpy/mcp-backpack"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center px-8 py-3 rounded-full bg-white border border-zinc-200 text-zinc-900 font-medium hover:bg-zinc-50 hover:border-zinc-300 transition-all"
        >
          <Github className="w-5 h-5 mr-2" />
          View on GitHub
        </a>
      </div>

      <InstallationBlock />
    </section>
  );
};