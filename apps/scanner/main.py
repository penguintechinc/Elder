"""Elder Local Scanner Service.

Polls the Elder API for pending scan jobs and executes them.
"""

import asyncio
import logging
import os
import sys
import time
from typing import Any, Dict, Optional

import httpx

from scanners.network import NetworkScanner
from scanners.http_screenshot import HTTPScreenshotScanner
from scanners.banner import BannerScanner

# Configuration from environment
POLL_INTERVAL = int(os.getenv("SCANNER_POLL_INTERVAL", "300"))
API_URL = os.getenv("ELDER_API_URL", "http://api:5000")
API_TOKEN = os.getenv("ELDER_API_TOKEN", "")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "/app/screenshots")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("scanner")


class ScannerService:
    """Main scanner service that polls for and executes scan jobs."""

    def __init__(self):
        self.api_url = API_URL.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
        }
        if API_TOKEN:
            self.headers["Authorization"] = f"Bearer {API_TOKEN}"

        # Initialize scanners
        self.scanners = {
            "network": NetworkScanner(),
            "http_screenshot": HTTPScreenshotScanner(screenshot_dir=SCREENSHOT_DIR),
            "banner": BannerScanner(),
        }

        # Ensure screenshot directory exists
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    async def get_pending_jobs(self) -> list:
        """Fetch pending scan jobs from the API."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/api/v1/discovery/jobs/pending",
                    headers=self.headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("jobs", [])
                else:
                    logger.error(
                        f"Failed to fetch pending jobs: {response.status_code}"
                    )
                    return []
        except Exception as e:
            logger.error(f"Error fetching pending jobs: {e}")
            return []

    async def mark_job_running(self, job_id: int) -> bool:
        """Mark a job as running."""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/v1/discovery/jobs/{job_id}/start",
                    headers=self.headers,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error marking job {job_id} as running: {e}")
            return False

    async def submit_results(
        self,
        job_id: int,
        success: bool,
        results: Dict[str, Any],
        error_message: Optional[str] = None,
    ) -> bool:
        """Submit scan results back to the API."""
        try:
            payload = {
                "success": success,
                "results": results,
                "error_message": error_message,
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/v1/discovery/jobs/{job_id}/complete",
                    headers=self.headers,
                    json=payload,
                )
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error submitting results for job {job_id}: {e}")
            return False

    async def execute_job(self, job: Dict[str, Any]) -> None:
        """Execute a single scan job."""
        job_id = job["id"]
        provider = job["provider"]
        config = job.get("config_json", {})

        logger.info(f"Executing job {job_id} (type: {provider})")

        # Mark job as running
        if not await self.mark_job_running(job_id):
            logger.error(f"Failed to mark job {job_id} as running")
            return

        # Get appropriate scanner
        scanner = self.scanners.get(provider)
        if not scanner:
            error_msg = f"Unknown scanner type: {provider}"
            logger.error(error_msg)
            await self.submit_results(job_id, False, {}, error_msg)
            return

        # Execute scan
        try:
            results = await scanner.scan(config)
            await self.submit_results(job_id, True, results)
            logger.info(f"Job {job_id} completed successfully")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Job {job_id} failed: {error_msg}")
            await self.submit_results(job_id, False, {}, error_msg)

    async def run(self) -> None:
        """Main poll loop."""
        logger.info(f"Scanner service started. Polling every {POLL_INTERVAL}s")
        logger.info(f"API URL: {self.api_url}")

        while True:
            try:
                # Fetch pending jobs
                jobs = await self.get_pending_jobs()

                if jobs:
                    logger.info(f"Found {len(jobs)} pending job(s)")
                    for job in jobs:
                        await self.execute_job(job)
                else:
                    logger.debug("No pending jobs")

            except Exception as e:
                logger.error(f"Error in poll loop: {e}")

            # Wait before next poll
            await asyncio.sleep(POLL_INTERVAL)


def main():
    """Entry point."""
    service = ScannerService()
    asyncio.run(service.run())


if __name__ == "__main__":
    main()
