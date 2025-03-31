import gspread
from google.oauth2.service_account import Credentials


def send_to_gsheets(weather_data_list):
    """ Summary:
        Recieves a list of lists as input and appends each list as a row in a Google Sheet


    Args:
        weather_data_list (list): Weather sensor input data, each entry is saved as a list 
    """

    # Load credentials
    creds = Credentials.from_service_account_file("cred.json", scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])

    # Authenticate and open the sheet
    client = gspread.authorize(creds)
    sheet = client.open("Weather Data").sheet1  # Open first sheet

    # For each list in the weather_data_list 
    for lt in weather_data_list:
        # Add a row of data
        sheet.append_row(lt)

'''
testing the function
listoflist = [['a','b'],['a1','b1']]
send_to_gsheets(listoflist)
'''