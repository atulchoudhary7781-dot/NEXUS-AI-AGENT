"""
NEXUS AI Agent - FastAPI Backend Server
Real-time autonomous agent orchestration with task management
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import json
import sqlite3
from enum import Enum
import logging
import uuid
from anthropic import Anthropic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NEXUS AI Agent API",
    description="Production-ready autonomous AI agent system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATA MODELS
# ============================================================================

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class AgentType(str, Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    CODE = "code"
    RETRIEVAL = "retrieval"
    COORDINATOR = "coordinator"

class Task(BaseModel):
    id: str
    prompt: str
    agent_type: AgentType
    status: TaskStatus
    result: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None

class TaskRequest(BaseModel):
    prompt: str
    agent_type: AgentType = AgentType.COORDINATOR
    priority: int = 5

class AgentStatus(BaseModel):
    agent_id: str
    agent_type: AgentType
    status: str
    current_task: Optional[str] = None
    tasks_completed: int
    uptime: float

class SystemMetrics(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    avg_response_time: float
    active_agents: int
    memory_usage: Dict[str, Any]

# ============================================================================
# DATABASE SETUP
# ============================================================================

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect("nexus_agent.db")
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            prompt TEXT NOT NULL,
            agent_type TEXT NOT NULL,
            status TEXT NOT NULL,
            result TEXT,
            created_at TEXT,
            completed_at TEXT,
            error TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS agent_metrics (
            agent_id TEXT PRIMARY KEY,
            agent_type TEXT NOT NULL,
            tasks_completed INT DEFAULT 0,
            total_time FLOAT DEFAULT 0,
            last_task_time TEXT
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id TEXT PRIMARY KEY,
            agent_id TEXT,
            key TEXT,
            value TEXT,
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

# ============================================================================
# AGENT SYSTEM
# ============================================================================

class Agent:
    def __init__(self, agent_id: str, agent_type: AgentType):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.status = "idle"
        self.current_task = None
        self.tasks_completed = 0
        self.client = Anthropic()
        self.conversation_history = []
    
    async def execute_task(self, prompt: str) -> str:
        """Execute task using Claude API"""
        self.status = "running"
        self.current_task = prompt
        
        try:
            # Build system prompt based on agent type
            system_prompts = {
                AgentType.RESEARCH: "You are a research specialist. Gather and synthesize information comprehensively.",
                AgentType.ANALYSIS: "You are a data analyst. Provide detailed insights and actionable recommendations.",
                AgentType.CODE: "You are an expert software engineer. Write clean, efficient, production-ready code.",
                AgentType.RETRIEVAL: "You are a knowledge retrieval specialist. Find and extract relevant information.",
                AgentType.COORDINATOR: "You are a coordinator agent. Orchestrate other agents and synthesize results.",
            }
            
            system = system_prompts.get(self.agent_type, "You are a helpful AI assistant.")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": prompt
            })
            
            # Call Claude API
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                system=system,
                messages=self.conversation_history
            )
            
            result = response.content[0].text
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": result
            })
            
            self.status = "idle"
            self.tasks_completed += 1
            
            return result
            
        except Exception as e:
            self.status = "idle"
            logger.error(f"Agent {self.agent_id} error: {str(e)}")
            raise

class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.task_queue: List[Task] = []
        self.initialize_agents()
    
    def initialize_agents(self):
        """Initialize all agent instances"""
        agent_types = [
            AgentType.RESEARCH,
            AgentType.ANALYSIS,
            AgentType.CODE,
            AgentType.RETRIEVAL,
            AgentType.COORDINATOR
        ]
        
        for agent_type in agent_types:
            agent_id = f"{agent_type.value}-{uuid.uuid4().hex[:8]}"
            self.agents[agent_id] = Agent(agent_id, agent_type)
            logger.info(f"Initialized agent: {agent_id}")
    
    async def submit_task(self, task_request: TaskRequest) -> Task:
        """Submit a task to the orchestrator"""
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            prompt=task_request.prompt,
            agent_type=task_request.agent_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now().isoformat()
        )
        
        # Save to database
        self.save_task(task)
        
        # Add to queue
        self.task_queue.append(task)
        
        return task
    
    async def execute_task(self, task: Task) -> Task:
        """Execute a task with the appropriate agent"""
        task.status = TaskStatus.RUNNING
        
        try:
            # Find appropriate agent
            agent_id = self.find_agent(task.agent_type)
            agent = self.agents[agent_id]
            
            # Execute task
            result = await agent.execute_task(task.prompt)
            
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now().isoformat()
            logger.error(f"Task {task.id} failed: {str(e)}")
        
        # Update database
        self.update_task(task)
        
        return task
    
    def find_agent(self, agent_type: AgentType) -> str:
        """Find best available agent for task type"""
        for agent_id, agent in self.agents.items():
            if agent.agent_type == agent_type and agent.status == "idle":
                return agent_id
        
        # Return first agent of type if none idle
        for agent_id, agent in self.agents.items():
            if agent.agent_type == agent_type:
                return agent_id
        
        raise ValueError(f"No agent found for type {agent_type}")
    
    def save_task(self, task: Task):
        """Save task to database"""
        conn = sqlite3.connect("nexus_agent.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO tasks (id, prompt, agent_type, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (task.id, task.prompt, task.agent_type.value, task.status.value, task.created_at))
        conn.commit()
        conn.close()
    
    def update_task(self, task: Task):
        """Update task in database"""
        conn = sqlite3.connect("nexus_agent.db")
        c = conn.cursor()
        c.execute("""
            UPDATE tasks 
            SET status = ?, result = ?, completed_at = ?, error = ?
            WHERE id = ?
        """, (task.status.value, task.result, task.completed_at, task.error, task.id))
        conn.commit()
        conn.close()

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# ============================================================================
# WEBSOCKET CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket broadcast error: {str(e)}")

manager = ConnectionManager()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_active": len(orchestrator.agents)
    }

@app.post("/tasks", response_model=Task)
async def create_task(task_request: TaskRequest, background_tasks: BackgroundTasks):
    """Create and submit a new task"""
    task = await orchestrator.submit_task(task_request)
    
    # Execute task in background
    background_tasks.add_task(orchestrator.execute_task, task)
    
    return task

@app.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """Get task status and result"""
    conn = sqlite3.connect("nexus_agent.db")
    c = conn.cursor()
    c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return Task(
        id=row[0],
        prompt=row[1],
        agent_type=AgentType(row[2]),
        status=TaskStatus(row[3]),
        result=row[4],
        created_at=row[5],
        completed_at=row[6],
        error=row[7]
    )

@app.get("/tasks", response_model=List[Task])
async def list_tasks(limit: int = 50, offset: int = 0):
    """List all tasks with pagination"""
    conn = sqlite3.connect("nexus_agent.db")
    c = conn.cursor()
    c.execute("""
        SELECT * FROM tasks 
        ORDER BY created_at DESC 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall()
    conn.close()
    
    tasks = [
        Task(
            id=row[0],
            prompt=row[1],
            agent_type=AgentType(row[2]),
            status=TaskStatus(row[3]),
            result=row[4],
            created_at=row[5],
            completed_at=row[6],
            error=row[7]
        )
        for row in rows
    ]
    
    return tasks

