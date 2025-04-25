'use client';

// components/VideoPlayer.tsx
import React, { useState, useEffect, useRef } from 'react';

interface VideoPlayerProps {
  videoFile: File;
  width: number;
  height: number;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoFile, width, height }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  useEffect(() => {
    if (videoFile) {
      // Create a temporary URL for the video file
      const url = URL.createObjectURL(videoFile);
      setVideoUrl(url);
      // Clean up the URL when the component unmounts or the videoFile changes
      return () => URL.revokeObjectURL(url);
    } else {
      setVideoUrl(null);
    }
  }, [videoFile]);

  if (!videoUrl) {
    return <p>No video selected.</p>;
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Video Player</h2>
      <video width={width} height={height} controls ref={videoRef}>
        <source src={videoUrl} type={videoFile?.type || 'video/mp4'} />
        Your browser does not support the video tag.
      </video>
    </div>
  );
};

export default VideoPlayer;