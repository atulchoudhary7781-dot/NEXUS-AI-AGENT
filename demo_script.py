"""
NEXUS AI Agent - Demo Script
Showcase all capabilities with real examples
"""

import requests
import time
import json
import asyncio
from typing import List, Dict
from datetime import datetime
from enum import Enum

# Configuration
API_BASE_URL = "http://localhost:8000"
DEMO_TASKS = [
    {
        "prompt": "Analyze the top 5 emerging AI trends in 2024 and their business implications",
        "agent_type": "research",
        "priority": 9
    },
    {
        "prompt": "Write Python code for a real-time data processing pipeline using asyncio and websockets",
        "agent_type": "code",
        "priority": 8
    },
    {
        "prompt": "Provide a detailed analysis of Python vs Go for backend services with pros/cons and recommendations",
        "agent_type": "analysis",
        "priority": 7
    },
    {
        "prompt": "Retrieve and summarize the latest breakthroughs in retrieval-augmented generation (RAG) systems",
        "agent_type": "retrieval",
        "priority": 6
    },
    {
        "prompt": "Coordinate a comprehensive market analysis by delegating research, analysis, and recommendations tasks",
        "agent_type": "coordinator",
        "priority": 10
    }
]

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class DemoClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_server(self) -> bool:
        """Check if server is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def submit_task(self, prompt: str, agent_type: str, priority: int = 5) -> Dict:
        """Submit a task to the system"""
        response = self.session.post(
            f"{self.base_url}/tasks",
            json={
                "prompt": prompt,
                "agent_type": agent_type,
                "priority": priority
            }
        )
        return response.json()
    
    def get_task(self, task_id: str) -> Dict:
        """Get task status and result"""
        response = self.session.get(f"{self.base_url}/tasks/{task_id}")
        return response.json()
    
    def list_tasks(self, limit: int = 50) -> List[Dict]:
        """List all tasks"""
        response = self.session.get(f"{self.base_url}/tasks?limit={limit}")
        return response.json()
    
    def list_agents(self) -> List[Dict]:
        """List all agents"""
        response = self.session.get(f"{self.base_url}/agents")
        return response.json()
    
    def get_metrics(self) -> Dict:
        """Get system metrics"""
        response = self.session.get(f"{self.base_url}/metrics")
        return response.json()

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_section(text: str):
    """Print formatted section"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}>>> {text}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*70}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def print_task_status(task: Dict, index: int = None):
    """Print formatted task status"""
    if index is not None:
        print(f"\n{Colors.YELLOW}Task {index}:{Colors.ENDC}")
    
    status_color = {
        "completed": Colors.GREEN,
        "running": Colors.CYAN,
        "failed": Colors.RED,
        "pending": Colors.YELLOW
    }.get(task.get('status'), Colors.BLUE)
    
    print(f"  ID: {task.get('id')[:12]}...")
    print(f"  Agent: {task.get('agent_type')}")
    print(f"  Status: {status_color}{task.get('status').upper()}{Colors.ENDC}")
    print(f"  Created: {task.get('created_at')}")
    
    if task.get('completed_at'):
        print(f"  Completed: {task.get('completed_at')}")
    
    if task.get('result'):
        result_preview = task.get('result', '')[:100]
        if len(task.get('result', '')) > 100:
            result_preview += "..."
        print(f"  Result: {result_preview}")
    
    if task.get('error'):
        print(f"  Error: {Colors.RED}{task.get('error')}{Colors.ENDC}")

def demo_server_check(client: DemoClient):
    """Demo 1: Check server health"""
    print_section("1. Server Health Check")
    
    if client.check_server():
        print_success("Server is running and healthy")
        print_info(f"API Base URL: {client.base_url}")
        print_info("Ready to submit tasks!")
    else:
        print_error("Server is not responding")
        print_info("Make sure to run: python main.py")
        return False
    
    return True

def demo_list_agents(client: DemoClient):
    """Demo 2: List available agents"""
    print_section("2. Available Agents")
    
    agents = client.list_agents()
    
    if agents:
        print_info(f"Total Agents: {len(agents)}")
        for i, agent in enumerate(agents, 1):
            print(f"\n  {i}. {Colors.BOLD}{agent.get('agent_type').upper()}{Colors.ENDC}")
            print(f"     ID: {agent.get('agent_id')[:16]}...")
            print(f"     Status: {agent.get('status')}")
            print(f"     Tasks Completed: {agent.get('tasks_completed')}")
    else:
        print_error("No agents found")

def demo_submit_tasks(client: DemoClient) -> List[str]:
    """Demo 3: Submit multiple tasks"""
    print_section("3. Submitting Tasks to System")
    
    task_ids = []
    
    for i, task_config in enumerate(DEMO_TASKS, 1):
        print_info(f"Submitting task {i}/{len(DEMO_TASKS)}: {task_config['agent_type'].upper()}")
        print(f"  Prompt: {task_config['prompt'][:60]}...")
        
        try:
            task = client.submit_task(
                prompt=task_config['prompt'],
                agent_type=task_config['agent_type'],
                priority=task_config['priority']
            )
            
            task_ids.append(task.get('id'))
            print_success(f"Task submitted with ID: {task.get('id')[:12]}...")
            
        except Exception as e:
            print_error(f"Failed to submit task: {str(e)}")
        
        time.sleep(0.5)  # Delay between submissions
    
    return task_ids

