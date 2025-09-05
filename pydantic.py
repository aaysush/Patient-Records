from pydantic import BaseModel, Field, EmailStr,computed_field,EmailStr,model_validator,field_validator
from typing import List, Dict, Optional


class contact(BaseModel):
    
    phone : int = Field(gt= 10000000,description='ayyo')
    email : str = Field(max_length=50,description='ayyooooooooooooooopje')
  

class patient(BaseModel):
    
    name : str = Field(max_length=60,description='name of patient')
    age : int   = Field(strict=False,description='age of patient')
    email : EmailStr
    emergency : Optional[int] = None
    weight : float  = Field(gt = 0,lt = 200,title ='weight of patient')
    married : bool
    allergies: Optional[List[str]]= None
    contact_details: contact
    
    @computed_field
    @property
    
    def new_weight(self)-> float:
        new_weight= self.weight + 1000
        return new_weight
    
    
    
    @field_validator('email')
    @classmethod
    def email_validation(cls,email_value):
        
        valid_domain = 'gmail.com'
        cur_domain = email_value.split('@')[-1]
        if cur_domain == valid_domain :
            return email_value
        else:
            raise ValueError(f"Email must be from gmail.com domain")
        
    @field_validator('name')
    @classmethod
    def transform(cls,name):
        return name.upper()
    
    @model_validator(mode = 'after')
    @classmethod
    # cls ---> the patient CLASS itself (not an instance)
    # model ---> a specific INSTANCE of our pydantic model (the actual patient object)
    def c_emergency(cls,model):
        if model.age > 60 and model.emergency is None :
            raise ValueError('old peeps need emergency no.')
        return model

    
p= {'name': 'aay','age':'22','email':'aayushpandey7@gmail.com','weight':70.1,'married': True ,'contact_details':{'phone':'1234567890','email':'aayushpandey7@gmail.com'}}    

patient_1 = patient(**p)
print(patient_1.model_dump())
