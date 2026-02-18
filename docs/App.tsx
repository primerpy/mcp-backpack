import React from 'react';
import { Hero } from './components/Hero';
import { Features } from './components/Features';
import { HowItWorks } from './components/HowItWorks';
import { Footer } from './components/Footer';
import { Package } from 'lucide-react';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-primary selection:bg-teal-100 selection:text-teal-900">
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-zinc-200">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-serif font-semibold text-xl tracking-tight text-zinc-900">
             <Package className="w-5 h-5 text-teal-600" strokeWidth={2.5} />
             mcp-backpack
          </div>
          <div className="flex items-center gap-6">
            <a 
              href="https://github.com/primerpy/mcp-backpack" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-sm font-medium text-zinc-600 hover:text-zinc-900 transition-colors"
            >
              GitHub
            </a>
            <a 
              href="https://pypi.org/project/mcp-backpack/" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="text-sm font-medium text-zinc-600 hover:text-zinc-900 transition-colors"
            >
              Docs
            </a>
          </div>
        </div>
      </nav>

      <main>
        <Hero />
        <Features />
        <HowItWorks />
      </main>

      <Footer />
    </div>
  );
};

export default App;