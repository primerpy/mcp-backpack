import React from 'react';
import { Github, Twitter, Package } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="py-12 bg-white border-t border-zinc-200 text-center">
      <div className="max-w-5xl mx-auto px-4 flex flex-col items-center">
        <div className="flex items-center gap-2 mb-6 font-serif font-semibold text-zinc-900">
          <Package className="w-5 h-5 text-teal-600" />
          mcp-backpack
        </div>
        
        <div className="flex gap-6 mb-8">
          <a href="https://github.com/primerpy/mcp-backpack" target="_blank" rel="noopener noreferrer" className="text-zinc-400 hover:text-zinc-900 transition-colors">
            <Github className="w-5 h-5" />
          </a>
          <a href="#" className="text-zinc-400 hover:text-zinc-900 transition-colors">
            <Twitter className="w-5 h-5" />
          </a>
        </div>
        
        <p className="text-zinc-500 text-sm font-light">
          Open source software. Released under the MIT License. <br/>
          Built by <a href="https://github.com/primerpy" target="_blank" rel="noopener noreferrer" className="underline hover:text-zinc-800">PrimerPy</a>.
        </p>
      </div>
    </footer>
  );
};