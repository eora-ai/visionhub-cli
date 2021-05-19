from moviepy.editor import AudioFileClip
from moviepy.audio.fx import all as afx


class MelodyMixer:
    """
    Retrieves audio from a file by chunks fitting video's duration and FPS
    """
    def __init__(self, melody_path):
        """
        :param melody_path: path to audio file: can be .mp3, .wav or other supported by MoviePy
        """
        self._audio = AudioFileClip(melody_path)
        self._audio_iter = None
        self._audio_fps = self._audio.fps
        self._video_fps = 30
        self._duration = 0

    def reset(self, video_fps, duration):
        """
        Resets audio clip to start chunks retrieval from the beginning
        :param video_fps: input video's FPS
        :param duration: input video's duration (in seconds)
        :return:
        """
        # shallow copy of the audio, resets state of the clip such as seek's pointer
        cur_audio = self._audio.copy()
        # set end of the audio clip to fade out accordingly to the video's duration
        cur_audio = cur_audio.set_end(duration)
        # fade out volume of the audio at the last 2 seconds
        cur_audio = afx.audio_fadeout(cur_audio, duration=2)
        chunk_size = self._audio_fps // video_fps
        # prepare an iterator for the updated audio
        self._audio_iter = cur_audio.iter_chunks(chunksize=chunk_size)

        self._video_fps = video_fps
        self._duration = duration

    def next_sound_chunk(self):
        try:
            sound = next(self._audio_iter)
        except StopIteration:
            # in case the audio is finished start from the beginning
            self.reset(self._video_fps, self._duration)
            sound = next(self._audio_iter)

        return sound
