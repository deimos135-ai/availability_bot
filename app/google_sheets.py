from __future__ import annotations

import json

import gspread
from google.oauth2.service_account import Credentials

from app.config import GOOGLE_CREDENTIALS_JSON, GOOGLE_SHEET_ID


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_credentials() -> Credentials:
    if not GOOGLE_CREDENTIALS_JSON:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON is not set")

    try:
        info = json.loads(GOOGLE_CREDENTIALS_JSON)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON is invalid JSON") from exc

    return Credentials.from_service_account_info(info, scopes=SCOPES)


def get_client() -> gspread.Client:
    creds = get_credentials()
    return gspread.authorize(creds)


def get_spreadsheet():
    if not GOOGLE_SHEET_ID:
        raise RuntimeError("GOOGLE_SHEET_ID is not set")

    client = get_client()
    return client.open_by_key(GOOGLE_SHEET_ID)


def get_worksheet(worksheet_name: str):
    spreadsheet = get_spreadsheet()
    return spreadsheet.worksheet(worksheet_name)


def get_all_rows(worksheet_name: str) -> list[list[str]]:
    worksheet = get_worksheet(worksheet_name)
    return worksheet.get_all_values()