def demo_monitor_tasks(client: DemoClient, task_ids: List[str]):
    """Demo 4: Monitor task execution"""
    print_section("4. Monitoring Task Execution")
    
    print_info("Waiting for tasks to complete...")
    print_info("This may take 30-60 seconds depending on API response times\n")
    
    max_attempts = 60
    attempt = 0
    completed = set()
    
    while attempt < max_attempts and len(completed) < len(task_ids):
        attempt += 1
        
        # Check each task
        for i, task_id in enumerate(task_ids):
            if task_id in completed:
                continue
            
            try:
                task = client.get_task(task_id)
                status = task.get('status')
                
                if status == "completed":
                    print_success(f"Task {i+1} ({task.get('agent_type')}) completed")
                    completed.add(task_id)
                elif status == "failed":
                    print_error(f"Task {i+1} ({task.get('agent_type')}) failed")
                    completed.add(task_id)
                elif status == "running":
                    print_info(f"Task {i+1} ({task.get('agent_type')}) running...")
                
            except Exception as e:
                print_error(f"Error checking task: {str(e)}")
        
        if len(completed) < len(task_ids):
            time.sleep(5)  # Wait before checking again
    
    print_success(f"Monitoring complete! {len(completed)}/{len(task_ids)} tasks processed")

def demo_task_details(client: DemoClient, task_ids: List[str]):
    """Demo 5: Show detailed task results"""
    print_section("5. Detailed Task Results")
    
    for i, task_id in enumerate(task_ids, 1):
        try:
            task = client.get_task(task_id)
            print_task_status(task, index=i)
            
        except Exception as e:
            print_error(f"Error fetching task details: {str(e)}")

def demo_system_metrics(client: DemoClient):
    """Demo 6: System metrics and statistics"""
    print_section("6. System Metrics & Statistics")
    
    try:
        metrics = client.get_metrics()
        
        print_info(f"Total Tasks: {metrics.get('total_tasks', 0)}")
        print_info(f"Completed Tasks: {metrics.get('completed_tasks', 0)}")
        print_info(f"Failed Tasks: {metrics.get('failed_tasks', 0)}")
        print_info(f"Active Agents: {metrics.get('active_agents', 0)}")
        
        if metrics.get('total_tasks', 0) > 0:
            success_rate = (metrics.get('completed_tasks', 0) / metrics.get('total_tasks', 0)) * 100
            print_info(f"Success Rate: {success_rate:.1f}%")
        
        print_info(f"Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s")
        
    except Exception as e:
        print_error(f"Error fetching metrics: {str(e)}")

def demo_api_examples(client: DemoClient):
    """Demo 7: API usage examples"""
    print_section("7. API Usage Examples")
    
    print_info("Get All Tasks:")
    print(f"{Colors.BOLD}curl {client.base_url}/tasks{Colors.ENDC}\n")
    
    print_info("Submit New Task:")
    print(f"{Colors.BOLD}curl -X POST {client.base_url}/tasks \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{'\"prompt\": \"Your task here\", \"agent_type\": \"coordinator\"}}{Colors.ENDC}\n")
    
    print_info("Get System Metrics:")
    print(f"{Colors.BOLD}curl {client.base_url}/metrics{Colors.ENDC}\n")
    
    print_info("List Agents:")
    print(f"{Colors.BOLD}curl {client.base_url}/agents{Colors.ENDC}\n")

def main():
    """Run complete demo"""
    
    # Print header
    print_header("🔷 NEXUS AI Agent - Live Demo")
    
    print_info("Autonomous AI Agent System with Multi-Agent Orchestration")
    print_info(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Initialize client
    client = DemoClient()
    
    # Run demos
    demos = [
        ("Server Health Check", demo_server_check),
        ("List Agents", demo_list_agents),
        ("Submit Tasks", demo_submit_tasks),
        ("Monitor Execution", demo_monitor_tasks),
        ("Task Details", demo_task_details),
        ("System Metrics", demo_system_metrics),
        ("API Examples", demo_api_examples),
    ]
    
    task_ids = []
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            if name == "Server Health Check":
                if not demo_func(client):
                    print_error("Cannot continue without server")
                    return
            elif name == "Submit Tasks":
                task_ids = demo_func(client)
            elif name == "Monitor Execution":
                demo_func(client, task_ids)
            elif name == "Task Details":
                demo_func(client, task_ids)
            else:
                demo_func(client)
            
        except Exception as e:
            print_error(f"Error in demo: {str(e)}")
    
    # Print summary
    print_header("✅ Demo Complete!")
    
    print_info("NEXUS AI Agent successfully demonstrated:")
    print(f"  ✓ Server health check")
    print(f"  ✓ Agent initialization")
    print(f"  ✓ Task submission ({len(task_ids)} tasks)")
    print(f"  ✓ Real-time monitoring")
    print(f"  ✓ Result retrieval")
    print(f"  ✓ System metrics")
    print(f"  ✓ API documentation\n")
    
    print_info("Next Steps:")
    print(f"  1. Access Dashboard: http://localhost:8501")
    print(f"  2. API Documentation: http://localhost:8000/docs")
    print(f"  3. Check GitHub: github.com/yourusername/nexus-ai-agent")
    print(f"  4. Deploy to Cloud: See DEPLOYMENT.md\n")
    
    print_success("System is ready for production use!")

if __name__ == "__main__":
    main()
