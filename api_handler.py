import requests
import json
import datetime

# --- Configuration API ---
endPointUrl = "https://edt.iut-velizy.uvsq.fr/Home/GetCalendarData"

headers = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
}

body = {
    "start": "2024-11-11",
    "end": "2024-11-16",
    "resType": 103,
    "calView": "agendaWeek",
    "federationIds": ["INF1-B2"],
    "colourScheme": 3,
}

def format_events(events):
    formatted_data = {}

    for event in events:
        # Conversion des dates au format lisible
        start_time = datetime.datetime.fromisoformat(event["start"])
        end_time = datetime.datetime.fromisoformat(event["end"])

        # Extraction des infos principales
        event_info = {
            "Début": start_time.strftime("%H:%M"),
            "Fin": end_time.strftime("%H:%M"),
            "Description": event["description"]
            .replace("<br />", "\n")
            .replace("&39;", "'")
            .strip(),
            "Professeur(s)": event["description"].split("<br />")[0],
            "Module(s)": (
                ", ".join(event["modules"]) if event["modules"] else "Non spécifié"
            ),
            "Type": event["eventCategory"],
            "Site": ", ".join(event["sites"]) if event["sites"] else "Non spécifié",
            "Couleur": event["backgroundColor"],
            "Id" : event["id"]
        }

        # Classement par jour
        date_str = start_time.strftime("%Y-%m-%d")
        if date_str not in formatted_data:
            formatted_data[date_str] = []

        formatted_data[date_str].append(event_info)

    return formatted_data


def fetch_and_format_data():
    response = requests.post(endPointUrl, headers=headers, data=body)
    formatted_response = json.loads(response.text)
    return format_events(formatted_response)
