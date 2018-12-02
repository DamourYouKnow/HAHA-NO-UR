# Build
## Instructions
1. Add a file named `auth.json` inside the `config` folder. This file will 
contain your discord application's oauth token and optionally channel IDs for 
logging errors and feedback:
    ```json
    {
        "token": "bottoken",
        "error_log": "00000000000000000",
        "feedback_log": "000000000000000000"
    }
    ```

2. Use pip to install the project's dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Run an instance of 
[MongoDB Server](https://www.mongodb.com/download-center?jmp=homepage#community). 
I'd recommend using the default port for configuration purposes.

4. Run the application:
    ```
    python main.py
    ```

Please note that the database of cards will be empty when you first run the app. 
Card information is retreived from the School Idol Tomoachi API in batches of 
10 cards every 2 minutes. It will take a few update cycles for all of the 
features to function as designed.

