# AntiScamBotAPI
API for querying ScamBot via HTTP Get.

This allows you to have a publicly accessible API to your [AntiScamBot](https://github.com/SocksTheWolf/AntiScamBot) installation.

## Setup

This setup assumes you know how to [setup a python virtual environment already](https://fastapi.tiangolo.com/virtual-environments/).

Clone the project somewhere that can access your AntiScamBot database file, and then create an .env with the following information

```
DATABASE_FILE="PATH TO DATABASE FILE"
```
Run with `fastapi run` or via the run script in the `.runtime` folder.

## Authentication

Authorization is not natively provided in this app, however an implementation is provided via Cloudflare workers (see `cloudflare` directory). 
Auth keys do not expire (as they're really only implemented to prevent misuse).
