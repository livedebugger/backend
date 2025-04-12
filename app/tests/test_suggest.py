# from fastapi.testclient import TestClient
# from main import app

# client = TestClient(app)

# def test_suggest_endpoint():
#     headers = {
#             "Content-Type": "application/json",
#             "x-api-key": "abc123",
#             }
#     data = {
#             "context": "print(\"Hello World\")\n NameError: name 'printt'is not defined",
#             "type": "error",
#             "language": "python",
#             "path": "main.py"
#     }

#     response = client.post("/suggest", json=data, headers=headers)
#     assert response.status_code == 200
#     assert "suggestion" in response.json()
#     assert "printt" in response.json()["suggestion"]
