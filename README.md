# Strong Data Project

This project is designed to help you analyze and visualize workout data from the iOS app "Strong", using Streamlit.

Python is far from the first language I reach for - this was developed with heavy use of Github Copilot to smooth out learning curves where I'd normally spend a while in the Python stdlib docs. 

## Running the Project Locally

To run this project locally, follow these steps:

### First time setup (assigning body parts to exercise in parsed data)

#### Customizing Body Parts & Mappings

You can edit the body parts available for mapping in `parse_raw_data.py` by modifying the `BodyPart` enum. For example:

```python
class BodyPart(Enum):
    TRAPS = "Traps"
    NEW_PART = "New Part"
    # ...
```

Any addition to this enum will appear as an option when parsing unknown exercises. Once selected, mappings are stored in exercise_body_part_mapping.json so you only need to assign each exercise once.

#### Using parse_raw_data.py to enter mappings

`parse_raw_data.py` reads a CSV file exported from Strong and creates data structures representing workouts, exercises, and sets. If it encounters an exercise name for which no mapping to a body part exists, it will prompt you on the command line to select one from a list of available parts. Any new mappings are saved to the JSON file in [exercise_body_part_mapping.json](http://_vscodecontentref_/0) for future use.

#### How to Run
1. In a terminal, navigate to the root of this project.
2. Run:
   ```bash
   python src/parse_raw_data.py

### Running the GUI

1. Clone the repository:
    ```bash
    git clone https://github.com/placy2/workout-data-analysis.git
    ```
2. Navigate to the project directory:
    ```bash
    cd workout-data-analysis
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit application pointing to your Strong export data:
    ```bash
    streamlit run src/gui.py -- /path/to/strong.csv
    ```
   Commented code is also provided to set the default in `gui.py` if helpful.




## Further Help

For more information on how to use Streamlit, please refer to the [Streamlit documentation](https://docs.streamlit.io/).
