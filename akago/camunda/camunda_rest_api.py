import json

import requests


class Camunda:
    @classmethod
    def genToken(cls):
        auth_url = "https://login.cloud.camunda.io/oauth/token"
        client_id = "tvxysvRpDv6MnMZtEmOcd7VT.E~HxsjU"
        client_secret = (
            "mOqoizmOFatlUCKyN6Yk5IP2U.9qEc2hOHcgz8v4TxRvXKKQ5TJLy.JKZYZI6dzO"
        )

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": "tasklist.camunda.io",
            #'audience': 'zeebe.camunda.io'
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        auth_response = requests.post(auth_url, data=payload, headers=headers)

        if auth_response.status_code == 200:
            access_token = auth_response.json().get("access_token")
            # print("Token uzyskany:", access_token)
            return access_token
        else:
            print("Błąd uzyskania tokenu:", auth_response.status_code)
            print(auth_response.json())
            exit()

        return None

    @classmethod
    def genTokenOperate(cls):
        auth_url = "https://login.cloud.camunda.io/oauth/token"
        client_id = "tvxysvRpDv6MnMZtEmOcd7VT.E~HxsjU"
        client_secret = (
            "mOqoizmOFatlUCKyN6Yk5IP2U.9qEc2hOHcgz8v4TxRvXKKQ5TJLy.JKZYZI6dzO"
        )

        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "audience": "operate.camunda.io",
            # 'audience': 'zeebe.camunda.io'
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        auth_response = requests.post(auth_url, data=payload, headers=headers)

        if auth_response.status_code == 200:
            access_token = auth_response.json().get("access_token")
            # print("Token uzyskany:", access_token)
            return access_token
        else:
            print("Błąd uzyskania tokenu:", auth_response.status_code)
            print(auth_response.json())
            exit()

        return None

    @classmethod
    def getTask(cls, task_id, access_token):
        url = "https://bru-2.tasklist.camunda.io:443/eea87386-0393-4bbc-ad2e-a10a85bb2646/v1/tasks/search"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        payload = json.dumps({"taskId": task_id})

        response = requests.post(url, headers=headers, data=payload)

        try:
            tasks_response = response.json()

            # Sprawdzenie, czy odpowiedź zawiera jakiekolwiek taski
            if (
                tasks_response
                and isinstance(tasks_response, list)
                and len(tasks_response) > 0
            ):
                task_name = tasks_response[0].get("name")  # Pobierz nazwę taska
                if task_name:
                    # print(f"Nazwa taska dla ID {task_id}: {task_name}")
                    return task_name
                else:
                    # print(f"Task o ID {task_id} nie ma przypisanej nazwy.")
                    return None
            else:
                # print(f"Nie znaleziono taska o ID {task_id}.")
                return None

        except ValueError:
            # print("Odpowiedź nie jest w formacie JSON.")
            return None

    @classmethod
    def sendRequest(cls, task_id, variable_name, variable_value, access_token):
        url = f"https://bru-2.tasklist.camunda.io:443/eea87386-0393-4bbc-ad2e-a10a85bb2646/v1/tasks/{task_id}/complete"

        payload = json.dumps(
            {"variables": [{"name": variable_name, "value": f'"{variable_value}"'}]}
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.patch(url, headers=headers, data=payload)

        if response.status_code == 200:
            print("Zadanie zostało pomyślnie ukończone.")
            # print(response.json())
        else:
            print(
                f"Błąd podczas ukończenia zadania. Kod statusu: {response.status_code}"
            )
            print(response.text)

    @classmethod
    def startProcessWithWebhook(cls):
        webhook_url = "https://bru-2.connectors.camunda.io/eea87386-0393-4bbc-ad2e-a10a85bb2646/inbound/Start"

        payload = {"status": "start process"}

        headers = {"Content-Type": "application/json"}

        response = requests.post(webhook_url, headers=headers, json=payload)

        if response.status_code == 200:
            print("Proces został pomyślnie uruchomiony.")
            try:
                response_data = response.json()
                print("Odpowiedź:", response_data)
                # Zmień nazwę klucza na "processInstanceKey"
                process_instance_key = response_data.get("processInstanceKey")
                if process_instance_key:
                    print(f"Klucz instancji procesu: {process_instance_key}")
                else:
                    print("Nie znaleziono klucza 'processInstanceKey' w odpowiedzi.")
                return process_instance_key
            except requests.exceptions.JSONDecodeError:
                print(
                    "Odpowiedź nie zawiera JSON-a. Odpowiedź tekstowa:", response.text
                )
        # else:
        # print(f"Błąd podczas uruchamiania procesu. Kod statusu: {response.status_code}")
        # print("Odpowiedź:", response.text)

        return None

    @classmethod
    def searchTaskForProcess(cls, process_instance_key, access_token):
        url = "https://bru-2.tasklist.camunda.io/eea87386-0393-4bbc-ad2e-a10a85bb2646/v1/tasks/search"

        payload = json.dumps(
            {"state": "CREATED", "processInstanceKey": process_instance_key}
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.post(url, headers=headers, data=payload)

        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                print("Znalezione zadania:", tasks)
                first_task = tasks[0]
                task_id = first_task.get("id")
                return task_id
            else:
                print("Nie znaleziono żadnych zadań dla podanej instancji procesu.")
                return None
        else:
            print(
                f"Błąd podczas wyszukiwania zadań. Kod statusu: {response.status_code}"
            )
            print("Odpowiedź:", response.text)
            return None

    @classmethod
    def getTaskVariableValue(cls, task_id, access_token, variable_name):
        url = f"https://bru-2.tasklist.camunda.io/eea87386-0393-4bbc-ad2e-a10a85bb2646/v1/tasks/{task_id}/variables/search"

        payload = {"variableNames": [variable_name]}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            try:
                variables = response.json()
                for variable in variables:
                    if variable["name"] == variable_name:
                        return json.loads(
                            variable["value"]
                        )  # Zwraca wartość zmiennej jako obiekt Python (lista)
                print(f"Zmienna {variable_name} nie została znaleziona.")
                return None
            except json.JSONDecodeError:
                print("Nie udało się zdekodować odpowiedzi JSON.")
                return None
        else:
            print(
                f"Błąd podczas wyszukiwania zmiennych. Kod statusu: {response.status_code}"
            )
            print("Odpowiedź serwera:", response.text)
            return None

    @classmethod
    def is_process_completed(cls, process_instance_key, access_token):
        url = "https://bru-2.operate.camunda.io/eea87386-0393-4bbc-ad2e-a10a85bb2646/v1/process-instances/search"

        # Żądanie dla procesu o określonym kluczu
        payload = json.dumps({"filter": {"key": process_instance_key}})

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            data = response.json()
            print(data)  # Debugowanie odpowiedzi

            items = data.get("items", [])
            if items:
                process = items[0]  # Zakładamy, że proces o podanym kluczu jest jeden
                state = process.get("state")
                if state == "COMPLETED":
                    return True
                else:
                    print(f"Proces {process_instance_key} jest w stanie {state}.")
                    return False
            else:
                return False
        else:
            print(
                f"Błąd podczas wyszukiwania procesu. Kod statusu: {response.status_code}"
            )
            print(response.text)
            return False
