import requests
import xmltodict
from jinja2 import Template

# Define filter selectors
EQ = "="
NOT = "!="
LIKE = "like"


class Firewall:
    # Templates for different API actions
    templates_dict = {
        "create": """
            <Set operation="add">
                <{{ entity_type }}>{{ entity_data | safe }}</{{ entity_type }}>
            </Set>
        """,
        "read": """
            <Get>
                <{{ entity_type }}>
                    {% if entity_data %}
                        <Filter>
                            <key name="Name" criteria="{{ filter_selector }}">{{ entity_data }}</key>
                        </Filter>
                    {% endif %}
                </{{ entity_type }}>
            </Get>
        """,
        "update": """
            <Set operation="update">
                <{{ entity_type }}>{{ entity_data | safe }}</{{ entity_type }}>
            </Set>
        """,
        "delete": """
            <Remove>
                <{{ entity_type }}>
                    {% if entity_type == "FirewallRule" %}
                        <Name>{{ entity_data }}</Name>
                    {% else %}
                        {% if entity_data %}
                            <Filter>
                                <key name="Name" criteria="{{ filter_selector }}">{{ entity_data }}</key>
                            </Filter>
                        {% endif %}
                    {% endif %}
                </{{ entity_type }}>
            </Remove>
        """,
    }

    def __init__(self, username, password, hostname, port=4444, certificate_verify=False, password_encrypted=False):
        self.url = f"https://{hostname}:{port}/webconsole/APIController"
        self.xml_login = f"""
            <Login> 
                <Username>{username}</Username>
                <Password{" passwordform='encrypt'" if password_encrypted else ""}>{password}</Password>
            </Login>
        """
        self.session = requests.Session()
        self.session.verify = certificate_verify
        self.headers = {"Accept": "application/xml"}
        if not certificate_verify:
            requests.packages.urllib3.disable_warnings()
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _format_xml_response(self, response, entity_type):
        response = response.get("Response", {})

        # Check status in response
        if "Status" in response:
            return {"status": response["Status"]["@code"], "message": response["Status"]["#text"], "data": []}

        # Handle authentication failure
        if response.get("Login") and response["Login"].get("status") == "Authentication Failure":
            return {"status": "401", "message": response["Login"]["status"], "data": []}

        # Check if entity exists in response
        if entity_type in response:
            entity_data = response[entity_type]

            # Handle status in entity data
            if "Status" in entity_data:
                if "@code" in entity_data["Status"]:
                    return {"status": entity_data["Status"]["@code"], "message": entity_data["Status"]["#text"], "data": []}
                elif entity_data["Status"] in ["No. of records Zero.", "Number of records Zero."]:
                    return {"status": "526", "message": "Record does not exist.", "data": []}

            # Normalize entity data to list
            entity_data = [entity_data] if isinstance(entity_data, dict) else entity_data
            entity_data = [{k: v for k, v in item.items() if k != "@transactionid"} for item in entity_data]

            return {"status": "216", "message": "Operation Successful.", "data": entity_data}

        # If entity not found in the response
        return {"status": "404", "message": "Entity not found", "data": []}

    def _perform_action(self, action_template_key, entity_type, entity_data=None, filter_selector=None):
        if self.closed:
            return {"status": "400", "message": "Session is closed and cannot be used.", "data": []}

        template_action = Template(self.templates_dict[action_template_key])
        xml_action = template_action.render(entity_type=entity_type, entity_data=entity_data, filter_selector=filter_selector)
        full_request_xml = f"<Request>{self.xml_login}{xml_action}</Request>"

        try:
            response = self.session.post(self.url, headers=self.headers, data={"reqxml": full_request_xml}, timeout=30)
            return self._format_xml_response(xmltodict.parse(response.content.decode()), entity_type)
        except requests.RequestException as e:
            return {"status": "500", "message": f"Request failed: {str(e)}", "data": []}

    # Public methods
    def close(self):
        if not self.closed:
            if self.session:
                self.session.close()
                self.session = None
            self.closed = True
            return {"status": "200", "message": "Session closed successfully.", "data": []}
        else:
            return {"status": "400", "message": "Session was already closed.", "data": []}

    # CRUD methods
    def create(self, entity_type, entity_data):
        xml_data = xmltodict.unparse(entity_data, full_document=False)
        return self._perform_action("create", entity_type, entity_data=xml_data)

    def read(self, entity_type, entity_data=None, filter_selector=LIKE):
        return self._perform_action("read", entity_type, entity_data, filter_selector)

    def update(self, entity_type, entity_data):
        xml_data = xmltodict.unparse(entity_data, full_document=False)
        return self._perform_action("update", entity_type, entity_data=xml_data)

    def delete(self, entity_type, entity_data=None, filter_selector=EQ):
        return self._perform_action("delete", entity_type, entity_data, filter_selector)
