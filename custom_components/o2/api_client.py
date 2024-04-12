import requests
import logging
from time import time
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, USER_AGENT, INTEGRATION_VERSION

_LOGGER = logging.getLogger(__name__)

class O2ApiClient:
    def __init__(self, email=None, password=None):
        self._username = email
        self._password = password
        self._device_info = None
        self._token_birth = 0

        self.number = None

        self._session = requests.Session()


    # External methods

    def create_session(self, username=None, password=None):
        # Login URL and credentials
        login_url = 'https://identity.o2.co.uk/auth/password_o2'
        login_data = {
            'username': username or self._username,
            'password': password or self._password,
            'sentTo': 'https://accounts.o2.co.uk/?checkproduct=true'
        }

        # Login to O2
        login_response = self._session.post(login_url, data=login_data, headers={ 'User-Agent': self._get_user_agent() }, allow_redirects=False)
        if login_response.status_code != 303:
            raise ApiException("Failed to login to O2. Status code:", login_response.status_code)

        if 'error' in login_response.headers['Location']:
            raise ApiException("Failed to login to O2")
        
        # If we were using one-time supplied credentials and logged in successfully, store them
        if username and password:
            self._username = username
            self._password = password

        self._token_birth = time()
        
        _LOGGER.debug("O2 session created")
        return True

    def get_allowances(self):
        resp = self._post('https://mymobile2.o2.co.uk/web/guest/account?p_p_id=O2UKAccountPortlet_INSTANCE_0ssTPnzpDk4K&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view&p_p_resource_id=getBoltOnsAndCurrentTariff&p_p_cacheability=cacheLevelPage')
        
        if resp.status_code != 200:
            self._token_birth = 0
            raise ApiException("Failed to get allowance. Status code:", resp.status_code)
        
        resp = resp.json()

        self._update_device_info(resp['tariffVM'])

        return resp


    # Internal API methods

    def _post(self, url):
        # Refresh token if its over 30 mins old
        if time() - self._token_birth > 2700:
            self.create_session()
        
        csrfToken = self._get_csrf()

        return self._session.post(url, headers={
            'X-Csrf-Token': csrfToken,
            'User-Agent': self._get_user_agent()
            })

    def _get_csrf(self):
        # Fetch account page
        data_page_url = 'https://mymobile2.o2.co.uk/'
        data_page_response = self._session.get(data_page_url, headers={ 'User-Agent': self._get_user_agent() })

        if data_page_response.status_code != 200:
            raise ApiException("Failed to retrieve account page. Status code:", data_page_response.status_code)

        return data_page_response.text.split("Liferay.authToken = '")[1].split("'")[0]


    # Internal methods

    def _get_user_agent(self):
        return f"{USER_AGENT}/{INTEGRATION_VERSION}"
    
    def _update_device_info(self, resp):
        self.number = resp['number']

        self._device_info = DeviceInfo(
            identifiers={(DOMAIN, "o2")},
            name=resp['name'] if 'name' in resp else number,
            manufacturer="O2",
            model=resp['subcategory'] if 'subcategory' in resp else None,
            serial_number=self.number
        )


    # Simple getters

    def get_device_info(self):
        return self._device_info

# Exceptions
class ApiException(Exception):
    ...
