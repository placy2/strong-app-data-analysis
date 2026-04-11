# Contains all core data models (Workout, Exercise, ExerciseSet, BodyPart) used across the app.
from enum import Enum

class BodyPart(Enum):
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

# single dated workout session
# contains multiple exerciseSets
class Workout:
    def __init__(self, name, date, duration, notes=""):
        self.name = name
        self.date = date
        self.duration = duration
        self.notes = notes
        self.exercises = []

    @property
    def number_of_exercises(self):
        return len(self.exercises)

    @property
    def number_of_exercise_sets(self):
        return sum(len(e.exercise_sets) for e in self.exercises)

    @property
    def total_weight_lifted(self):
        return sum(sum(s.weight for s in e.exercise_sets) for e in self.exercises)

    @property
    def total_reps_performed(self):
        return sum(sum(s.reps for s in e.exercise_sets) for e in self.exercises)

# specific exercise (across all workouts)
class Exercise:
    def __init__(self, name, body_part=None):
        self.name = name
        self.exercise_sets = []
        # Randomly assign an enum value if not provided
        self.body_part = body_part

    @property
    def number_of_times_performed(self):
        return len(self.exercise_sets)

    @property
    def last_performed(self):
        if not self.exercise_sets:
            return None
        return max(s.date for s in self.exercise_sets)

# specific set of an exercise within a workout
# Has a quirk with 'set_number' because of warmup sets, drop sets, and failure sets that don't follow the regular numeric order. For now we will just store the raw string and handle it in the parsing logic.
# They are always entered as set_number 0 in the ExerciseSet, but currently only total number of sets is tracked in the GUI
# Future work should expose a "set type" field that can be "regular", "warmup", "drop", or "failure" to allow for more nuanced analysis of set types
class ExerciseSet:
    def __init__(self, workout, date, set_number, weight, reps, notes=""):
        self.workout = workout
        self.date = date
        self.set_number = set_number
        self.weight = weight
        self.reps = reps
        self.notes = notes