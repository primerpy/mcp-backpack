import React from 'react';

const steps = [
  {
    num: "01",
    title: "Store Context",
    description: "Tell Claude to save important details about architecture, bugs, or decisions to survive context compaction.",
    code: '"Put a note in the backpack: refactoring auth module"'
  },
  {
    num: "02",
    title: "Recall Instantly",
    description: "When the context window clears or you start a new session, ask Claude to check the backpack.",
    code: '"Check backpack for notes about auth"'
  },
  {
    num: "03",
    title: "Pack for Travel",
    description: "Switching machines? Pack memory to JSON, push to Git, and unpack on your desktop.",
    code: '"Pack for travel" → git push → "Unpack"'
  }
];

export const HowItWorks: React.FC = () => {
  return (
    <section id="how-it-works" className="py-24 bg-zinc-50 border-t border-zinc-200">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-20 text-center">
          <h2 className="text-3xl font-serif font-medium text-zinc-900 mb-4">The Travel Pattern</h2>
          <p className="text-zinc-600 text-lg">Your AI's memory moves with your code.</p>
        </div>

        <div className="space-y-16">
          {steps.map((step, idx) => (
            <div key={idx} className="flex flex-col md:flex-row gap-8 md:gap-16 items-start">
              
              {/* Step Info */}
              <div className="flex-1 md:text-right md:sticky md:top-32">
                 <div className="inline-block px-3 py-1 bg-white border border-zinc-200 rounded-full text-xs font-bold text-zinc-400 mb-4 shadow-sm">
                   STEP {step.num}
                 </div>
                 <h3 className="text-2xl font-serif font-medium text-zinc-900 mb-3">{step.title}</h3>
                 <p className="text-zinc-600 leading-relaxed max-w-md ml-auto">{step.description}</p>
              </div>

              {/* Step Visual */}
              <div className="flex-1 w-full">
                 <div className="bg-white border border-zinc-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
                    <div className="flex gap-1.5 mb-4 border-b border-zinc-100 pb-4">
                        <div className="w-2.5 h-2.5 rounded-full bg-zinc-200"></div>
                        <div className="w-2.5 h-2.5 rounded-full bg-zinc-200"></div>
                    </div>
                    <div className="font-mono text-sm text-zinc-700">
                      <span className="text-teal-600 font-bold mr-2">&gt;</span>
                      {step.code}
                    </div>
                 </div>
              </div>
              
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};