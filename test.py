import os
import time
from pathlib import Path
import matchering as match
from lib_v5 import spec_utils
from gui_data.constants import *


TIME_WINDOW_MAPPER = {
    "None": None,
    "1": [0.0625],
    "2": [0.125],
    "3": [0.25],
    "4": [0.5],
    "5": [0.75],
    "6": [1],
    "7": [2],
    "Shifts: Low": [0.0625, 0.5],
    "Shifts: Medium": [0.0625, 0.125, 0.5],
    "Shifts: High": [0.0625, 0.125, 0.25, 0.5],
    # "Shifts: Very High": [0.0625, 0.125, 0.25, 0.5, 0.75, 1],
}

INTRO_MAPPER = {
    "Default": [10],
    "1": [8],
    "2": [6],
    "3": [4],
    "4": [2],
    "Shifts: Low": [1, 10],
    "Shifts: Medium": [1, 10, 8],
    "Shifts: High": [1, 10, 8, 6, 4],
}

VOLUME_MAPPER = {
    "None": (0, [0]),
    "Low": (-4, range(0, 8)),
    "Medium": (-6, range(0, 12)),
    "High": (-6, [x * 0.5 for x in range(0, 25)]),
    "Very High": (-10, [x * 0.5 for x in range(0, 41)]),
}
# "Max": (-10, [x * 0.3 for x in range(0, int(20 / 0.3) + 1)])}

NONE_P = "None"
VLOW_P = "Shifts: Very Low"
LOW_P = "Shifts: Low"
MED_P = "Shifts: Medium"
HIGH_P = "Shifts: High"
VHIGH_P = "Shifts: Very High"
VMAX_P = "Shifts: Maximum"

PHASE_SHIFTS_OPT = {
    NONE_P: 190,
    VLOW_P: 180,
    LOW_P: 90,
    MED_P: 45,
    HIGH_P: 20,
    VHIGH_P: 10,
    VMAX_P: 1,
}


class AudioTools:

    def __init__(self, audio_tool):
        time_stamp = round(time.time())
        self.audio_tool = audio_tool
        self.main_export_path = Path(root.export_path_var.get())
        self.wav_type_set = root.wav_type_set
        self.is_normalization = root.is_normalization_var.get()
        self.is_testing_audio = (
            f"{time_stamp}_" if root.is_testing_audio_var.get() else ""
        )
        self.save_format = lambda save_path: save_format(
            save_path, root.save_format_var.get(), root.mp3_bit_set_var.get()
        )
        self.align_window = TIME_WINDOW_MAPPER[root.time_window_var.get()]
        self.align_intro_val = INTRO_MAPPER[root.intro_analysis_var.get()]
        self.db_analysis_val = VOLUME_MAPPER[root.db_analysis_var.get()]
        self.is_save_align = root.is_save_align_var.get()  #
        self.is_match_silence = root.is_match_silence_var.get()  #
        self.is_spec_match = root.is_spec_match_var.get()

        self.phase_option = root.phase_option_var.get()  #
        self.phase_shifts = PHASE_SHIFTS_OPT[root.phase_shifts_var.get()]

    def align_inputs(
        self,
        audio_inputs,
        audio_file_base,
        audio_file_2_base,
        command_Text,
        set_progress_bar,
    ):
        audio_file_base = f"{self.is_testing_audio}{audio_file_base}"
        audio_file_2_base = f"{self.is_testing_audio}{audio_file_2_base}"

        aligned_path = os.path.join(
            "{}".format(self.main_export_path),
            "{}_(Aligned).wav".format(audio_file_2_base),
        )
        inverted_path = os.path.join(
            "{}".format(self.main_export_path),
            "{}_(Inverted).wav".format(audio_file_base),
        )

        spec_utils.align_audio(
            audio_inputs[0],
            audio_inputs[1],
            aligned_path,
            inverted_path,
            self.wav_type_set,
            self.is_save_align,
            command_Text,
            self.save_format,
            align_window=self.align_window,
            align_intro_val=self.align_intro_val,
            db_analysis=self.db_analysis_val,
            set_progress_bar=set_progress_bar,
            phase_option=self.phase_option,
            phase_shifts=self.phase_shifts,
            is_match_silence=self.is_match_silence,
            is_spec_match=self.is_spec_match,
        )

    def match_inputs(self, audio_inputs, audio_file_base, command_Text):

        target = audio_inputs[0]
        reference = audio_inputs[1]

        command_Text(f"Processing... ")

        save_path = os.path.join(
            "{}".format(self.main_export_path),
            "{}_(Matched).wav".format(f"{self.is_testing_audio}{audio_file_base}"),
        )

        match.process(
            target=target,
            reference=reference,
            results=[
                match.save_audiofile(save_path, wav_set=self.wav_type_set),
            ],
        )

        self.save_format(save_path)

    def combine_audio(self, audio_inputs, audio_file_base):
        spec_utils.combine_audio(
            audio_inputs,
            os.path.join(
                self.main_export_path, f"{self.is_testing_audio}{audio_file_base}"
            ),
            self.wav_type_set,
            save_format=self.save_format,
        )

    def pitch_or_time_shift(self, audio_file, audio_file_base):
        is_time_correction = True
        rate = (
            float(root.time_stretch_rate_var.get())
            if self.audio_tool == TIME_STRETCH
            else float(root.pitch_rate_var.get())
        )
        is_pitch = False if self.audio_tool == TIME_STRETCH else True
        if is_pitch:
            is_time_correction = True if root.is_time_correction_var.get() else False
        file_text = TIME_TEXT if self.audio_tool == TIME_STRETCH else PITCH_TEXT
        save_path = os.path.join(
            self.main_export_path,
            f"{self.is_testing_audio}{audio_file_base}{file_text}.wav",
        )
        spec_utils.augment_audio(
            save_path,
            audio_file,
            rate,
            self.is_normalization,
            self.wav_type_set,
            self.save_format,
            is_pitch=is_pitch,
            is_time_correction=is_time_correction,
        )
