import requests
import xmltodict
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Kapitalbank:
    def __init__(self, environment='test', cert_file='testmerchant_06.crt', key_file='merchant_name.key'):
        self.url = "https://tstpg.kapitalbank.az:5443/Exec" if environment == 'test' else "https://3dsrv.kapitalbank.az:5443/Exec"
        self.cert_file = cert_file
        self.key_file = key_file
        self.headers = {"Content-Type": "text/html; charset=utf-8"}

    def send_request(self, amount, language):
        response = requests.post(
            self.url,
            data=f'''<?xml version="1.0" encoding="UTF-8"?>
                        <TKKPG>
                            <Request>
                                <Operation>CreateOrder</Operation>
                                <Language>{language}</Language>
                                <Order>
                                    <OrderType>Purchase</OrderType>
                                    <Merchant>E1000010</Merchant>
                                    <Amount>{int(float(amount) * 100)}</Amount>
                                    <Currency>944</Currency>
                                    <Description>xxxxxxxx</Description>
                                    <ApproveURL>/testshopPageReturn.jsp</ApproveURL>
                                    <CancelURL>/testshopPageReturn.jsp</CancelURL>
                                    <DeclineURL>/testshopPageReturn.jsp</DeclineURL>
                                </Order>
                            </Request>
                        </TKKPG>''',
            headers=self.headers,
            cert=(self.cert_file, self.key_file),
            verify=False  # Disable SSL verification; replace with proper SSL handling for production
        )

        response.raise_for_status()  # Raise an exception for HTTP errors

        if response.status_code == 200:
            return self.xml_to_json(response.text)
        else:
            return {"error": f"HTTP Error {response.status_code}"}

    @staticmethod
    def xml_to_json(xml_string):
        try:
            xml_dict = xmltodict.parse(xml_string)
            return json.loads(json.dumps(xml_dict,indent=2))  # Convert XML to JSON format
        except Exception as e:
            return {"error": str(e)}

    def get_order_url(self, amount, language):
        response = self.send_request(amount, language)
        print("***************************")
        print(response)
        print("***************************")

        # Check if response is a dictionary and contains the expected keys
        if isinstance(response, dict):
            order = response.get("TKKPG", {}).get("Response", {}).get("Order", {})
            OrderID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("OrderID", {})
            SessionID = response.get("TKKPG", {}).get("Response", {}).get("Order", {}).get("SessionID", {})

            if "URL" in order:
                return order["URL"] + '?' + 'ORDERID=' + OrderID + '&SessionID=' + SessionID
            else:
                return {"error": "URL not found in response"}
        else:
            return {"error": "Invalid response format"}

# Example usage:
xml_requester = Kapitalbank(environment='test')
url = xml_requester.get_order_url(amount=5, language='AZ')
print("Order URL:", url)


