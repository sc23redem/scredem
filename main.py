import http.server
import socketserver
import base64
from bs4 import BeautifulSoup
import binascii

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    MAX_REDIRECTS = 5

    def do_GET(self):
        # Get the request url
        print("Received request for URL:", self.headers['Host'] + self.path)

        # Get the base url
        base_url = self.path[1:]

        if "-" not in base_url:
            # Return an error if the URL does not contain a '-' separator
            self.send_error(400, "Invalid URL format: URL should contain an email and a redirection URL separated by a '-'")
            return

        splitted_base_url = base_url.split("-")
        
        if len(splitted_base_url) != 2:
            # Return an error if there are not exactly 2 parameters in the URL
            self.send_error(400, "Invalid URL format: URL should contain an email and a redirection URL separated by a '-'")
            return

        print("Base URL:", base_url)

        # Get the email
        encoded_email = splitted_base_url[0]
        # Add padding characters to the encoded string if needed
        encoded_email += "=" * ((4 - len(encoded_email) % 4) %4)
        encoded_url = splitted_base_url[1]
        encoded_url += "=" * ((4 - len(encoded_url) % 4) %4)

        try:
            decoded_email = base64.b64decode(encoded_email).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError) as e:
            # Try decoding with another encoding
            self.send_error(400, str(e))
            return

        if not decoded_email:
            # Return an error if the decoded email is empty
            self.send_error(400, "Invalid URL format: Decoded email is empty")
            return

        print("Decoded Email:", decoded_email)

        # Get the Redirection URL
        try:
            decoded_url = base64.b64decode(encoded_url).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError) as e:
            # Try decoding with another encoding
            self.send_error(400, str(e))
            return

        if not decoded_url:
            # Return an error if the decoded email is empty
            self.send_error(400, "Invalid URL format: Decoded URL is empty")
            return

        print("Decoded Redirection URL:", decoded_url)

        redirect_html = BeautifulSoup(decoded_url, "html.parser")
        redirect_url = redirect_html.get_text()
        print("Redirection URL:", redirect_url)

        if getattr(self, 'redirect_count', 0) < self.MAX_REDIRECTS:
            self.redirect_count = getattr(self, 'redirect_count', 0) + 1

            # Use relative URLs for redirecting
            self.send_response(302)
            self.send_header('Location', redirect_url)
            self.end_headers()
        else:
            # Return an error if too many redirects
            self.send_error(500, "Too many redirects")

        # urllib.request.urlopen(decoded_url)
        # Add try-except blocks to handle unexpected errors
        try:
            pass
        except Exception as e:
            self.send_error(500, str(e))

        # Add logging for better error tracking
        print("Request processed successfully")

#HOST = 'diagonallysc.com'
HOST = '170.64.150.15'
PORT = 80

handler = MyRequestHandler
httpd = socketserver.TCPServer((HOST, PORT), handler)
print('Server started')
httpd.serve_forever()
