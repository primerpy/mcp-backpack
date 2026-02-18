import React, { useState } from 'react';
import { Copy, Check, ChevronRight } from 'lucide-react';

export const InstallationBlock: React.FC = () => {
  const [copied, setCopied] = useState(false);
  const command = "claude mcp add backpack -- uvx mcp-backpack";

  const handleCopy = () => {
    navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="w-full max-w-xl mx-auto animate-slide-up" style={{ animationDelay: '0.2s' }}>
      <div className="relative flex items-center bg-zinc-50 border border-zinc-200 rounded-lg p-2 pr-2 sm:pr-4 shadow-sm hover:border-zinc-300 transition-colors">
        <div className="pl-4 pr-3 flex-shrink-0">
            <ChevronRight className="w-4 h-4 text-zinc-400" />
        </div>
        <div className="flex-1 font-mono text-sm sm:text-base text-zinc-700 overflow-x-auto whitespace-nowrap scrollbar-hide py-2">
          <span className="text-purple-700 font-medium">claude</span> mcp add backpack <span className="text-zinc-400">--</span> <span className="text-teal-700 font-medium">uvx</span> mcp-backpack
        </div>
        <button
          onClick={handleCopy}
          className="ml-2 p-2 rounded-md hover:bg-white border border-transparent hover:border-zinc-200 hover:shadow-sm transition-all focus:outline-none"
          aria-label="Copy to clipboard"
        >
          {copied ? (
            <Check className="w-4 h-4 text-teal-600" />
          ) : (
            <Copy className="w-4 h-4 text-zinc-400 hover:text-zinc-600 transition-colors" />
          )}
        </button>
      </div>
      <p className="text-center text-xs text-zinc-400 mt-4 font-sans">
        Requires <span className="font-mono text-zinc-600 bg-zinc-100 px-1 py-0.5 rounded">uv</span> installed
      </p>
    </div>
  );
};