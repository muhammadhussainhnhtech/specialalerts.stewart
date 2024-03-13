import uvicorn
from fastapi import FastAPI
from script.script import start_scrapping

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/get-results/")
def read_root(first_name: str = None, last_name: str = ""):
    if first_name is None :
        return "first_name is required"
    name= {
        'fname': first_name,
        'lname': last_name
    }
    data= start_scrapping(name)

    return data







if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)