from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, ColorClip
from PIL import Image
import numpy as np
import os


class ImageVideoGenerator:
    def __init__(
        self,
        width,
        height,
        duration,
        image_content,
        transition_duration=0.5,
        background_color=(255, 255, 255),
    ):
        # ... [previous initialization code remains the same] ...
        self.width = width
        self.height = height // 2
        self.full_height = height
        self.duration = duration
        self.image_content = image_content
        self.transition_duration = transition_duration
        self.background_color = background_color
        self.image_clips = []
        self.y_offset = self.height

    def load_and_resize_image(self, image_path):
        # ... [previous image loading code remains the same] ...
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            original_width, original_height = img.size
            width_ratio = self.width / original_width
            height_ratio = self.height / original_height
            scaling_factor = min(width_ratio, height_ratio)

            new_width = int(original_width * scaling_factor)
            new_height = int(original_height * scaling_factor)

            resized_img = img.resize(
                (new_width, new_height), resample=Image.Resampling.LANCZOS
            )

            img_array = np.array(resized_img)
            clip = ImageClip(img_array)

        return clip

    def position_image_clip(self, clip):
        # Calculate center position for the image
        x_position = (self.width - clip.w) // 2
        y_position = self.y_offset + (self.height - clip.h) // 2
        return clip.set_position((x_position, y_position))

    def create_video_segment(self):
        # Process each image and create clips
        for item in self.image_content:
            try:
                clip = self.load_and_resize_image(item["image_path"])
                clip = (
                    clip.set_start(item["start_time"])
                    .set_end(item["end_time"])
                    .crossfadein(self.transition_duration)
                    .crossfadeout(self.transition_duration)
                )

                clip = self.position_image_clip(clip)
                self.image_clips.append(clip)

            except Exception as e:
                print(f"Error processing image {item['image_path']}: {str(e)}")
                continue

        return self.image_clips

    def create_background(self):
        return (
            ColorClip(size=(self.width, self.height), color=self.background_color)
            .set_duration(self.duration)
            .set_position((0, self.y_offset))
        )

    def cleanup_resources(self):
        for clip in self.image_clips:
            if clip is not None:
                clip.close()

    def generate_video(self, output_path, fps=30):
        """
        Generate and save the video to a file.

        Args:
            output_path: Path where the video file should be saved
            fps: Frames per second for the output video
        """
        try:
            # Create background and image clips
            clips = [self.create_background()]
            clips.extend(self.create_video_segment())

            # Create the final composite
            final_video = CompositeVideoClip(clips, size=(self.width, self.full_height))

            print(f"Starting video generation - this may take a few minutes...")
            print(f"Saving video to: {output_path}")

            # Write the video file
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec="libx264",
                audio=False,
                preset="medium",
                threads=4,
            )

            print(f"Video generation completed successfully!")

            # Cleanup
            if final_video is not None:
                final_video.close()

        except Exception as e:
            print(f"Error generating video: {str(e)}")
        finally:
            self.cleanup_resources()


# Example usage that will actually create a video file
if __name__ == "__main__":
    # Sample image content
    image_content = [
        {
            "start_time": 3,
            "end_time": 26,
            "image_path": "video_generation/data/image_1.png",
        },
        {
            "start_time": 26,
            "end_time": 40,
            "image_path": "video_generation/data/image_2.png",
        },
        {
            "start_time": 40,
            "end_time": 67,
            "image_path": "video_generation/data/image_3.png",
        },
    ]

    # Create the generator
    generator = ImageVideoGenerator(
        width=1080,
        height=1920,
        duration=67,
        image_content=image_content,
        transition_duration=0.5,
        background_color=(240, 240, 240),  # Light gray background
    )

    # Generate and save the video
    generator.generate_video("output_video.mp4")
