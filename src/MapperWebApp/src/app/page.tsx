'use client'; // This directive is important for using React Hooks in this component

import Image from 'next/image';
import { useState } from 'react';
import VideoUploader from '@/components/VideoUploader'; // Adjust the import path if needed
import VideoPlayer from '@/components/VideoPlayer';   // Adjust the import path if needed
import Navbar from '@/components/Navbar';           // Adjust the import path if needed

export default function HomePage() {
  return (
    <div>
      <Navbar />
      <main>
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:grid lg:grid-cols-12 lg:gap-8">
              <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
                <h1 className="text-4xl font-bold text-orange-500 tracking-tight sm:text-5xl md:text-6xl">
                  ZoneMapper
                  <span className="block text-orange-900 text-5xl">A Work Zone Mapping Tool</span>
                </h1>
                <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                  Visualize, edit, and manage work zones
                  in real-time
                </p>
                <div className="mt-8 sm:max-w-lg sm:mx-auto sm:text-center lg:text-left lg:mx-0">
                  <a
                    href="https://path.berkeley.edu/"
                    target="_blank"
                  >
                    Learn more about us
                  </a>
                </div>
              </div>
              <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:w-full lg:col-span-6 lg:flex lg:items-center lg:justify-end">
                <Image
                  src="/images/path-logo-rgbsized.jpg"
                  alt="SaaS product image"
                  width={400}
                  height={200}
                />
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white w-full">
            <div className="mt-8 lg:mt-0 flex w-full">
              <iframe
                src="http://localhost:3306"
                style={{ width: '100%', height: '1300px', border: 'none' }}
              />
            </div>
            <div className="lg:grid lg:grid-cols-3 lg:gap-8">
              {/* ... rest of your section ... */}
            </div>
        </section>

        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            {/* ... rest of your section ... */}
          </div>
        </section>
      </main>
    </div>
  );
}