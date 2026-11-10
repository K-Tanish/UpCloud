import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from upcloud.server import UpCloudHandler


class DashboardServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), UpCloudHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_dashboard_page_and_api_are_available(self):
        with urlopen(self.base_url) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"UpCloud", response.read())

        with urlopen(f"{self.base_url}/api/dashboard") as response:
            data = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(data["mode"], "simulation")

    def test_scan_endpoint_returns_simulation_result(self):
        request = Request(
            f"{self.base_url}/api/scan",
            data=json.dumps({"provider": "gcp", "category": "ai"}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request) as response:
            data = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(data["provider"], "gcp")
            self.assertIn("sample findings", data["message"])

    def test_invalid_provider_returns_bad_request(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(f"{self.base_url}/api/findings?provider=not-a-cloud")

        self.assertEqual(error.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
