"""Contains all core data models (Workout, Exercise, ExerciseSet, BodyPart) used across the app."""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional

class BodyPart(Enum):
    """Class representing different body parts for exercises."""
    TRAPS = "Traps"
    FRONT_DELTS = "Front Delts"
    SIDE_DELTS = "Side Delts"
    REAR_DELTS = "Rear Delts"
    BACK_UPPER = "Back (Upper)"
    BACK_LATS = "Back (Lats)"
    ABS = "Abs"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    PECS = "Pecs"
    FOREARMS = "Forearms"
    GLUTES = "Glutes"
    HAMSTRINGS = "Hamstrings"
    QUADS = "Quads"
    CALVES = "Calves"
    TIBIALIS = "Tibialis"
    CARDIO = "Cardio"
    OTHER = "Other"

# specific set of an exercise within a workout
# Has a quirk with 'set_number' because of warmups, drop sets, and failure sets.
# These don't follow the regular numeric order. For now we will just store the raw string.
# They are always entered as set_number 0 in the ExerciseSet,
# but currently only total number of sets is tracked in the GUI
# Future work should expose a "set type" field that can be "regular", "warmup",
# "drop", or "failure" to allow for more nuanced analysis of set types
@dataclass
class ExerciseSet:
    """Class representing a specific set of an exercise within a workout."""
    workout: 'Workout'
    date: str
    set_number: str
    weight: float
    reps: int
    notes: str = ""

# specific exercise (across all workouts)
@dataclass
class Exercise:
    """Class representing a specific exercise. Contains multiple sets across different workouts."""
    name: str
    exercise_sets: List[ExerciseSet] = field(default_factory=list)
    body_part: Optional[BodyPart] = None

    @property
    def number_of_times_performed(self):
        """Returns the total number of times this exercise has been performed."""
        return len(self.exercise_sets)

    @property
    def last_performed(self):
        """Returns the date of the most recent set performed for this exercise, or None."""
        if not self.exercise_sets:
            return None
        return max(s.date for s in self.exercise_sets)



# single dated workout session
# contains multiple exerciseSets
@dataclass
class Workout:
    """Class representing a single workout session. Contains exercises, which contain sets."""
    name: str
    date: str
    duration: float  # in minutes
    notes: str = ""
    exercises: List[Exercise] = field(default_factory=list)

    @property
    def number_of_exercises(self):
        """Returns the total number of exercises in this workout."""
        return len(self.exercises)

    @property
    def number_of_exercise_sets(self):
        """Returns the total number of exercise sets in this workout."""
        return sum(len(e.exercise_sets) for e in self.exercises)

    @property
    def total_weight_lifted(self):
        """Returns the total weight lifted in this workout."""
        return sum(sum(s.weight for s in e.exercise_sets) for e in self.exercises)

    @property
    def total_reps_performed(self):
        """Returns the total number of reps performed in this workout."""
        return sum(sum(s.reps for s in e.exercise_sets) for e in self.exercises)
