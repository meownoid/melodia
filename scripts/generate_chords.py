import argparse
from dataclasses import dataclass
from typing import List

indent = ' ' * 4

file_template = """
# DO NOT EDIT! This file is auto generated by scripts/generate_chords.py.
from typing import Union, Tuple, Optional

from melodia.core import Tone, Note, Signature


def _get_parameters(
        base: Union[int, str, Tone, Note],
        duration: Union[Tuple[int, int], Signature, None] = None,
        velocity: Optional[float] = None
) -> Tuple[Tone, Signature, float]:
    if isinstance(base, int):
        base_tone = Tone(base)
    elif isinstance(base, str):
        base_tone = Tone.from_notation(base)
    elif isinstance(base, Tone):
        base_tone = base
    elif isinstance(base, Note):
        base_tone = base.tone
    else:
        raise ValueError('base must be int, str, Tone or Note')

    if duration is None:
        if isinstance(base, Note):
            base_duration = base.duration
        else:
            base_duration = Signature(1, 4)
    else:
        base_duration = duration

    if velocity is None:
        if isinstance(base, Note):
            base_velocity = base.velocity
        else:
            base_velocity = 0.75
    else:
        base_velocity = velocity

    return base_tone, base_duration, base_velocity


{functions}
"""

function_template = """
def {name}(
        base: Union[int, str, Tone, Note],
        duration: Union[Tuple[int, int], Signature, None] = None,
        velocity: Optional[float] = None
) -> {return_type}:
    \"\"\"
    This function generates {full_name} chord.

    :param base: base tone (can be integer, string, ~`melodia.core.tone.Tone` or ~`melodia.core.note.Note`)
    :param duration: duration of the chord
    :param velocity: velocity of the chord
    :return: tuple of {number} notes
    \"\"\"
    base_tone, base_duration, base_velocity = _get_parameters(base, duration, velocity)

    return {return_statement}
"""


@dataclass(frozen=True)
class Chord:
    name: str
    full_name: str
    notation: List[int]


chords = [
    Chord('major,maj', 'Major Triad', [0, 4, 7]),
    Chord('minor,min', 'Minor Triad', [0, 3, 7]),
    Chord('augmented,aug', 'Augmented Triad', [0, 4, 8]),
    Chord('diminished,dim', 'Diminished Triad', [0, 3, 6]),

    Chord('suspended4,sus4', 'Suspended Fourth', [0, 5, 7]),
    Chord('suspended2,sus2', 'Suspended Second', [0, 2, 7]),

    Chord('major7,maj7', 'Major Seventh', [0, 4, 7, 11]),
    Chord('minor7,min7', 'Minor Seventh', [0, 3, 7, 10]),
    Chord('dominant7,dom7', 'Dominant Seventh', [0, 4, 7, 10]),
    Chord('dominant7b5,dom7b5', 'Dominant Seventh Flat Five', [0, 4, 6, 10]),
    Chord('diminished7,dim7', 'Diminished Seventh', [0, 3, 6, 9]),
    Chord('minor7b5,min7b5', 'Half Diminished Seventh', [0, 3, 6, 10]),
    Chord('diminished_major7', 'Diminished Major Seventh', [0, 3, 6, 11]),
    Chord('minor_major7', 'Minor Major Seventh', [0, 3, 7, 11]),
    Chord('augmented_major7,major7s5,maj7s5', 'Augmented Major Seventh', [0, 4, 8, 11]),
    Chord('augmented_minor7,augmented7,aug7', 'Augmented Minor Seventh', [0, 4, 8, 10]),

    Chord('major9,maj9', 'Major Ninth', [0, 4, 7, 11, 14]),
    Chord('minor9,min9', 'Minor Ninth', [0, 3, 7, 10, 14]),
    Chord('dominant9,dom9', 'Dominant Ninth', [0, 4, 7, 10, 14]),
    Chord('dominant_minor9,min7b9', 'Dominant Minor Ninth', [0, 4, 7, 10, 13]),
    Chord('minor69,min69', '6/9', [0, 4, 7, 9, 14]),
    Chord('added9,add9', 'Added Ninth', [0, 4, 14]),

    Chord('major11,maj11', 'Major Eleventh', [0, 4, 7, 11, 14, 17]),
    Chord('minor11,min11', 'Minor Eleventh', [0, 3, 7, 10, 14, 17]),
    Chord('dominant11,dom11', 'Dominant Eleventh', [0, 4, 7, 10, 14, 17]),
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', help='output file', type=str)
    args = parser.parse_args()

    functions: List[str] = []

    for chord in chords:
        return_type = f'Tuple[{", ".join(["Note"] * len(chord.notation))}]'
        note_statements = []

        for n in chord.notation:
            if n == 0:
                statement = 'Note(base_tone, base_duration, base_velocity)'
            elif n > 0:
                statement = f'Note(base_tone.transposed(+{abs(n)}), base_duration, base_velocity)'
            else:
                statement = f'Note(base_tone.transposed(-{abs(n)}), base_duration, base_velocity)'

            note_statements.append(statement)

        return_statement = f'(\n{indent}{indent}' + f',\n{indent}{indent}'.join(note_statements) + f'\n{indent})'

        for name in chord.name.split(','):
            functions.append(
                function_template.strip().format(
                    name=name.strip(),
                    full_name=chord.full_name,
                    number=len(chord.notation),
                    return_type=return_type,
                    return_statement=return_statement
                )
            )

    functions_formatted = '\n\n\n'.join(functions)

    with open(args.output, 'w') as f:
        f.write(file_template.strip().format(functions=functions_formatted) + '\n')


if __name__ == '__main__':
    main()
