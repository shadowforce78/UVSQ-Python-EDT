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
    "start": "2024-11-18",
    "end": "2024-11-24",
    "resType": 103,
    "calView": "agendaWeek",
    "federationIds": ["INF1-b2"],
    "colourScheme": 3,
}


def make_body(start_date, end_date, federationIds):

    # FederationIds to array
    federationIds = [federationIds]
    body = {
        "start": start_date,
        "end": end_date,
        "resType": 103,
        "calView": "agendaWeek",
        "federationIds": federationIds,
        "colourScheme": 3,
    }
    return body


def format_events(events):
    formatted_data = {}

    for event in events:
        start_time = datetime.datetime.fromisoformat(event["start"])
        end_time = datetime.datetime.fromisoformat(event["end"])

        event_info = {
            "ID": event["id"],  # Ajouter l'ID de l'événement
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
        }

        date_str = start_time.strftime("%Y-%m-%d")
        if date_str not in formatted_data:
            formatted_data[date_str] = []

        formatted_data[date_str].append(event_info)

    return formatted_data


def fetch_event_details(event_id):
    """
    Récupère les détails d'un événement donné son ID.
    """
    endpoint = "https://edt.iut-velizy.uvsq.fr/Home/GetSideBarEvent"
    body = {"eventId": event_id}

    # print(f"Fetching details for event ID: {event_id}")
    response = requests.post(endpoint, headers=headers, data=body)
    if response.status_code == 200:
        return json.loads(response.text)
    elif response.status_code == 500:
        print(
            f"Erreur serveur : {response.text}"
        )  # Ou un autre attribut contenant les détails
        return None
    else:
        print(
            f"Erreur lors de la récupération des détails de l'événement {event_id}: {response.status_code}"
        )
        return None


def fetch_and_format_data():
    response = requests.post(endPointUrl, headers=headers, data=body)
    formatted_response = json.loads(response.text)
    return format_events(formatted_response)
