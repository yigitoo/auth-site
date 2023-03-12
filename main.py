#!/usr/bin/env python3
'''
@author: github.com/yigitoo
@date: 12.03.2023 10:42 PM.
'''

import uuid
from typing import Dict

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth

from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib 

from nicegui import app, ui

from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
from dataclasses import dataclass

from util.structs import User

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
config = Config('.env')
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id = os.getenv("GOOGLE_CLIENT_ID"),
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs = {'scope': 'openid email profile'}
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)  # use your own secret key here

@app.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = f'{os.getenv("PRODUCTION_LINK")}/auth/google'
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth/google")
async def auth_via_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = await oauth.google.parse_id_token(request, token)
    return dict(user)

# in reality users and session_info would be persistent (e.g. database, file, ...) and passwords obviously hashed
client = MongoClient(os.getenv('DB_LINK'))
db = client['blog']
users = db.users.find({})
session_info: Dict[str, Dict] = {}

def sync_users(id: str, user_dict: User) -> None:
    global users
    db.users.update_one({
        "id": id
    }, {
        "$set": user_dict
    })
    users = db.users.find({})

def make_user_active(user: User) -> None:
    user['is_active'] = True
    sync_users(user['id'], user)

def is_authenticated(request: Request) -> bool:
    return session_info.get(request.session.get('id'), {}).get('authenticated', False)

@ui.page('/blogs')
def blogs_page(request: Request) -> None:
    if not is_authenticated(request):
        return RedirectResponse('/login')
    
    session = session_info[request.session['id']]


@ui.page('/')
def main_page(request: Request) -> None:
    if not is_authenticated(request):
        return RedirectResponse('/login')
    session = session_info[request.session['id']]

    with ui.dialog() as dialog, ui.card():
        ui.label('Are you sure to logout?')
        with ui.row():
            ui.button('Yes', on_click=lambda: dialog.submit('true'))
            ui.button('No', on_click=lambda: dialog.submit('false'))

    async def logout_dialog():
        result = await dialog
        if result == "true":
            ui.notify(f'Logging out from {session["username"]}...')
            await asyncio.sleep(1.5)
            ui.open('/logout')
        else:
            ui.notify('Gave up to logout.')

    with ui.column().classes('absolute-center items-center'):
        with ui.row().classes('mr-1 my-2'):
            ui.label(f'Hello {session["username"]}!').classes('text-2xl')
            ui.button('', on_click=logout_dialog).props('icon=logout')

@ui.page('/login')
def login(request: Request) -> None:
    global users
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        for user in users:
            if (username.value, password.value) == (user['username'], user['password']):
                
                make_user_active(user)
                session_info[request.session['id']] = {**user, 'authenticated': True}
                
                ui.open('/')
            else:
                ui.notify('Wrong username or password', color='negative')

    if is_authenticated(request):
        return RedirectResponse('/')

    request.session['id'] = str(uuid.uuid4())
    
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password').props('type=password').on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)


@ui.page('/logout')
def logout(request: Request) -> None:
    if is_authenticated(request):
        session = session_info[request.session['id']]
        last_active = f"{datetime.now():%D %H:%M:%S}"
        db.users.update_one({
            "username": session['username']
        }, {
            "$set": { "is_active": False, "last_active": last_active }
        })
        session_info.pop(request.session['id'])
        request.session['id'] = None
        return RedirectResponse('/login')
    return RedirectResponse('/')


ui.run(title="Auth Site")
