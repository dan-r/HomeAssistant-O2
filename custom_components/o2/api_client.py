import requests
import logging
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class O2ApiClient:
    def __init__(self, email=None, password=None):
        self._username = email
        self._password = password
        self._device_info = None
        
        self.number = None

        self._session = requests.Session()

    def create_session(self, username=None, password=None):
        # Login URL and credentials
        login_url = 'https://identity.o2.co.uk/auth/password_o2'
        login_data = {
            'username': username or self._username,
            'password': password or self._password,
            'sentTo': 'https://accounts.o2.co.uk/?checkproduct=true'
        }

        # Login to O2
        login_response = self._session.post(login_url, data=login_data, allow_redirects=False)
        if login_response.status_code != 303:
            raise ApiException("Failed to login to O2. Status code:", login_response.status_code)

        if 'error' in login_response.headers['Location']:
            raise ApiException("Failed to login to O2")
        
        # If we were using one-time supplied credentials and logged in successfully, store them
        if username and password:
            self._username = username
            self._password = password

        return True
        
    def get_device_info(self):
        return self._device_info

    def update_device_info(self, resp):
        self.number = resp['number']

        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, "o2")},
            name=resp['name'] if 'name' in resp else number,
            manufacturer="O2",
            model=resp['subcategory'] if 'subcategory' in resp else None,
            serial_number=self.number
        )


    def get_csrf(self):
        # Fetch account page
        data_page_url = 'https://mymobile2.o2.co.uk/'
        data_page_response = self._session.get(data_page_url)

        if data_page_response.status_code != 200:
            raise ApiException("Failed to retrieve account page. Status code:", data_page_response.status_code)

        return data_page_response.text.split("Liferay.authToken = '")[1].split("'")[0]

    def get_allowances(self):
        csrfToken = self.get_csrf()

        allowance_url = 'https://mymobile2.o2.co.uk/web/guest/account?p_p_id=O2UKAccountPortlet_INSTANCE_0ssTPnzpDk4K&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getBoltOnsAndCurrentTariff&p_p_cacheability=cacheLevelPage'
        allowance_response = self._session.post(allowance_url, headers={'X-Csrf-Token': csrfToken})

        if allowance_response.status_code != 200:
            raise ApiException("Failed to get allowance. Status code:", allowance_response.status_code)
        
        resp = allowance_response.json()
        self.update_device_info(resp['tariffVM'])

        return resp

# Exceptions
class ApiException(Exception):
    ...
