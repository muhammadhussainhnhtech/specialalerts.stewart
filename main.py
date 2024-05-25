import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from script.script import start_scrapping
from script.scrap_priorfile import start_priorfile_scrapping
from script.scrap_nyc_property_poral import start_nyc_scrapping
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/get-results/")
def read_root(first_name: str = None, last_name: str = "", response: Response = None):
    if first_name is None :
        response.status_code= 400
        return "first_name is required"
    name= {
        'fname': first_name,
        'lname': last_name
    }
    data= start_scrapping(name)

    return data


@app.get("/get-priorfile-results/")
def read_root(street_address: str= None, city: str= None, postal_code:str=None, response: Response = None):
    if not street_address and not city and not postal_code:
        response.status_code= 400
        return {
            "status": False,
            "message":"street_address or city or postal_code any 1 key is required"
            }
    
    params= {
        "street_address":street_address if street_address else "",
        "city": city if city else "",
        "postal_code": postal_code if postal_code else ""
    }
    data= start_priorfile_scrapping(params)

    return data




@app.get("/get-nycportal-results/")
def read_root(address: str= None, response: Response = None):
    if not address :
        response.status_code= 400
        return {
            "status": False,
            "message":"address key is required"
            }

    data= start_nyc_scrapping(address)

    return data





if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)