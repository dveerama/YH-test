from fastapi import FastAPI, Request, Response, status
import asyncpg
import asyncio
import json
import datetime
import random
import string
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env when running locally
DB_URL = os.getenv("DATABASE_URL")
app= FastAPI()



async def run():
    con = await asyncpg.connect(DB_URL)
    try:
        result = await con.fetchrow(
        'SELECT * FROM test ')
        print(result)
    except:
        print("fetchrow error")
    
    try:
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5,20)))
        await con.execute('''
        INSERT INTO test(test_timestamp,random_int,random_string) VALUES($1,$2,$3)
        ''', str(datetime.datetime.now()),random.randint(0,1000000),random_string)
    except:
        print("insert into error")
        
    
    await con.close()


@app.post("/")
async def test_pg_connect(request:Request):
    await run()


    
@app.post("/participants")
async def tally_webhook(request:Request):
    try:
        
        payload = await request.json()
        print(json.dumps(payload,indent=2))
        first_name = payload["data"]["fields"][0]["value"]
        last_name = payload["data"]["fields"][1]["value"]
        email = payload["data"]["fields"][2]["value"]
        school = payload["data"]["fields"][3]["value"]
        
    
        
    except:
        print("BAD tally connection") #add more exception handling later
    try:
        con = await asyncpg.connect(DB_URL)
        await con.execute(" INSERT INTO participants(email, first_name,last_name,school) VALUES($1, $2, $3, $4)", email, first_name, last_name, school)
    
        await con.close()
        return {"status": "success"}
    except:
        print("BAD pg connection") #add more exception handling later
        
@app.post("/participant-score")
async def tally_score_webhook(request:Request):
    try:
        
        payload = await request.json()
        #print(json.dumps(payload,indent=2))
        email = payload["data"]["fields"][0]["value"]
        source = payload["data"]["fields"][1]["value"][0]
        skill_code= payload["data"]["fields"][2]["value"][0]
        awareness_score= payload["data"]["fields"][3]["value"]
        competence_score = payload["data"]["fields"][4]["value"]
        buy_in_score = payload["data"]["fields"][5]["value"]
        
        if source == "c21e40e8-4e05-4949-9aca-5ecef9425190":
            source = "Coaching"
        elif source == "5a283fe0-227b-44e5-a582-1a012a176e98":
            source = "Workshop"
        elif source == "a6e5ed70-9c81-47a6-949a-c16b42c88b36":
            source = "Shadowing"
        
        if skill_code == "2254accb-de1f-486b-8944-1adf93047b58":
            skill_code = "1.0"
        elif skill_code == "812d319d-c80e-4f2f-b821-a05ef5e8f196":
            skill_code = "1.1"
        elif skill_code == "504487ec-336c-43c1-958d-ea31113211be":
            skill_code = "1.2"
        elif skill_code == "15160b6b-6360-4809-b69e-138b69aa1016":
            skill_code = "1.3"
        elif skill_code == "de74651d-9842-43b4-93af-f2b0a4ea533b":
            skill_code = "2.0"
        
        score_date = str(datetime.datetime.now())
        
       
        print("email: " + email + " source: " + source + " score_date: " + score_date + " skill code: "+ skill_code + " awareness_score: " + str(awareness_score) + " competence_score: " + str(competence_score)+ " buy_in_score: "+ str(buy_in_score))
    except:
        print("tally connection bad") #add more exception handling later
    
    try:
        con = await asyncpg.connect(DB_URL)
        #await con.execute('''
        #INSERT INTO participant_scores(participant_email,source_of_score,date_of_scoring,skill_code,awareness_score,competence_score,buy_in_score) VALUES($1,$2,$3,$4,$5,$6,$7)
        #''', email,source,score_date,skill_code,str(awareness_score),str(competence_score),str(buy_in_score))
        
        await con.execute('''
        INSERT INTO participant_scores(participant_email,source_of_score,date_of_scoring,skill_code,awareness_score,competence_score,buy_in_score) VALUES($1,$2,$3,$4,$5,$6,$7)
        ''', email,source,score_date,skill_code,awareness_score,competence_score,buy_in_score)
        await con.close()
        return {"status": "success"}
    except:
         print("pg connection BAD") #add more exception handling later
