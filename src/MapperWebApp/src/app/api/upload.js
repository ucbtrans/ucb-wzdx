// /api/upload.js
import formidable from 'formidable';
import fs from 'fs/promises';
import path from 'path';

// Configure the directory to save uploaded videos
const uploadDir = path.join(process.cwd(), 'public', 'uploads');

// Ensure the upload directory exists
fs.mkdir(uploadDir, { recursive: true }).catch(console.error);

export const config = {
  api: {
    bodyParser: false, // Disable Next.js's default body parser
  },
};

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  try {
    const form = new formidable.IncomingForm({
      uploadDir,
      keepExtensions: true,
      maxFileSize: 10 * 1024 * 1024, // Example: 10MB limit
    });

    form.parse(req, async (err, fields, files) => {
      if (err) {
        console.error('Form parsing error:', err);
        return res.status(500).json({ message: 'Failed to parse form data.' });
      }

      const uploadedFile = files.video;

      if (!uploadedFile) {
        return res.status(400).json({ message: 'No video file uploaded.' });
      }

      const oldPath = uploadedFile.filepath;
      const newFilename = `${Date.now()}-${uploadedFile.originalFilename}`;
      const newPath = path.join(uploadDir, newFilename);

      try {
        await fs.rename(oldPath, newPath);
        const videoUrl = `/uploads/${newFilename}`; // Public URL to access the video
        res.status(200).json({ message: 'Video uploaded successfully!', videoUrl });
      } catch (renameError) {
        console.error('Error renaming file:', renameError);
        await fs.unlink(oldPath); // Clean up the temporary file
        return res.status(500).json({ message: 'Failed to save the uploaded video.' });
      }
    });
  } catch (error) {
    console.error('Unexpected error during upload:', error);
    res.status(500).json({ message: 'An unexpected error occurred.' });
  }
}