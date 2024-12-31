from moviepy.editor import ColorClip, CompositeVideoClip, TextClip
import textwrap


class TextVideoGenerator:
    def __init__(
        self,
        width,
        height,
        duration,
        slide_content,
        header_text,
        font_size=70,
        header_font_multiplier=1.2,  # Header will be 20% larger than content
        header_margin_top=100,  # Space from top of frame to header
    ):
        """
        Initialize a simplified text video generator that creates clean, minimal text animations.

        Args:
            width: Video width in pixels
            height: Video height in pixels
            duration: Video duration in seconds
            slide_content: List of dictionaries containing text content and timing
            header_text: Text to display as the video title
            font_size: Base font size for content text
            header_font_multiplier: How much larger the header should be compared to content
            header_margin_top: Distance from top of frame to header text
        """
        self.width = width
        self.height = height
        self.duration = duration
        self.font_size = int(width * 0.05)  # Base font size as 5% of width
        self.slide_content = slide_content
        self.header_text = header_text
        self.text_clips = []
        self.header_font_size = int(self.font_size * header_font_multiplier)
        self.header_margin_top = header_margin_top
        self.char_limit = 20

        # Calculate zones for header and content
        header_height = int(self.header_font_size * 2)  # Space reserved for header
        self.content_zone = {
            "top": header_height
            + header_margin_top
            + 20,  # Extra 20px buffer after header
            "bottom": height // 2,  # Content stays in upper half
            "left": 0,
            "right": width,
        }

    def wrap_text(self, text):
        """
        Wrap text at character limit while preserving formatting.
        """
        if text.startswith("•"):
            text_without_bullet = text[2:].strip()
            wrapped = textwrap.fill(
                text_without_bullet, width=self.char_limit, subsequent_indent="   "
            )
            return "• " + wrapped
        else:
            return textwrap.fill(text, width=self.char_limit + 5)

    def create_header_clip(self):
        """
        Create the persistent header text clip.
        """
        header_clip = TextClip(
            self.header_text,
            fontsize=self.header_font_size,
            color="black",
            font="Arial-Bold",
            method="label",
        )

        # Center header horizontally
        header_x = (self.width - header_clip.w) // 2

        # Position header at specified distance from top
        header_clip = header_clip.set_position(
            (header_x, self.header_margin_top)
        ).set_duration(self.duration)

        return [header_clip]

    def calculate_content_layout(self, wrapped_lines, line_spacing):
        """
        Calculate the vertical positioning of content text to center it
        in the available space below the header.
        """
        total_height = len(wrapped_lines) * line_spacing
        available_height = self.content_zone["bottom"] - self.content_zone["top"]
        start_y = self.content_zone["top"] + (available_height - total_height) // 2
        return start_y

    def create_video(self, output_path):
        """
        Create the complete video with header and animated content text.
        """
        # Create white background
        background = ColorClip(
            size=(self.width, self.height),
            color=(255, 255, 255),
            duration=self.duration,
        )

        # Create header
        all_clips = [background] + self.create_header_clip()

        # Handle dynamic content text
        line_spacing = self.font_size * 1.5

        for slide in self.slide_content:
            # Calculate total height needed for this slide
            all_wrapped_lines = []
            for line in slide["lines"]:
                wrapped_text = self.wrap_text(line)
                all_wrapped_lines.extend(wrapped_text.split("\n"))

            # Get starting position for this slide's content
            start_y = self.calculate_content_layout(all_wrapped_lines, line_spacing)
            current_y = start_y

            for i, line in enumerate(slide["lines"]):
                start_time = slide["start_times"][i]
                duration = float(slide["end_time"]) - float(start_time)

                wrapped_text = self.wrap_text(line)
                wrapped_lines = wrapped_text.split("\n")

                for wrapped_line in wrapped_lines:
                    # Create the text clip
                    text_clip = TextClip(
                        wrapped_line,
                        fontsize=self.font_size,
                        color="black",
                        font="Arial",
                        method="label",
                    )

                    # Center text horizontally
                    x_pos = (self.width - text_clip.w) // 2

                    # Add timing and animation
                    text_clip = (
                        text_clip.set_position((x_pos, current_y))
                        .set_start(start_time)
                        .set_duration(duration)
                        .crossfadein(0.5)
                    )

                    all_clips.append(text_clip)
                    current_y += line_spacing

                # Add spacing between main items
                current_y += line_spacing * 0.8

        # Create final video
        final_video = CompositeVideoClip(all_clips)

        final_video.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio=False,
            preset="medium",
            threads=4,
        )

        # Clean up resources
        if final_video is not None:
            final_video.close()
        if background is not None:
            background.close()


# Example usage
if __name__ == "__main__":
    slide_content = [
        {
            "start_times": [1, 5],
            "end_time": 13,
            "lines": [
                "systemic",
                "dysfunctional",
            ],
        },
        {
            "start_times": [16, 23],
            "end_time": 26,
            "lines": [
                "mailbox",
                "signals",
            ],
        },
        {
            "start_times": [28, 32, 36],
            "end_time": 40,
            "lines": [
                "primary discomfort",
                "secondary manifestations",
                "tertiary effects",
            ],
        },
        {
            "start_times": [42, 49],
            "end_time": 53,
            "lines": [
                "percentage",
                "risk factors",
            ],
        },
        {
            "start_times": [55, 59, 63],
            "end_time": 66,
            "lines": [
                "primary testing methods",
                "key indicators",
                "secondary evaluation methods",
            ],
        },
    ]

    generator = TextVideoGenerator(
        width=1080,
        height=1920,
        duration=66,
        slide_content=slide_content,
        header_text="Systemic disorder",
        header_margin_top=100,  # Adjust this value to move the header up or down
    )
    generator.create_video("text_animations.mp4")
