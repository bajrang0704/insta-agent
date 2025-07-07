import os
import random
import logging
from datetime import datetime
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
from config import *

class VideoCreator:
    def __init__(self):
        pass

    def create_video_with_pil_text(self, quote_text, author_text, music_file):
        logging.info("Starting video creation with random effects...")
        try:
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=VIDEO_DURATION_SECONDS
            )
            quote_clip = self.create_text_with_random_effect(
                f'"{quote_text}"', 
                QUOTE_FONT_SIZE, 
                QUOTE_COLOR, 
                'center',
                VIDEO_WIDTH - 300,
                0
            )
            author_clip = self.create_text_with_random_effect(
                f"- {author_text}", 
                AUTHOR_FONT_SIZE, 
                AUTHOR_COLOR, 
                (0, int(VIDEO_HEIGHT * 0.75)),
                VIDEO_WIDTH - 200,
                TEXT_STAGGER_DELAY
            )
            if quote_clip is None or author_clip is None:
                logging.error("Failed to create text clips")
                return None
            audio = AudioFileClip(music_file).set_duration(VIDEO_DURATION_SECONDS)
            final_video = CompositeVideoClip([background, quote_clip, author_clip])
            final_video.audio = audio
            final_video.fps = VIDEO_FPS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_video_{timestamp}.mp4"
            final_video.write_videofile(filename, codec='libx264', audio_codec='aac')
            final_video.close()
            audio.close()
            logging.info(f"Video with random effects created: {filename}")
            if music_file and music_file.startswith("temp_") and os.path.exists(music_file):
                os.remove(music_file)
                logging.info(f"Deleted temporary music file: {music_file}")
            return filename
        except Exception as e:
            logging.error(f"Error creating video with random effects: {e}")
            return None

    def create_video_with_pil_text_and_blur_keyframe(self, quote_text, author_text, music_file, effect):
        """
        Create a video where the quote is strongly blurred at the start and animates to clear.
        The first frame (keyframe) is the blurred quote.
        """
        logging.info(f"Starting video creation with blur keyframe and effect: {effect}...")
        try:
            background = ColorClip(
                size=(VIDEO_WIDTH, VIDEO_HEIGHT),
                color=BACKGROUND_COLOR,
                duration=VIDEO_DURATION_SECONDS
            )
            # 1. Main effect (entire video, no separate keyframe)
            quote_clip = self.create_text_with_effect(
                quote_text, QUOTE_FONT_SIZE, QUOTE_COLOR, 'center', VIDEO_WIDTH - 300, 0, effect, duration=VIDEO_DURATION_SECONDS)
            author_clip = self.create_text_with_effect(
                f"- {author_text}", AUTHOR_FONT_SIZE, AUTHOR_COLOR, (0, int(VIDEO_HEIGHT * 0.75)), VIDEO_WIDTH - 200, TEXT_STAGGER_DELAY, effect, duration=VIDEO_DURATION_SECONDS)
            audio = AudioFileClip(music_file).set_duration(VIDEO_DURATION_SECONDS)
            final_video = CompositeVideoClip([background, quote_clip, author_clip])
            final_video.audio = audio
            final_video.fps = VIDEO_FPS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_video_{timestamp}.mp4"
            final_video.write_videofile(filename, codec='libx264', audio_codec='aac')
            final_video.close()
            audio.close()
            logging.info(f"Video with blur keyframe and effect created: {filename}")
            if music_file and music_file.startswith("temp_") and os.path.exists(music_file):
                os.remove(music_file)
                logging.info(f"Deleted temporary music file: {music_file}")
            return filename
        except Exception as e:
            logging.error(f"Error creating video with blur keyframe and effect: {e}")
            return None

    def create_text_with_effect(self, text, font_size, color, position='center', max_width=None, delay=0, effect='fade', duration=None):
        try:
            base_clip = self.create_text_image(text, font_size, color, position, max_width)
            if base_clip is None:
                return None
            base_clip = base_clip.set_duration(duration) if duration else base_clip
            if effect == 'fade':
                return self.apply_fade_effect(base_clip, delay)
            elif effect == 'blur':
                return self.apply_blur_effect(base_clip, delay)
            elif effect == 'diamond_blur':
                return self.apply_diamond_blur_effect(base_clip, delay)
            else:
                return self.apply_fade_effect(base_clip, delay)
        except Exception as e:
            logging.error(f"Error creating text with effect: {e}")
            return None

    def create_text_with_random_effect(self, text, font_size, color, position='center', max_width=None, delay=0):
        try:
            base_clip = self.create_text_image(text, font_size, color, position, max_width)
            if base_clip is None:
                return None
            effect = random.choice(AVAILABLE_EFFECTS)
            logging.info(f"Applying effect: {effect}")
            if effect == 'fade':
                return self.apply_fade_effect(base_clip, delay)
            elif effect == 'blur':
                return self.apply_blur_effect(base_clip, delay)
            elif effect == 'diamond_blur':
                return self.apply_diamond_blur_effect(base_clip, delay)
            else:
                return self.apply_fade_effect(base_clip, delay)
        except Exception as e:
            logging.error(f"Error creating text with random effect: {e}")
            return None

    def create_text_image(self, text, font_size, color, position='center', max_width=None):
        try:
            img = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            font = None
            font_paths = [
                "fonts/HelveticaNeue-UltraLight.ttf"  # Only use Helvetica Neue Ultra Light
            ]
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    logging.info(f"Using font: {font_path}")
                    break
                except:
                    continue
            if font is None:
                font = ImageFont.load_default()
                logging.warning("Using default font")
            if max_width is None:
                max_width = VIDEO_WIDTH - 200
            def wrap_text(text, font, max_width):
                words = text.split()
                lines = []
                current_line = []
                for word in words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    text_width = bbox[2] - bbox[0]
                    if text_width <= max_width:
                        current_line.append(word)
                    else:
                        if current_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            lines.append(word)
                if current_line:
                    lines.append(' '.join(current_line))
                return lines
            wrapped_lines = wrap_text(text, font, max_width)
            logging.info(f"Text wrapped into {len(wrapped_lines)} lines: {wrapped_lines}")
            line_height = font_size + 15
            total_height = len(wrapped_lines) * line_height
            if position == 'center':
                x = (VIDEO_WIDTH - max_width) // 2
                y = (VIDEO_HEIGHT - total_height) // 2
                y = max(50, min(y, VIDEO_HEIGHT - total_height - 50))
            else:
                x, y = position
            # Draw each line with a much thicker black outline for boldness
            outline_width = max(4, font_size // 8)  # Increased thickness
            outline_color = 'black'
            for i, line in enumerate(wrapped_lines):
                line_y = y + (i * line_height)
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                line_x = (VIDEO_WIDTH - line_width) // 2
                line_x = max(50, min(line_x, VIDEO_WIDTH - line_width - 50))
                # Draw outline
                for ox in range(-outline_width, outline_width+1):
                    for oy in range(-outline_width, outline_width+1):
                        if ox != 0 or oy != 0:
                            draw.text((line_x+ox, line_y+oy), line, font=font, fill=outline_color)
                # Draw main text
                draw.text((line_x, line_y), line, fill=color, font=font)
            img_array = np.array(img)
            clip = ImageClip(img_array, duration=VIDEO_DURATION_SECONDS)
            return clip
        except Exception as e:
            logging.error(f"Error creating text image: {e}")
            return None

    def apply_fade_effect(self, base_clip, delay=0):
        try:
            # More intense: start fully transparent, fade in quickly
            fade_in = base_clip.fadein(TEXT_FADE_IN_DURATION * 0.5)  # Faster fade-in
            fade_out = fade_in.fadeout(TEXT_FADE_OUT_DURATION)
            return fade_out.set_start(delay)
        except Exception as e:
            logging.error(f"Error applying fade effect: {e}")
            return base_clip.set_start(delay)

    def apply_blur_effect(self, base_clip, delay=0):
        try:
            # More intense: start with strong blur, animate to clear
            duration = base_clip.duration
            def blur_dynamic(get_frame, t):
                # Blur is strong at start, 0 at 1s
                max_blur = 20
                blur_amount = max_blur * max(0, 1 - t/1.0)  # 1s to clear
                frame = get_frame(t)
                pil_img = Image.fromarray(frame)
                if blur_amount > 0:
                    blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_amount))
                    return np.array(blurred)
                else:
                    return frame
            blurred = base_clip.fl(blur_dynamic, apply_to=['mask'])
            # No fade in/out, just blur to clear
            return blurred.set_start(delay)
        except Exception as e:
            logging.error(f"Error applying blur effect: {e}")
            return self.apply_fade_effect(base_clip, delay)

    def apply_diamond_blur_effect(self, base_clip, delay=0):
        try:
            # More intense: start with more/larger blurred layers, animate to clear
            duration = base_clip.duration
            def diamond_blur_dynamic(get_frame, t):
                # At t=0, 3 layers of blur, fade to clear by t=1s
                max_blur = [30, 20, 10]
                blur_factors = [max(0, 1 - t/1.0) for _ in max_blur]
                frame = get_frame(t)
                pil_img = Image.fromarray(frame)
                layers = [np.array(pil_img)]
                for b, f in zip(max_blur, blur_factors):
                    if f > 0:
                        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=b * f))
                        layers.append(np.array(blurred) * 0.3)
                # Composite: average the layers
                composite = np.mean(layers, axis=0).astype(np.uint8)
                return composite
            diamond_blurred = base_clip.fl(diamond_blur_dynamic, apply_to=['mask'])
            # No fade in/out, just blur to clear
            return diamond_blurred.set_start(delay)
        except Exception as e:
            logging.error(f"Error applying diamond blur effect: {e}")
            return self.apply_fade_effect(base_clip, delay)

    def pil_blur_imageclip(self, image_clip, blur_radius):
        # Convert ImageClip to PIL Image, apply GaussianBlur, return new ImageClip
        img = image_clip.get_frame(0)
        pil_img = Image.fromarray(img)
        blurred = pil_img.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        return ImageClip(np.array(blurred)).set_duration(image_clip.duration) 