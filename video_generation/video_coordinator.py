from moviepy.editor import CompositeVideoClip, ColorClip, VideoFileClip
import tempfile
import os


class VideoCoordinator:
    def __init__(
        self,
        width=1080,
        height=1920,
        duration=None,
        slide_content=None,
        image_content=None,
        header_text="Video Title",
        background_color=(255, 255, 255),
    ):
        """
        Coordinate the generation of the complete video with text and images.

        Args:
            width: Video width in pixels
            height: Video height in pixels
            duration: Total video duration in seconds (optional, will calculate if not provided)
            slide_content: Content for text slides in upper half
            image_content: Content for images in lower half
            header_text: Text to display as the persistent header
            background_color: Background color for the entire video
        """
        self.width = width
        self.height = height

        # Calculate required duration based on content if not provided
        if duration is None:
            max_text_time = (
                max(s["end_time"] for s in slide_content) if slide_content else 0
            )
            max_image_time = (
                max(i["end_time"] for i in image_content) if image_content else 0
            )
            self.duration = max(max_text_time, max_image_time)
        else:
            self.duration = duration

        self.slide_content = slide_content
        self.image_content = image_content
        self.header_text = header_text
        self.background_color = background_color

    def create_video(self, output_path, fps=30):
        """
        Create the complete video by combining upper and lower half content.

        Args:
            output_path: Path where the final video will be saved
            fps: Frames per second for the output video
        """
        print("Starting video generation process...")
        temp_text_path = None  # Initialize for cleanup handling

        try:
            # Create the text generator for upper half
            from generate_text_video import TextVideoGenerator

            text_generator = TextVideoGenerator(
                width=self.width,
                height=self.height,
                duration=self.duration,
                slide_content=self.slide_content,
                header_text=self.header_text,
            )

            # Create the image generator for lower half
            from generate_image_video import ImageVideoGenerator

            image_generator = ImageVideoGenerator(
                width=self.width,
                height=self.height,
                duration=self.duration,
                image_content=self.image_content,
                transition_duration=0.5,
            )

            print("Creating background...")
            # Create a background for the full video
            background = ColorClip(
                size=(self.width, self.height), color=self.background_color
            ).set_duration(self.duration)

            print("Processing text content...")
            # Create a temporary file for the text part
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_text:
                temp_text_path = temp_text.name
                # Generate the text video
                text_generator.create_video(temp_text_path)
                # Load the text video as a clip
                text_video = VideoFileClip(temp_text_path)
                text_clips = [text_video]

            print("Processing image content...")
            # Get the image clips
            image_clips = image_generator.create_video_segment()

            print("Combining all elements...")
            # Combine all elements
            final_video = CompositeVideoClip(
                [background] + text_clips + image_clips, size=(self.width, self.height)
            )

            print(f"Writing final video to {output_path}")
            # Write the final video
            final_video.write_videofile(
                output_path,
                fps=fps,
                codec="libx264",
                audio=False,
                preset="medium",
                threads=4,
            )

            print("Video generation completed successfully!")

        except Exception as e:
            print(f"Error during video generation: {str(e)}")
            raise

        finally:
            print("Cleaning up resources...")
            try:
                # Clean up temporary files
                if temp_text_path and os.path.exists(temp_text_path):
                    try:
                        os.unlink(temp_text_path)
                    except Exception as e:
                        print(
                            f"Warning: Could not delete temporary file {temp_text_path}: {str(e)}"
                        )

                # Close video clips
                if "final_video" in locals():
                    final_video.close()
                if "text_video" in locals():
                    text_video.close()
                if "background" in locals():
                    background.close()

            except Exception as e:
                print(f"Warning: Error during cleanup: {str(e)}")


# Example usage
if __name__ == "__main__":
    # Sample content (previously defined)
    slide_content = [
        {
            "start_times": [0, 2, 6],
            "end_time": 13,
            "lines": [
                "vessel wall weakening",
                "balloon outward bulge",
                "brain aorta artery",
            ],
        },
        {
            "start_times": [13, 16, 20],
            "end_time": 26,
            "lines": [
                "garden hose weak",
                "water pressure burst",
                "vessel balloon rupture",
            ],
        },
        {
            "start_times": [29, 32, 36],
            "end_time": 39,
            "lines": [
                "brain aneurysm headaches",
                "vision problems drooping",
                "back abdominal pain",
            ],
        },
        {
            "start_times": [49, 51, 57],
            "end_time": 62,
            "lines": [
                "over fifty common",
                "blood pressure smokers",
                "gender specific differences",
            ],
        },
        {
            "start_times": [62, 65, 67],
            "end_time": 75,
            "lines": [
                "ct scan mri",
                "angiography blood vessels",
                "screening detect early",
            ],
        },
    ]

    image_content = [
        {
            "start_time": 0,
            "end_time": 13,
            "image_path": "video_generation/data/definition.png",
        },
        {
            "start_time": 13,
            "end_time": 26,
            "image_path": "video_generation/data/analogy.png",
        },
        {
            "start_time": 26,
            "end_time": 47,
            "image_path": "video_generation/data/symptoms.png",
        },
        {
            "start_time": 47,
            "end_time": 62,
            "image_path": "video_generation/data/epidemiology.png",
        },
        {
            "start_time": 62,
            "end_time": 75,
            "image_path": "video_generation/data/diagnostic.png",
        },
    ]
    # Create and run the coordinator
    coordinator = VideoCoordinator(
        width=1080,
        height=1920,
        slide_content=slide_content,
        image_content=image_content,
        header_text="Aneurysms",
    )

    # Generate the complete video
    coordinator.create_video("final_video.mp4", fps=30)
