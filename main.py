from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from typing import Union
from DatabaseDriver import DatabaseDriver
from DatabaseSchema import Ban
from pydantic import BaseModel
from datetime import datetime

# Application Config
service_name = "ScamGuard"
host_name = "scamguard.app"
api_host_name = f"api.{host_name}"
contact_url = "https://socksthewolf.com/contact"

# API Naming Config
global_title = f"{service_name} API"
global_version = "1.1.4"
global_summary = f"An API for interfacing with {service_name} data"
global_description = f"""
# Info

This API allows you to interface and query operational information about {service_name}'s database!

**NOTE**: all API calls require an `Authorization: Bearer <token>` header, otherwise the request will fail.

If you would like to obtain an API Token, please send a message in the `#api-requests` channel of the [{service_name} Discord server](https://{host_name}/discord).

"""


app = FastAPI(redoc_url=None, docs_url=None, openapi_url="/openapi.json", description=global_description, title=global_title, summary=global_summary,
              contact={"name":"Support Contact", "url":contact_url}, terms_of_service=f"https://{host_name}/terms",
              license_info={"name":"MIT", "url":"https://github.com/theantiscamgroup/AntiScamBotAPI/blob/main/LICENSE"},
              servers=[{"url": f"https://{api_host_name}", "description": "Production API"}], version=global_version)

db = DatabaseDriver()

class BaseAPIResponse(BaseModel):
  valid: bool = False

class APIBan(BaseAPIResponse):
  banned: bool = False
  user_id: int = 0
  user_id_str: str = ""

  def Create(self, user_id:int=0):
    self.user_id = user_id
    self.valid = (user_id >= 1)
    if (self.valid):
      self.user_id_str = str(user_id)
    return self

  def Execute(self):
    return self.ExecuteOnData(db.GetBanInfo(self.user_id))

  def ExecuteOnData(self, BanInfo:Ban|None):
    self.banned = (BanInfo is not None)
    return self

class APIBanDetailed(APIBan):
  banned_on: Union[datetime, None] = None
  banned_by: str = f"{service_name} reviewer handle"
  evidence_thread: Union[int, None] = None
  evidence_thread_str: Union[str, None] = None

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
      self.evidence_thread_str = str(self.evidence_thread)
      self.banned_by = BanInfo.assigner_discord_user_name

    return self

class APIStats(BaseAPIResponse):
  count: int = 0

  def Execute(self):
    self.valid = True
    self.count = db.GetNumBans()
    return self

class APIAuthError(BaseAPIResponse):
  msg: str = "Invalid Auth Key Provided"

class APIInvalidData(BaseAPIResponse):
  msg: str = "Provided data was invalid"
  details: Union[str, None] = None

  def Execute(self, data: str):
    self.details = data
    return self

@app.get("/", include_in_schema=False, response_class=RedirectResponse, status_code=302)
def main():
  return f"https://{api_host_name}/docs"

@app.get("/docs", include_in_schema=False)
async def docs_output(req: Request):
  return get_swagger_ui_html(
      openapi_url=app.openapi_url,
      title=app.title,
      swagger_favicon_url="/favicon.png",
      swagger_ui_parameters=app.swagger_ui_parameters,
  )

@app.get("/check/{user_id}", description="Check if a Discord UserID is banned", response_model=APIBan, responses={403: {"model": APIAuthError}, 422: {"model": APIInvalidData}})
def check_ban(user_id: int):
  return APIBan().Create(user_id).Execute()

@app.get("/ban/{user_id}", description="Get extensive information as to an UserID being banned", response_model=APIBanDetailed, responses={403: {"model": APIAuthError}, 422: {"model": APIInvalidData}})
def get_ban_info(user_id: int):
  return APIBanDetailed().Create(user_id).Execute()

@app.get("/bans", description="Get Number of All Bans", response_model=APIStats, responses={403: {"model": APIAuthError}})
def get_ban_stats():
   return APIStats().Execute()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
  message = ""
  for error in exc.errors():
      message += f"[Field: {error['loc']}, Error: {error['msg']}] "
  ErrObj = jsonable_encoder(APIInvalidData().Execute(message))
  return JSONResponse(content=ErrObj, status_code=422)

@app.get('/favicon.png', include_in_schema=False)
async def favicon():
  return FileResponse("favicon.png")

@app.get('/openapi.json', include_in_schema=False)
async def openapi():
  return FileResponse("openapi.json")