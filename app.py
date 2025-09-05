from fastapi import FastAPI,Path,Query,HTTPException
import uvicorn # web server for fast api    nginx ---> uvicorn -----> asgi-----> db/ml code
import json

app = FastAPI()
p = set()

# Absolute path to patient.json
json_path = r"C:\Users\Administrator\Desktop\revision\fast\patient.json"

def load_dataset():
    with open(json_path, "r", encoding="utf-8") as f:
        a = json.load(f)
        return a 

load_dataset()
@app.get("/")
def base():
    return {"lets help patient "}

#R ---> Read
@app.get("/view/")
def all_patient(
    
    sort_by : str = Query(...,description='sort on the basis of age as default'),
    order: str = Query('asc',description = 'ascending')
):
    cur = load_dataset()
    if order == 'asc':
        r = False
    elif order == 'desc':
        r= True
    else:
        raise HTTPException(400,'BAD QUERY')
        
    if sort_by not in ['age','gender']:
        raise HTTPException(400,'BAD QUERY')
           
    sorted_cur = sorted(cur.items(),key = lambda x:x[1][sort_by],reverse=r )
    return sorted_cur

@app.get("/exact/{id}")
def exact_patient(
    id:str = Path(...,description = 'path is basically just constraints and description of parameter',example = 'P005')):
   
    b = load_dataset()
    
    if id not in b:
        raise HTTPException(status_code = 404 ,detail = 'no such patient')
    else:
        return b[id]
    
#C ---> Create
from pydantic import BaseModel, Field, field_validator
import json
from fastapi import FastAPI, HTTPException

class contacts(BaseModel):
    phone:  str
    email: str
    
    
class inside(BaseModel):
    name : str = Field(max_length=60)
    age : int  = Field(lt = 200,gt = 0)
    gender : str 
    blood_group: str
    contact: contacts 
    address:str
    medical_history: list[str]
    current_medications : list[str]
    allergies:list[str]
    last_visit: str
    
    
    #@computed_field,EmailStr,model_validator,field_validator
    
    @field_validator('gender')
    @classmethod
    def name_validation(cls,g):
        valid_gender = {'Male','Female'}
        if g in valid_gender:
            return g
        else: 
             raise ValueError('Gender acn only be Male or Female')
         


    @field_validator('blood_group')
    @classmethod
    def blood_group_validation(cls, bg):
        valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if bg in valid_blood_groups:
            return bg
        raise ValueError('Invalid blood group. Must be one of: ' + ', '.join(valid_blood_groups))



class new_patient(BaseModel):
    key : str
    val : inside
        
            
@app.post('/create')
def create(patient:new_patient):
    
    try :
        with open(json_path,'r') as  f:      
            data = json.load(f)  
    
    except FileNotFoundError:
        data = {} 
        
    # CORRECT: This gets data from the request
    key = patient.key
    value = patient.val.model_dump()
                
    if key in data.keys():
        raise HTTPException(status_code=400, detail='Patient already present')
    else:
        data[key] = value
            
    # Write back to file
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)
    
     
    return {
        "message": "Patient created successfully", 
        "patient_key": key,
        "patient_name": value["name"]
    }
            
            
# update --->
from typing import Optional

class contacts(BaseModel):
    phone:   Optional[str] = None
    email:  Optional[str] = None
    
    
class inside(BaseModel):
    name: Optional[str] = Field(None, max_length=60)
    age : Optional[int]  = Field(None,lt = 200,gt = 0)
    gender : Optional[str] = None
    blood_group:  Optional[str] = None
    contact: Optional[contacts]  = None
    address: Optional[str] = None
    medical_history: Optional[list[str]] = None
    current_medications : Optional[list[str]] = None
    allergies:Optional[list[str]] = None
    last_visit: Optional[str] = None
    
    
    #@computed_field,EmailStr,model_validator,field_validator
    
    @field_validator('gender')
    @classmethod
    def name_validation(cls,g):
        if g is None:  # Allow None values
            return g
        valid_gender = {'Male','Female'}
        if g in valid_gender:
            return g
        else: 
             raise ValueError('Gender acn only be Male or Female')
         


    @field_validator('blood_group')
    @classmethod
    def blood_group_validation(cls, bg):
        if bg is None:  # Allow None values
            return bg
        valid_blood_groups = {'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'}
        if bg in valid_blood_groups:
            return bg
        raise ValueError('Invalid blood group. Must be one of: ' + ', '.join(valid_blood_groups))



class new_patient(BaseModel):
    key : str
    val : inside
        
            

@app.post('/update/{update_id}')
def update(
    update_id: str = Path(..., description="Patient ID to update", example="P001"),
    new_data: new_patient = None  # Use Pydantic model for validation
):

    with open(json_path,'r') as f:
        data =json.load(f) 
        
    if update_id not in data.keys():
        raise HTTPException(status_code=404, detail='ID not available')

    
    og_data = data[update_id] 
    #------
     # Convert the new data to dict and filter out None values
    update_dict = new_data.val.model_dump(exclude_none=True)  # Only include non-None values
    
    # Handle nested contact updates properly
    if 'contact' in update_dict and update_dict['contact'] is not None:
        if 'contact' not in og_data:
            og_data['contact'] = {}
        # Merge contact fields
        for contact_key, contact_value in update_dict['contact'].items():
            if contact_value is not None:
                og_data['contact'][contact_key] = contact_value
        # Remove contact from update_dict since we handled it specially
        del update_dict['contact']
    
    #------ 
    for key,value in update_dict.items():
        og_data[key] = value
        
    data[update_id] = og_data
    
    
    with open(json_path,'w') as f:
        json.dump(data, f, indent=2)
    
    return {"message": "Data updated successfully", "data": data[update_id]}
    
    
    
    #---->Delete

@app.post('/delete/{key}')

def delete(key:str):
    with open(json_path,'r') as f:
        data = json.load(f)
        if key in data:
            del data[key]
            
            with open(json_path,'w') as f:
                json.dump(data, f, indent=2)
                return {"message": f"Patient with key {key} deleted successfully"}

                
        
    
        else:
            raise HTTPException(status_code=404, detail=f'Given key {key} is not in the dataset')

        
        
        
        
    
    
    
    
     
    

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

