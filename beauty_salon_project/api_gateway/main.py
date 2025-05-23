from fastapi import FastAPI, Depends, HTTPException
import httpx
from typing import List

app = FastAPI(title="Beauty Salon API Gateway", version="1.0.0")

USER_SERVICE_URL = "http://localhost:8001"
SERVICE_MANAGEMENT_URL = "http://localhost:8002"
APPOINTMENT_SERVICE_URL = "http://localhost:8003"
REVIEW_SERVICE_URL = "http://localhost:8004"


async def forward_request(url: str, method: str = "GET", json_data: dict = None, headers: dict = None):
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, json=json_data, headers=headers)
        elif method == "PUT":
            response = await client.put(url, json=json_data, headers=headers)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)

        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.json())

        return response.json()


# User routes
@app.post("/auth/register")
async def register(user_data: dict):
    return await forward_request(f"{USER_SERVICE_URL}/register", "POST", user_data)


@app.post("/auth/login")
async def login(credentials: dict):
    return await forward_request(f"{USER_SERVICE_URL}/login", "POST", credentials)


@app.get("/users/me")
async def get_profile(authorization: str = None):
    headers = {"Authorization": authorization} if authorization else None
    return await forward_request(f"{USER_SERVICE_URL}/users/me", headers=headers)


@app.get("/services")
async def get_services():
    return await forward_request(f"{SERVICE_MANAGEMENT_URL}/services")


@app.post("/services")
async def create_service(service_data: dict, authorization: str = None):
    headers = {"Authorization": authorization} if authorization else None
    return await forward_request(f"{SERVICE_MANAGEMENT_URL}/services", "POST", service_data, headers)


@app.get("/services/{service_id}")
async def get_service(service_id: int):
    return await forward_request(f"{SERVICE_MANAGEMENT_URL}/services/{service_id}")


# Appointment routes
@app.post("/appointments")
async def create_appointment(appointment_data: dict, authorization: str = None):
    headers = {"Authorization": authorization} if authorization else None
    return await forward_request(f"{APPOINTMENT_SERVICE_URL}/appointments", "POST", appointment_data, headers)


@app.get("/appointments/my")
async def get_my_appointments(authorization: str = None):
    headers = {"Authorization": authorization} if authorization else None
    return await forward_request(f"{APPOINTMENT_SERVICE_URL}/appointments/my", headers=headers)


@app.put("/appointments/{appointment_id}/cancel")
async def cancel_appointment(appointment_id: int, authorization: str = None):
    headers = {"Authorization": authorization} if authorization else None
    return await forward_request(f"{APPOINTMENT_SERVICE_URL}/appointments/{appointment_id}/cancel", "PUT",
                                 headers=headers)


@app.post("/reviews")
async def create_review(review_data: dict, authorization: str = None):
    headers = {"Authorization": authorization} if authorization else None
    return await forward_request(f"{REVIEW_SERVICE_URL}/reviews", "POST", review_data, headers)


@app.get("/reviews/service/{service_id}")
async def get_service_reviews(service_id: int):
    return await forward_request(f"{REVIEW_SERVICE_URL}/reviews/service/{service_id}")
