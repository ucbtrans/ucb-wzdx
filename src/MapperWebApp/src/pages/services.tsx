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
  const videoPlaceholderRef = useRef<HTMLDivElement>(null);
  const [videoPlayerWidth, setVideoPlayerWidth] = useState<number>(0);
  const [videoPlayerHeight, setVideoPlayerHeight] = useState<number>(0);
  const [galleryImages, setGalleryImages] = useState<string[]>([
    "/inference/predicted_frame0.png",
    "/inference/predicted_frame1.png",
    "/inference/predicted_frame2.png",
    "/inference/predicted_frame3.png",
    "/inference/predicted_frame4.png",
    "/inference/predicted_frame5.png",
    "/inference/predicted_frame6.png",
    "/inference/predicted_frame7.png",
    "/inference/predicted_frame8.png",
    "/inference/predicted_frame9.png",
    "/inference/predicted_frame10.png",
    "/inference/predicted_frame11.png",
    "/inference/predicted_frame12.png",
    "/inference/predicted_frame13.png"
  ]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const handleVideoSelected = (file: File | null) => {
    setSelectedVideoFile(file);
    setShowVideoPlayer(!!file);

    if (file && iframeRef.current && iframeRef.current.contentWindow) {
      const videoUrl = URL.createObjectURL(file);
      iframeRef.current.contentWindow.postMessage(
        { type: 'videoUrl', url: videoUrl },
        'http://localhost:8050'
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

  useEffect(() => {
    if (videoPlaceholderRef.current) {
      setVideoPlayerWidth(videoPlaceholderRef.current.offsetWidth);
      setVideoPlayerHeight(videoPlaceholderRef.current.offsetHeight);
    }
  }, [showVideoPlayer]);

  const goToPreviousImage = () => {
    setCurrentImageIndex((prevIndex) =>
      prevIndex === 0 ? galleryImages.length - 1 : prevIndex - 1
    );
  };

  const goToNextImage = () => {
    setCurrentImageIndex((prevIndex) =>
      prevIndex === galleryImages.length - 1 ? 0 : prevIndex + 1
    );
  };

  return (
    <div>
      <Navbar />
      <main>
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="lg:grid lg:grid-cols-12 lg:gap-8">
              <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
                <h1 className="text-4xl font-bold text-orange-500 tracking-tight sm:text-5xl md:text-6xl">
                  Our Services
                  <span className="block text-orange-900 text-5xl">
                    Visualize and Analyze Your Work Zones
                  </span>
                </h1>
                <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                  Upload a video of your work zone and leverage our tools to visualize and gain insights.
                </p>
                <div className="mt-8 flex flex-col items-start w-full">
                  <VideoUploader onVideoSelected={handleVideoSelected} />
                </div>
              </div>
              <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:w-full lg:col-span-6 lg:flex lg:items-center lg:justify-end">
                <Image
                  src="/images/path-logo-rgbsized.jpg"
                  alt="Services Image"
                  width={400}
                  height={200}
                />
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 bg-white w-full">
          <div className="mt-8 lg:mt-0 flex w-full flex-col lg:flex-row">
            <div className="lg:w-1/2">
              <iframe
                ref={iframeRef}
                src="http://localhost:3306"
                style={{ width: '100%', height: '1300px', border: 'none' }}
              />
            </div>
            <div className="lg:w-1/2 relative">
              {showVideoPlayer && selectedVideoFile ? (
                <div style={{ marginLeft: '40px' }}>
                  <VideoPlayer videoFile={selectedVideoFile} width={videoPlayerWidth} height={videoPlayerHeight} />
                  {/* Image Gallery */}
                  <div className="mt-8">
                    <h2 className="text-2xl font-semibold mb-4">Image Gallery</h2>
                    <div className="relative">
                      <Image
                        src={galleryImages[currentImageIndex]}
                        alt={`Gallery Image ${currentImageIndex + 1}`}
                        width={videoPlayerWidth}
                        height={videoPlayerHeight}
                        className="rounded-lg"
                      />
                      <button
                        onClick={goToPreviousImage}
                        className="absolute top-1/2 left-0 transform -translate-y-1/2 bg-gray-500 p-2 rounded-full"
                      >
                        {'<'}
                      </button>
                      <button
                        onClick={goToNextImage}
                        className="absolute top-1/2 right-0 transform -translate-y-1/2 bg-gray-500 p-2 rounded-full"
                      >
                        {'>'}
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  ref={videoPlaceholderRef}
                  style={{
                    marginLeft: '40px',
                    width: '100%',
                    height: '600px',
                    border: '2px dashed gray',
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    color: 'gray',
                  }}
                >
                  Video Placeholder
                </div>
              )}
            </div>
          </div>

          <div className="lg:grid lg:grid-cols-3 lg:gap-8">
            {/* Additional content for services */}
          </div>
        </section>

        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-gray-900 sm:text-4xl text-center">
              Start Analyzing Your Work Zones Today
            </h2>
            <p className="mt-3 max-w-3xl text-lg text-gray-500 sm:mt-5 sm:text-xl text-center mx-auto">
              Upload your video to begin the analysis and visualization process.
            </p>
            {/* Call-to-action or more service details */}
          </div>
        </section>
      </main>
    </div>
  );
}