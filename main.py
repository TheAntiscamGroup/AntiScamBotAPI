from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from typing import Union
from DatabaseDriver import DatabaseDriver
from DatabaseSchema import Ban
from pydantic import BaseModel
from datetime import datetime

# Application Config
host_name = "scamguard.app"
api_host_name = f"api.{host_name}"
contact_url = "https://socksthewolf.com/contact"

# API Naming Config
global_title = "ScamGuard API"
global_version = "1.1.2"
global_summary = "An API for interfacing with ScamGuard data"
global_description = f"""
# Info

This API allows you to interface and query operational information about ScamGuard's database!

**NOTE**: all API calls require an `Authorization: Bearer <token>` header, otherwise the request will fail. 

If you would like to obtain an API Token, please send a message in the `#api-requests` channel of the [ScamGuard Discord server](https://{host_name}/discord).

"""


app = FastAPI(redoc_url=None, openapi_url="/openapi.json", description=global_description, title=global_title, summary=global_summary, 
              contact={"name":"Support Contact", "url":contact_url}, terms_of_service=f"https://{host_name}/terms", 
              license_info={"name":"MIT", "url":"https://github.com/theantiscamgroup/AntiScamBotAPI/blob/main/LICENSE"}, 
              servers=[{"url": f"https://{api_host_name}", "description": "Production API"}], version=global_version)

db = DatabaseDriver()

class APIBan(BaseModel):
  banned: bool = False
  user_id: int = 0
  valid: bool = False
  
  def Create(self, user_id:int=0):
    self.user_id = user_id
    self.valid = (user_id >= 1)
    return self
   
  def Execute(self):
    return self.ExecuteOnData(db.GetBanInfo(self.user_id))
    
  def ExecuteOnData(self, BanInfo:Ban|None):
    self.banned = (BanInfo is not None)
    return self

class APIBanDetailed(APIBan):
  banned_on:Union[datetime, None] = None
  banned_by:str = "scamguard reviewer handle"
  evidence_thread:Union[int, None] = None
  
  def Create(self, user_id:int=0):
    super().Create(user_id)
    self.banned_on = None
    self.banned_by = ""
    self.evidence_thread = None
    return self
  
  def Execute(self):    
    BanInfo:Ban|None = db.GetBanInfo(self.user_id)
    super().ExecuteOnData(BanInfo)
    
    if self.banned and BanInfo is not None:
      self.banned_on = BanInfo.created_at
      self.evidence_thread = BanInfo.evidence_thread
      self.banned_by = BanInfo.assigner_discord_user_name
      
    return self

class APIStats(BaseModel):
  count:int = 0
  valid:bool = True
  
  def Execute(self):
    self.count = db.GetNumBans()
    return self
    
class APIAuthError(BaseModel):
  valid: bool = False
  msg: str = "Invalid Auth Key Provided"

@app.get("/", include_in_schema=False, response_class=RedirectResponse, status_code=302)
def main():
  return f"https://{api_host_name}/docs"
  
@app.get("/check/{user_id}", description="Check if a Discord UserID is banned", response_model=APIBan, responses={403: {"model": APIAuthError}})
def check_ban(user_id: int):
  return APIBan().Create(user_id).Execute()

@app.get("/ban/{user_id}", description="Get extensive information as to an UserID being banned", response_model=APIBanDetailed, responses={403: {"model": APIAuthError}})
def get_ban_info(user_id: int):
  return APIBanDetailed().Create(user_id).Execute()

@app.get("/bans", description="Get Number of All Bans", response_model=APIStats, responses={403: {"model": APIAuthError}})
def get_ban_stats():
   return APIStats().Execute()

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
  return FileResponse("favicon.ico")
