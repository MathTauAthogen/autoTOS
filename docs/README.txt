To set up the test server, just use:

$ python3 mock-api.py

The mock testing API will give one of three responses:

1. If the input contains the word "blank", it will return no classes.
2. If the input contains the word "error", it will purposely error.
3. Otherwise, it will return the JSON response in 'mock-response.json'

The 'mock-api.py' also spins up the website (frontend) at
http://localhost:3000.

IMPORTANT: when changing from testing to production, be sure to change
the API_URL variable at the top of js/scripts.js.
