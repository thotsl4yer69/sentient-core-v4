"""
FastAPI server for Sentient Core.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def start_server(agent):
    """
    Start FastAPI server.

    Args:
        agent: SentientAgent instance
    """
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel
        import uvicorn

        app = FastAPI(
            title="Sentient Core API",
            description="API for Sentient Core v4",
            version="4.0.0"
        )

        # Request/Response models
        class ProcessRequest(BaseModel):
            input: str
            context: Dict[str, Any] = {}

        class TeamTaskRequest(BaseModel):
            task: str
            num_agents: int = 3

        # Routes
        @app.get("/")
        def root():
            return {
                "message": "Sentient Core v4 API",
                "version": "4.0.0",
                "status": "active"
            }

        @app.get("/health")
        def health():
            return agent.get_status()

        @app.post("/process")
        def process(request: ProcessRequest):
            try:
                response = agent.process(request.input, request.context)
                return {"response": response}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @app.post("/team/task")
        def team_task(request: TeamTaskRequest):
            try:
                result = agent.create_team_task(request.task, request.num_agents)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Start server
        host = agent.config.api_host
        port = agent.config.api_port

        logger.info(f"Starting server on {host}:{port}")
        print(f"\nAPI Server: http://{host}:{port}")
        print(f"API Docs: http://{host}:{port}/docs\n")

        uvicorn.run(app, host=host, port=port)

    except ImportError:
        logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
        print("Error: FastAPI not installed")
