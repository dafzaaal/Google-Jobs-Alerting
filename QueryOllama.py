import os
import glob
import subprocess
from ollama import Client
from dotenv import load_dotenv

load_dotenv()


class QueryOllama:

    @staticmethod
    def Query(job_desc: str) -> str:

        client = Client(host='https://ollama.com', headers={'Authorization': 'Bearer ' + os.getenv("OLLAMA_API_KEY")})

        messages = [
            {
                'role': 'user',
                'content': f"""Given the job description below attached at the bottom, simplify it, return the company name, position name, location and job duties/responsibilities and qualifications in the format below. \n\n\n\n  
                Company Name 
                Position Name 
                Location 
                \n\n 
                ------ JOB DESCRIPTION ------ \n\n
                ----- QUALIFICATIONS ----- \n\n
                
                Job Description attached below: \n\n
                {job_desc}
                """
            },
        ]

        response = ""

        for part in client.chat('gemma4:31b-cloud', messages=messages, stream=True):
            response += part.message.content

        return response
        
    @staticmethod
    def CleanJobDescs():

        dirPath = os.getenv("DIR")
        jobs = glob.glob(f"{dirPath}/*.txt")

        for i in range(len(jobs)):
            jobs[i] = jobs[i].replace(f"{dirPath}/", "")

        for job in jobs:
            with open(f"{dirPath}/{job}", "r+", encoding="utf-8") as f:
                res = QueryOllama.Query(f.read())
                f.seek(0)
                f.truncate(0)
                f.write(res)

                
