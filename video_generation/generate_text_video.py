from moviepy.editor import ColorClip, CompositeVideoClip, TextClip
import textwrap


slide_content = [
    {
        "start_times": [3, 7],
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


class TextVideoGenerator:
    def __init__(
        self,
        width,
        height,
        duration,
        slide_content,
        font_size=70,
        text_color="black",
        text_bg_color=(200, 200, 200),  # Light gray background for text
        text_bg_padding=(20, 10),  # Horizontal and vertical padding
    ):
        """
        Initialize the video generator with customizable styling options

        Args:
            width: Video width in pixels
            height: Video height in pixels
            duration: Video duration in seconds
            slide_content: List of dictionaries containing text content and timing
            font_size: Base font size (will be scaled relative to video width)
            text_color: Color of the text
            text_bg_color: Background color behind text
            text_bg_padding: Tuple of (horizontal, vertical) padding around text
        """
        self.width = width
        self.height = height
        self.duration = duration
        self.font_size = int(width * 0.05)  # 5% of width
        self.slide_content = slide_content
        self.text_clips = []
        self.text_color = text_color
        self.text_bg_color = text_bg_color
        self.text_bg_padding = text_bg_padding
        self.char_limit = 20

        # Define the upper half zone for text placement
        self.text_zone = {"top": 0, "bottom": height // 2, "left": 0, "right": width}

    def wrap_text(self, text):
        """
        Wrap text at character limit while preserving formatting
        """
        if text.startswith("•"):
            indent = "  "
            subsequent_indent = "   "
            text_without_bullet = text[2:].strip()
            wrapped = textwrap.fill(
                text_without_bullet,
                width=self.char_limit,
                subsequent_indent=subsequent_indent,
            )
            return "• " + wrapped
        else:
            return textwrap.fill(text, width=self.char_limit + 5)

    def create_text_with_background(self, text, start_time, duration):
        """
        Create a text clip with a background color and padding

        Args:
            text: The text to display
            start_time: When the text should appear
            duration: How long the text should stay

        Returns:
            A composite clip containing the text and its background
        """
        # Create the main text clip
        text_clip = TextClip(
            text,
            fontsize=self.font_size,
            color=self.text_color,
            font="Arial",
            method="label",
        )

        # Create a slightly larger background clip
        bg_width = text_clip.w + (2 * self.text_bg_padding[0])
        bg_height = text_clip.h + (2 * self.text_bg_padding[1])
        bg_clip = ColorClip(
            size=(bg_width, bg_height), color=self.text_bg_color
        ).set_duration(duration)

        # Combine text and background
        composite = CompositeVideoClip(
            [
                bg_clip,
                text_clip.set_position(
                    (self.text_bg_padding[0], self.text_bg_padding[1])
                ),
            ]
        )

        return composite.set_start(start_time).set_duration(duration).crossfadein(0.5)

    def calculate_vertical_layout(self, wrapped_lines, line_spacing):
        """
        Calculate the total height needed for all lines and their starting y-position
        to achieve vertical centering in the upper half
        """
        total_height = len(wrapped_lines) * line_spacing
        available_height = self.text_zone["bottom"] - self.text_zone["top"]
        start_y = self.text_zone["top"] + (available_height - total_height) // 2
        return start_y

    def create_video(self, output_path):
        """
        Create the final video with centered text in the upper half
        """
        # Create white background
        background = ColorClip(
            size=(self.width, self.height),
            color=(255, 255, 255),
            duration=self.duration,
        )

        line_spacing = self.font_size * 1.5

        for slide in self.slide_content:
            # First, collect all wrapped lines for this slide to calculate total height
            all_wrapped_lines = []
            for line in slide["lines"]:
                wrapped_text = self.wrap_text(line)
                all_wrapped_lines.extend(wrapped_text.split("\n"))

            # Calculate starting y-position for vertical centering
            start_y = self.calculate_vertical_layout(all_wrapped_lines, line_spacing)
            current_y = start_y

            for i, line in enumerate(slide["lines"]):
                start_time = slide["start_times"][i]
                duration = float(slide["end_time"]) - float(start_time)

                wrapped_text = self.wrap_text(line)
                wrapped_lines = wrapped_text.split("\n")

                for wrapped_line in wrapped_lines:
                    # Create text clip with background
                    temp_clip = self.create_text_with_background(
                        wrapped_line, start_time, duration
                    )

                    # Center horizontally and position vertically
                    x_pos = (self.width - temp_clip.w) // 2
                    temp_clip = temp_clip.set_position((x_pos, current_y))

                    self.text_clips.append(temp_clip)
                    current_y += line_spacing

                # Add extra spacing between main items
                current_y += line_spacing * 0.8

        final_video = CompositeVideoClip([background] + self.text_clips)

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


if __name__ == "__main__":
    # Example usage with custom styling
    generator = TextVideoGenerator(
        width=1080,
        height=1920,
        duration=67,
        slide_content=slide_content,
        text_color="white",  # White text
        text_bg_color=(0, 0, 139),  # Dark blue background
        text_bg_padding=(30, 15),  # Comfortable padding around text
    )
    generator.create_video("text_animations.mp4")