@app.get("/agents", response_model=List[AgentStatus])
async def list_agents():
    """Get status of all agents"""
    agent_statuses = []
    
    for agent_id, agent in orchestrator.agents.items():
        status = AgentStatus(
            agent_id=agent_id,
            agent_type=agent.agent_type,
            status=agent.status,
            current_task=agent.current_task,
            tasks_completed=agent.tasks_completed,
            uptime=0.0
        )
        agent_statuses.append(status)
    
    return agent_statuses

@app.get("/metrics", response_model=SystemMetrics)
async def get_metrics():
    """Get system-wide metrics"""
    conn = sqlite3.connect("nexus_agent.db")
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.COMPLETED.value,))
    completed_tasks = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM tasks WHERE status = ?", (TaskStatus.FAILED.value,))
    failed_tasks = c.fetchone()[0]
    
    conn.close()
    
    return SystemMetrics(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        avg_response_time=0.0,
        active_agents=len(orchestrator.agents),
        memory_usage={"available": "N/A", "used": "N/A"}
    )

@app.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time task updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"message": data})
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(websocket)

@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    conn = sqlite3.connect("nexus_agent.db")
    c = conn.cursor()
    c.execute("""
        UPDATE tasks SET status = ? WHERE id = ?
    """, (TaskStatus.FAILED.value, task_id))
    conn.commit()
    conn.close()
    
    return {"status": "cancelled", "task_id": task_id}

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    logger.info("NEXUS AI Agent Server Starting...")
    logger.info(f"Initialized {len(orchestrator.agents)} agents")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("NEXUS AI Agent Server Shutting Down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
