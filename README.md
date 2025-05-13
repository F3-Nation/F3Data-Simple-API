# F3Data-Simple-API
Quick and dirty way to get map/workout data out

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Set up environment variables in the `config.py` file:

3. Run the application:
```bash
python main.py
```

## API Endpoints

- GET /: Returns a welcome message and health check
- GET /regions/count: Returns the count of regions
- GET /weeklyworkouts/count: Returns the count of weekly workouts
