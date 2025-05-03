import httpx,subprocess,time,signal,pytest,os
@pytest.fixture(scope="session",autouse=True)
def server():
    p=subprocess.Popen(["poetry","run","uvicorn","app.main:app"])
    time.sleep(5); yield; p.send_signal(signal.SIGINT)
def test_health():
    assert httpx.get("http://127.0.0.1:8000/health").json()["status"]=="ok" 