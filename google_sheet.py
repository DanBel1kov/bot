from imports import *


def upload_csv_to_google_sheets(csv_file_path, spreadsheet_id, range_name):
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheets_api = build('sheets', 'v4', credentials=credentials)

    sheets_api.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        body={}
    ).execute()

    with open(csv_file_path, 'r') as csvfile:
        data = [row for row in csv.reader(csvfile)]

    sheets_api.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            'valueInputOption': 'RAW',
            'data': [
                {
                    'range': range_name,
                    'values': data
                }
            ]
        }
    ).execute()


def update_user_in_google_sheets(user_id, user_data, spreadsheet_id, sheet_name):
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    sheets_api = build('sheets', 'v4', credentials=credentials)

    result = sheets_api.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=sheet_name
    ).execute()
    rows = result.get('values', [])

    row_number = None
    for i, row in enumerate(rows):
        if str(user_id) == row[0]:
            row_number = i + 1
            break

    if row_number is not None:
        update_range = f"{sheet_name}!A{row_number}:Z{row_number}"
        request = sheets_api.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=update_range,
            valueInputOption='RAW',
            body={
                'values': [user_data]
            }
        )
        request.execute()
    else:
        request = sheets_api.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=sheet_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={
                'values': [user_data]
            }
        )
        request.execute()
