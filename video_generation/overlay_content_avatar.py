import cv2
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip

class VideoProcessor:
    def __init__(self, foreground_path, background_path, output_path):
        """
        Initialize the VideoProcessor with input and output paths.

        Args:
            foreground_path (str): Path to the avatar video with white background
            background_path (str): Path to the background video
            output_path (str): Path where the combined video will be saved
        """
        self.foreground_path = foreground_path
        self.background_path = background_path
        self.output_path = output_path

        # Initialize video captures
        self.fg_cap = cv2.VideoCapture(foreground_path)
        self.bg_cap = cv2.VideoCapture(background_path)

        # Get video properties
        self.fg_fps = self.fg_cap.get(cv2.CAP_PROP_FPS)
        self.bg_fps = self.bg_cap.get(cv2.CAP_PROP_FPS)
        self.fg_frames = int(self.fg_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.bg_frames = int(self.bg_cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate timing factors
        self.fg_duration = self.fg_frames / self.fg_fps
        self.bg_duration = self.bg_frames / self.bg_fps

        # Use background video's fps if it's longer, otherwise use foreground fps
        self.fps = self.bg_fps if self.bg_duration > self.fg_duration else self.fg_fps

        # Get dimensions
        self.width = int(self.fg_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.fg_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Initialize video writer
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(
            'temp_output.mp4',  # Temporary file without audio
            self.fourcc,
            self.fps,
            (self.width, self.height)
        )

    def process_frame(self, fg_frame, bg_frame):
        """
        Process a single pair of frames to combine them with white background removal.

        Args:
            fg_frame (numpy.ndarray): Foreground frame
            bg_frame (numpy.ndarray): Background frame

        Returns:
            numpy.ndarray: Combined frame
        """
        # Resize background frame to match foreground dimensions
        bg_frame = cv2.resize(bg_frame, (self.width, self.height))

        # Convert frames to float32 for better precision
        fg_float = fg_frame.astype(np.float32) / 255.0
        bg_float = bg_frame.astype(np.float32) / 255.0

        # Create mask for white background
        # Adjust these thresholds based on your specific video
        white_mask = np.all(fg_frame > 240, axis=2)
        white_mask = white_mask.astype(np.float32)

        # Smooth the mask edges
        white_mask = cv2.GaussianBlur(white_mask, (5, 5), 0)
        white_mask = np.stack([white_mask] * 3, axis=2)

        # Combine foreground and background using the mask
        combined = fg_float * (1 - white_mask) + bg_float * white_mask

        # Convert back to uint8
        return (combined * 255).astype(np.uint8)

    def combine_videos(self):
        """
        Process the entire videos and combine them with audio.
        """
        try:
            frame_count = 0
            total_frames = min(self.fg_frames, self.bg_frames)

            while frame_count < total_frames:
                # Calculate the correct frame positions based on timing
                fg_frame_pos = int((frame_count / total_frames) * self.fg_frames)
                bg_frame_pos = int((frame_count / total_frames) * self.bg_frames)

                # Set frame positions
                self.fg_cap.set(cv2.CAP_PROP_POS_FRAMES, fg_frame_pos)
                self.bg_cap.set(cv2.CAP_PROP_POS_FRAMES, bg_frame_pos)

                # Read frames from both videos
                fg_ret, fg_frame = self.fg_cap.read()
                bg_ret, bg_frame = self.bg_cap.read()

                # Check if we've reached the end of either video
                if not fg_ret or not bg_ret:
                    break

                frame_count += 1

                # Process and combine frames
                combined_frame = self.process_frame(fg_frame, bg_frame)

                # Write the frame
                self.out.write(combined_frame)

            # Release resources
            self.fg_cap.release()
            self.bg_cap.release()
            self.out.release()

            # Add audio from the foreground video
            self.add_audio()

        except Exception as e:
            print(f"Error during video processing: {str(e)}")
            self.cleanup()

    def add_audio(self):
        """
        Add audio from the foreground video to the combined video.
        """
        try:
            # Load the temporary video without audio
            video = VideoFileClip("temp_output.mp4")

            # Extract audio from the foreground video
            audio = AudioFileClip(self.foreground_path)

            # Combine video with audio
            final_video = video.set_audio(audio)

            # Write the final video with audio
            final_video.write_videofile(
                self.output_path,
                codec='libx264',
                audio_codec='aac'
            )

            # Close the clips
            video.close()
            audio.close()
            final_video.close()

        except Exception as e:
            print(f"Error during audio processing: {str(e)}")
        finally:
            # Clean up temporary files
            import os
            if os.path.exists("temp_output.mp4"):
                os.remove("temp_output.mp4")

    def cleanup(self):
        """
        Release all resources and clean up temporary files.
        """
        self.fg_cap.release()
        self.bg_cap.release()
        self.out.release()
        cv2.destroyAllWindows()

        import os
        if os.path.exists("temp_output.mp4"):
            os.remove("temp_output.mp4")

# Example usage
if __name__ == "__main__":
    processor = VideoProcessor(
        foreground_path="avatar.mp4",
        background_path="final_video.mp4",
        output_path="combined_output.mp4"
    )
    processor.combine_videos()
