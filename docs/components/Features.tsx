import React from 'react';
import { Database, GitBranch, Terminal } from 'lucide-react';
import { FeatureCard } from './FeatureCard';

export const Features: React.FC = () => {
  return (
    <section className="py-24 bg-white relative">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-20">
                <h2 className="text-3xl font-serif font-medium text-zinc-900 mb-6">Two Layers, One Backpack</h2>
                <p className="text-lg text-zinc-600 max-w-2xl mx-auto leading-relaxed">
                    Most AI memory needs are just key-value lookups, not semantic search. <br/>Backpack uses a hybrid architecture to balance speed and portability.
                </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <FeatureCard 
                    icon={<Database className="w-6 h-6" />}
                    title="SQLite Persistence"
                    description="The runtime layer uses diskcache (SQLite) for fast, process-safe storage. It handles concurrency and survives session clears without corruption."
                    delay="0s"
                />
                <FeatureCard 
                    icon={<GitBranch className="w-6 h-6" />}
                    title="Git-Ready Portability"
                    description="Pack memories into `backpack.json` for travel. Commit your AI's context to Git and merge it across machines or share with your team."
                    delay="0.1s"
                />
                <FeatureCard 
                    icon={<Terminal className="w-6 h-6" />}
                    title="Zero Infrastructure"
                    description="No Redis. No Vector DB. No servers to manage. Just 138 lines of Python that give your agent a persistent brain in 30 seconds."
                    delay="0.2s"
                />
            </div>
        </div>
    </section>
  );
};