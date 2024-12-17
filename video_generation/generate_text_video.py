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
    def __init__(self, width, height, duration, slide_content, font_size=70):
        """
        init
        """
        self.width = width
        self.height = height
        self.duration = duration
        # Increased font size to 5% of width (was 3%)
        self.font_size = int(width * 0.05)
        self.slide_content = slide_content
        self.text_clips = []
        self.letter_duration = 0.2
        self.letter_fade_duration = 0.15
        self.quarter_width = width // 2
        self.quarter_height = height // 2
        # Reduced character limit to account for larger font
        self.char_limit = 20

    def wrap_text(self, text):
        """
        Wrap text at character limit, preserving bullet points
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
            # Make headers slightly longer than bullet points
            return textwrap.fill(text, width=self.char_limit + 5)

    @staticmethod
    def get_starting_position(width, height, margin_percentage=0.05):
        """
        Get the starting position for the text in the top left quarter
        """
        x = int(width * margin_percentage)
        y = int(height * margin_percentage)
        return x, y

    def create_background(self, duration, color):
        return ColorClip(
            size=(self.width, self.height),
            color=color,
            duration=duration,
        )

    def create_video(self, output_path):
        background = self.create_background(self.duration, (255, 255, 255))
        x, y = self.get_starting_position(self.width, self.height)
        # Increased line spacing to 1.5 times font size (was 1.2)
        line_spacing = self.font_size * 1.5

        for slide in self.slide_content:
            current_y = y
            for i, line in enumerate(slide["lines"]):
                start_time = slide["start_times"][i]
                duration = float(slide["end_time"]) - float(start_time)

                wrapped_text = self.wrap_text(line)
                wrapped_lines = wrapped_text.split("\n")

                for j, wrapped_line in enumerate(wrapped_lines):
                    line_y = current_y + (j * line_spacing)

                    if line_y + self.font_size > self.quarter_height:
                        continue

                    font_weight = "regular"

                    temp_clip = (
                        TextClip(
                            wrapped_line,
                            fontsize=self.font_size,
                            color="black",
                            font="Arial",
                            method="label",
                        )
                        .set_position((x, line_y))
                        .set_start(start_time)
                        .set_duration(duration)
                        .crossfadein(0.5)
                    )
                    self.text_clips.append(temp_clip)

                # Increased spacing between main items
                current_y += line_spacing * (len(wrapped_lines) + 0.8)

        final_video = CompositeVideoClip([background] + self.text_clips)

        final_video.write_videofile(
            output_path,
            fps=30,
            codec="libx264",
            audio=False,
            preset="medium",
            threads=4,
        )
        if final_video is not None:
            final_video.close()
        if background is not None:
            background.close()


if __name__ == "__main__":
    generator = TextVideoGenerator(
        width=1080, height=1920, duration=66, slide_content=slide_content
    )
    generator.create_video("text_animations.mp4")
