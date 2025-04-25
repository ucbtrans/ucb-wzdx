'use client';

// components/VideoUploader.js
import { useRef } from 'react'; // Removed useState import

const VideoUploader = ({ onVideoSelected }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('video/')) {
      onVideoSelected(file); // Pass the File object to the parent
    } else if (file) {
      alert('Please select a valid video file.');
      fileInputRef.current.value = ''; // Clear the input
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click(); // Trigger file input click
  };

  return (
    <div>
      <input
        type="file"
        accept="video/*"
        onChange={handleFileChange}
        style={{ display: 'none' }} // Hide the default input
        ref={fileInputRef}
      />
      <button onClick={handleButtonClick}>Select Video</button>
    </div>
  );
};

export default VideoUploader;