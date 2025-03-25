import csv
from datetime import datetime

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

class Exercise:
    def __init__(self, name):
        self.name = name
        self.exercise_sets = []

    @property
    def number_of_times_performed(self):
        return len(self.exercise_sets)

    @property
    def last_performed(self):
        if not self.exercise_sets:
            return None
        return max(s.date for s in self.exercise_sets)

class ExerciseSet:
    def __init__(self, workout, date, set_number, weight, reps, notes=""):
        self.workout = workout
        self.date = date
        self.set_number = set_number
        self.weight = weight
        self.reps = reps
        self.notes = notes

def parse_duration(duration_str):
    # Examples of duration_str: "53m", "1h 31m", "32h 5m"
    parts = duration_str.split()
    total_minutes = 0
    for part in parts:
        if "h" in part:
            hrs = int(part.replace("h", ""))
            total_minutes += hrs * 60
        elif "m" in part:
            mins = int(part.replace("m", ""))
            total_minutes += mins
    return total_minutes

def parse_csv(file_path):
    workouts = {}
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_str = row["Date"]
            workout_name = row["Workout Name"]
            duration_str = row["Duration"]
            exercise_name = row["Exercise Name"]
            set_order = row["Set Order"]
            weight = row["Weight"]
            reps = row["Reps"]
            notes = row["Notes"] or ""
            workout_notes = row["Workout Notes"] or ""

            # Parse fields
            date_parsed = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            set_number = int(set_order) if set_order else 1
            weight = int(float(weight)) if weight else 0
            reps = int(reps) if reps else 0
            duration = parse_duration(duration_str) if duration_str else 0

            # Get or create the Workout
            workout_key = (date_str, workout_name)
            if workout_key not in workouts:
                workout_obj = Workout(workout_name, date_parsed, duration, workout_notes)
                workouts[workout_key] = workout_obj
            else:
                workout_obj = workouts[workout_key]

            # Get or create the Exercise
            exercise_obj = None
            for e in workout_obj.exercises:
                if e.name == exercise_name:
                    exercise_obj = e
                    break
            if exercise_obj is None:
                exercise_obj = Exercise(exercise_name)
                workout_obj.exercises.append(exercise_obj)

            # Create the ExerciseSet
            exercise_set = ExerciseSet(
                workout=workout_obj.name,
                date=date_parsed,
                set_number=set_number,
                weight=weight,
                reps=reps,
                notes=notes,
            )
            exercise_obj.exercise_sets.append(exercise_set)

    return list(workouts.values())

if __name__ == "__main__":
    file_path = "/Users/parkerlacy/coding/strong-data/data/raw/strong.csv"
    parsed_workouts = parse_csv(file_path)
    print(f"Parsed {len(parsed_workouts)} workouts.")