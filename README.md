# Strong Data Project

This project is designed to help you analyze and visualize workout data from the iOS app "Strong", using Streamlit.

Python is far from the first language I reach for - this was developed with heavy use of Github Copilot to smooth out learning curves where I'd normally spend a while in the Python stdlib docs. 

## Running the Project Locally

To run this project locally, follow these steps:

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
