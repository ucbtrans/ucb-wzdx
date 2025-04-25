// pages/services.tsx
'use client';

import Image from 'next/image';
import { useState, useRef, useEffect } from 'react';
import VideoUploader from '@/components/VideoUploader';
import VideoPlayer from '@/components/VideoPlayer';
import Navbar from '@/components/Navbar';
import '@/app/globals.css';

export default function ServicesPage() {
  const [selectedVideoFile, setSelectedVideoFile] = useState<File | null>(null);
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const handleVideoSelected = (file: File | null) => {
    setSelectedVideoFile(file);
    setShowVideoPlayer(!!file);

    if (file && iframeRef.current && iframeRef.current.contentWindow) {
      const videoUrl = URL.createObjectURL(file); // Create a temporary URL
      iframeRef.current.contentWindow.postMessage(
        { type: 'videoUrl', url: videoUrl },
        'http://localhost:8050' // Replace with your Dash app's origin
      );
    }
  };

  useEffect(() => {
    return () => {
      if (selectedVideoFile) {
        URL.revokeObjectURL(URL.createObjectURL(selectedVideoFile));
      }
    };
  }, [selectedVideoFile]);

  return (
    <div>
      <Navbar />
      <main>
        {/* ... rest of your Next.js code ... */}
        <section className="py-16 bg-white w-full">
          <div className="mt-8 lg:mt-0 flex w-full flex-col lg:flex-row">
            <div className="lg:w-1/2">
              <iframe
                ref={iframeRef}
                src="http://localhost:8050" // Dash Leaflet app URL
                style={{ width: '100%', height: '1300px', border: 'none' }}
              />
            </div>
            {/* ... rest of Next.js code ... */}
          </div>
          {/* ... rest of Next.js code ... */}
        </section>
        {/* ... rest of Next.js code ... */}
      </main>
    </div>
  );
}