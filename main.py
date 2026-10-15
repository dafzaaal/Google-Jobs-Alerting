import os
import re
import ssl
import json
import glob
import serpapi
import smtplib
import textwrap
import subprocess
from pathlib import Path
from email import encoders 
from dotenv import load_dotenv
from QueryOllama import QueryOllama
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


load_dotenv()
OUT_DIR = Path(os.getenv("DIR"))

def queryJobAPI(job_title: str, location: str) -> list[str]:
    client = serpapi.Client(api_key=os.getenv("SERPAPI_KEY"))
    results = client.search({
    "engine": "google_jobs",
    "q": job_title,
    "location": location,
    "google_domain": "google.ca",
    "hl": "en",
    "gl": "ca"
    })
    return results["jobs_results"]


def safe_name(text: str) -> str:
    # Replace anything that isn't a letter, digit, dot, or dash with "_"
    return re.sub(r"[^\w.\-]+", "_", text).strip("_")


def generateJobDescFiles(jobs: list[dict]) -> None:
    
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for job in jobs:
        title = job["title"]
        company = job["company_name"]
        location = job["location"]
        desc = job.get("description")

        # Include location to avoid collisions between same-title postings
        base = safe_name(f"{title} {company} {location}")[:150]
        path = OUT_DIR / f"{base}.txt"

        with path.open("w", encoding="utf-8") as f:
            f.write(f"{title}\n{company}\n{location}\n\n")
            if desc:
                f.write(textwrap.fill(desc, width=90))
    QueryOllama.CleanJobDescs()


def sendEmailAlerts(title: str, location: str, jobRoleAndLoc: list[str]):
    
    indexed_map = dict(enumerate(jobRoleAndLoc))
    s = ""

    for i, val in indexed_map.items():
        s += f"{i + 1}. {val['title']} at {val['company_name']} \n"

    msg = MIMEMultipart()
    msg["Subject"] = f"Job Postings Alert for: {title} in {location}"
    msg["From"] = os.getenv("SENDER_EMAIL")
    msg["To"] = os.getenv("RECEIVER")
    body = f"""
        \n
        --- Job Roles and Location --- 
        \n
        {s}
    """
    msg.attach(MIMEText(body, 'plain'))

    files = glob.glob(f"{OUT_DIR}/*.txt")

    for file in files:
        try:
            with open(file, "rb") as f: 
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(file)
                )
                msg.attach(part)
        except FileNotFoundError:
            print(f"Error. File '{file}' does not exist or exists but isn't under the /Jobs subfolder.")
            continue

    # Logic to actually send the E-mail
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT")), context=context) as server:
            server.login(os.getenv("EMAIL"), os.getenv("PASSWORD"))
            server.send_message(msg)
    except Exception as e:
        print(f"Exception occured while sending E-mail: {e}")


    
def getJobs():
    with open('data.json') as f:
        job_data = json.load(f)
        f.close()
    
    res = []

    try: 
        for title, location in job_data.items():
            res.extend(queryJobAPI(title, location))
            generateJobDescFiles(res)
            sendEmailAlerts(title, location, res)
            subprocess.run(f'rm $(find {OUT_DIR} -type f -name "*.txt")', shell=True)
            res.clear()
    except:
        raise ValueError("Bad request format.")

    

if __name__ == "__main__":
    getJobs()