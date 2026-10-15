# Google-Jobs-Alerting
A Python project which leverages the Google Job Board API, Ollama and SMTP to send the user e-mail notifications regarding specified position names and locations directly to their inbox. Could be used in tandem with a shceduler (like cron) to send automated alerts for new job postings.

# How to Use
Before running the application, you need to specify a few env variables. I load them into the project via the dotenv library in python. Begin by installing the pip packages required using the requirements.txt file present: `pip install -r requirements.txt` (ensure your working directory is where the requirements.txt file is). A templated .env file is includes, all values which are required are indicated as so. A couple things you will need...

1. An Serpapi API key, this is used to query the Google Job Boards and return jobs matching the search criteria
2. A dummy G-Mail account, this is going to be the dummy account which sends you the notification with the job details and .txt files
3. An Ollama API key, I use the Ollama free-tier cloud based models to essentially re-format the job descriptions to make the more human readable
4. Reciever, this is you or more precisely the user you want receiving the e-mail notification
5. DIR or directory, this is the directory where the generated job descriptions will live (don't worry the program will clean them up but we need to specify a location to which they will be stored)
6. Password, this refers to the app password for your dummy gmail account, this is used by the SMTP server to authenticate the account. You can generate one in the privacy settings of your gmail account.
