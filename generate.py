import re
import os
from random import choice

import mingus.core.keys as keys
import mingus.core.intervals as intervals
import mingus.core.chords as chords
from mingus.containers import Note, NoteContainer, Bar
from mingus.containers.instrument import Instrument, MidiInstrument
from mingus.containers import Track
from mingus.midi import fluidsynth
from mingus.midi.midi_file_out import write_Track
from midi2audio import FluidSynth as M2AFluidSynth
from instruments_consts import PIANO, EPIANO1

PROGRESSION_LENGTH = 2
DEFAULT_SF2 = "./defaults/sf2/GeneralUser_GS_v1.471.sf2"
DEFAULT_OUTPUT_DIR = "./output"

chord_options = [
    chords.minor_seventh,
    chords.major_seventh,
    chords.dominant_seventh,
    chords.minor_major_seventh,
    chords.minor_seventh_flat_five,
    chords.diminished_seventh,
    chords.minor_ninth,
    chords.major_ninth,
    chords.dominant_ninth,
    chords.minor_eleventh,
    chords.eleventh,
    chords.minor_thirteenth,
    chords.major_thirteenth,
    chords.dominant_thirteenth,
    chords.augmented_major_seventh,
    chords.augmented_minor_seventh,
    chords.suspended_seventh,
    chords.suspended_fourth_ninth,
    chords.dominant_flat_ninth,
    chords.dominant_sharp_ninth,
    chords.dominant_flat_five,
    chords.sixth_ninth,
    chords.hendrix_chord,
]


def fix_name(name: str):
    regex = r"^(.*\|..).*"
    name = re.sub(regex, r"\1", name)
    name = name.replace("|", "/")
    return name


def generate_chord():
    key = root = choice(keys.keys)[0]
    chord = choice(chord_options)(root)
    return chord


class Progression:
    def __init__(self, sf2=DEFAULT_SF2, instrument=EPIANO1):
        self._progression = []
        self._tracks = {"harmonic": None, "melodic": None}

        fluidsynth.init(sf2)
        fluidsynth.set_instrument(1, instrument)

    def add_chord(self):
        new_chord = generate_chord()
        container = NoteContainer(new_chord)
        self._progression.append(container)

    def get_progression(self):
        ret = []
        for container in self._progression:
            ret.append(fix_name(choice(container.determine(True))))
        return "|".join(ret)

    def get_chords_notes(self):
        ret = []
        for container in self._progression:
            ret.append(container.get_note_names())
        return ret

    def set_instrument(self, instrument):
        fluidsynth.set_instrument(1, instrument)

    def __len__(self):
        return len(self._progression)

    def generate(self, length=PROGRESSION_LENGTH):
        while len(self) < length:
            self.add_chord()

    def finilize(self):
        self._prepare_harmonic_track()
        self._prepare_melodic_track()

    def _prepare_melodic_track(self):
        arpg = Track()
        for chord in self._progression:
            arp_bar = Bar()
            for note in chord:
                arp_bar.place_notes(note, 16)
            arp_bar.transpose("12", up=False)
            arp_bar.place_rest(4)
            arpg.add_bar(arp_bar)
        self._tracks["melodic"] = arpg

    def _prepare_harmonic_track(self):
        track = Track()
        for chord in self._progression:
            new_bar = Bar()
            new_bar.place_notes(chord, 2)
            new_bar.transpose("12", up=False)
            track.add_bar(new_bar)
        self._tracks["harmonic"] = track

    def play(self, *, melodic=False):
        if melodic:
            fluidsynth.play_Track(self._tracks["melodic"], bpm=60)
        else:
            fluidsynth.play_Track(self._tracks["harmonic"], bpm=60)

    def midi_out(self, file=None):
        full_track = Track()
        for bar in self._tracks["harmonic"].bars:
            full_track.add_bar(bar)
        for bar in self._tracks["melodic"].bars:
            full_track.add_bar(bar)
        write_Track(file, full_track)


def midi_to_wav(infile, outfile="output.wav", *, sf2=DEFAULT_SF2):
    M2AFluidSynth(sf2).midi_to_audio(infile, outfile)


def generate_wav(length=PROGRESSION_LENGTH):
    if not os.path.exists(DEFAULT_OUTPUT_DIR):
        os.makedirs(DEFAULT_OUTPUT_DIR)

    prog = Progression()
    prog.generate()
    prog.finilize()
    print(prog.get_progression())
    print(prog.get_chords_notes())
    # prog.play()
    # prog.play(melodic=True)
    midi_file = os.path.join(DEFAULT_OUTPUT_DIR, "new.mid")
    prog.midi_out(midi_file)
    wav_file = os.path.join(DEFAULT_OUTPUT_DIR, "output.wav")
    midi_to_wav(midi_file, wav_file)
    return wav_file


# class ProgressionGenerator():
