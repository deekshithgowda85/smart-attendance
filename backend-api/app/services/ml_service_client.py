import httpx
import os
from typing import List, Dict, Optional


class MLServiceClient:
    """
    Client for communicating with the ML Face Recognition Service.
    """
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("ML_SERVICE_URL", "http://localhost:8001")
        self.timeout = 30.0  # Face operations can take time
    
    async def register_face(self, student_id: str, image_bytes: bytes) -> Dict:
        """
        Register a face by sending image to ML service.
        
        Args:
            student_id: Student identifier
            image_bytes: Image file bytes
        
        Returns:
            Response from ML service
        
        Raises:
            httpx.HTTPError: If ML service is unreachable
            Exception: If ML service returns error
        """
        url = f"{self.base_url}/api/face/register-face"
        
        files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
        data = {"student_id": student_id}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, files=files, data=data)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"ML Service error: {str(e)}")
    
    async def register_face_base64(self, student_id: str, image_base64: str) -> Dict:
        """
        Register a face using base64 encoded image.
        
        Args:
            student_id: Student identifier
            image_base64: Base64 encoded image
        
        Returns:
            Response from ML service
        """
        url = f"{self.base_url}/api/face/register-face-base64"
        
        payload = {
            "student_id": student_id,
            "image_base64": image_base64
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"ML Service error: {str(e)}")
    
    async def recognize_faces(
        self, 
        image_base64: str, 
        student_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Recognize faces in an image.
        
        Args:
            image_base64: Base64 encoded image
            student_ids: Optional list of student IDs to search within
        
        Returns:
            Response from ML service with recognized faces
        """
        url = f"{self.base_url}/api/face/recognize-face"
        
        payload = {
            "image_base64": image_base64,
            "student_ids": student_ids
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"ML Service error: {str(e)}")
    
    async def health_check(self) -> bool:
        """
        Check if ML service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        url = f"{self.base_url}/api/face/health"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                response = await client.get(url)
                return response.status_code == 200
            except:
                return False
    
    async def delete_embeddings(self, student_id: str) -> Dict:
        """
        Delete embeddings for a student.
        
        Args:
            student_id: Student identifier
        
        Returns:
            Response from ML service
        """
        url = f"{self.base_url}/api/face/embeddings/{student_id}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.delete(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                raise Exception(f"ML Service error: {str(e)}")


# Global ML service client instance
ml_service_client = MLServiceClient()
