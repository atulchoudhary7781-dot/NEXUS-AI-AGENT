"""
NEXUS AI Agent - Streamlit Frontend Dashboard
Interactive real-time monitoring and task management UI
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from enum import Enum
import asyncio
from typing import Dict, List

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="NEXUS AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic look
st.markdown("""
<style>
    :root {
        --primary-color: #00D9FF;
        --secondary-color: #FF006E;
        --bg-color: #0A0E27;
        --card-bg: #1A1F3A;
    }
    
    .main {
        background-color: #0A0E27;
        color: #E0E0E0;
    }
    
    .stMetricLabel {
        color: #00D9FF !important;
        font-weight: bold;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #16213E 100%);
        border-left: 4px solid #00D9FF;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .task-card {
        background: linear-gradient(135deg, #1A1F3A 0%, #16213E 100%);
        border-left: 4px solid #FF006E;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    
    .status-badge {
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
    }
    
    .status-running {
        background-color: #00D9FF;
        color: #0A0E27;
    }
    
    .status-completed {
        background-color: #00FF41;
        color: #0A0E27;
    }
    
    .status-failed {
        background-color: #FF006E;
        color: white;
    }
    
    .status-pending {
        background-color: #FFA500;
        color: #0A0E27;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIG & API CLIENT
# ============================================================================

API_BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 2  # seconds

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def submit_task(self, prompt: str, agent_type: str = "coordinator") -> Dict:
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
                json={"prompt": prompt, "agent_type": agent_type}
            )
            return response.json()
        except Exception as e:
            st.error(f"Error submitting task: {str(e)}")
            return None
    
    def get_task(self, task_id: str) -> Dict:
        try:
            response = requests.get(f"{self.base_url}/tasks/{task_id}")
            return response.json()
        except:
            return None
    
    def list_tasks(self, limit: int = 50) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/tasks?limit={limit}")
            return response.json()
        except:
            return []
    
    def list_agents(self) -> List[Dict]:
        try:
            response = requests.get(f"{self.base_url}/agents")
            return response.json()
        except:
            return []
    
    def get_metrics(self) -> Dict:
        try:
            response = requests.get(f"{self.base_url}/metrics")
            return response.json()
        except:
            return {}

# Initialize API client
client = APIClient(API_BASE_URL)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("# 🔷 NEXUS AI Agent")
    st.markdown("---")
    
    # Server status
    if client.health_check():
        st.success("✅ Server Connected")
    else:
        st.error("❌ Server Offline")
    
    st.markdown("---")
    
    # Navigation
    page = st.radio("Navigate", [
        "🎯 Dashboard",
        "📝 Submit Task",
        "📊 Tasks",
        "🤖 Agents",
        "📈 Analytics"
    ])
    
    st.markdown("---")
    
    # Settings
    with st.expander("⚙️ Settings"):
        auto_refresh = st.checkbox("Auto Refresh", value=True)
        refresh_interval = st.slider("Refresh Interval (s)", 1, 10, 2)
    
    st.markdown("---")
    st.caption("NEXUS AI Agent v1.0 | Production Ready")

# ============================================================================
# DASHBOARD PAGE
# ============================================================================

if page == "🎯 Dashboard":
    st.markdown("# 🎯 Dashboard")
    
    # Get metrics
    metrics = client.get_metrics()
    agents = client.list_agents()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tasks",
            metrics.get('total_tasks', 0),
            delta=f"+{metrics.get('completed_tasks', 0)} completed"
        )
    
    with col2:
        success_rate = (metrics.get('completed_tasks', 0) / max(metrics.get('total_tasks', 1), 1)) * 100
        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
            delta=f"-{metrics.get('failed_tasks', 0)} failed"
        )
    
    with col3:
        st.metric(
            "Active Agents",
            metrics.get('active_agents', 0),
            delta="All operational"
        )
    
    with col4:
        st.metric(
            "Avg Response Time",
            f"{metrics.get('avg_response_time', 0):.2f}s"
        )
    
    st.markdown("---")
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Task status distribution
        tasks = client.list_tasks()
        if tasks:
            status_counts = pd.DataFrame(tasks).groupby('status').size()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Task Status Distribution",
                color_discrete_map={
                    "completed": "#00FF41",
                    "running": "#00D9FF",
                    "failed": "#FF006E",
                    "pending": "#FFA500"
                }
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0A0E27",
                plot_bgcolor="#1A1F3A",
                font=dict(color="#E0E0E0")
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Agent utilization
        if agents:
            agent_types = [a.get('agent_type') for a in agents]
            agent_status = [a.get('status') for a in agents]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=agent_types,
                    y=[1]*len(agent_types),
                    name="Agents",
                    marker=dict(color="#00D9FF")
                )
            ])
            fig.update_layout(
                title="Agent Status",
                xaxis_title="Agent Type",
                yaxis_title="Count",
                template="plotly_dark",
                paper_bgcolor="#0A0E27",
                plot_bgcolor="#1A1F3A",
                font=dict(color="#E0E0E0"),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Recent tasks
    st.markdown("### 📋 Recent Tasks")
    
    tasks = client.list_tasks(limit=5)
    if tasks:
        for task in tasks:
            status_color = {
                "completed": "completed",
                "running": "running",
                "failed": "failed",
                "pending": "pending"
            }.get(task.get('status'), 'pending')
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                **Task:** {task.get('prompt', '')[:100]}...
                
                **ID:** `{task.get('id', '')[:12]}...`
                """)
            
            with col2:
                st.markdown(f"<span class='status-badge status-{status_color}'>{task.get('status', 'pending').upper()}</span>", unsafe_allow_html=True)

# ============================================================================
# SUBMIT TASK PAGE
# ============================================================================

elif page == "📝 Submit Task":
    st.markdown("# 📝 Submit New Task")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        agent_type = st.selectbox(
            "Select Agent Type",
            ["coordinator", "research", "analysis", "code", "retrieval"]
        )
    
    with col2:
        priority = st.slider("Priority", 1, 10, 5)
    
    st.markdown("---")
    
    prompt = st.text_area(
        "Task Prompt",
        height=200,
        placeholder="Enter your task here...\n\nExample: Analyze the latest trends in AI and provide insights..."
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        submit_btn = st.button("🚀 Submit Task", use_container_width=True)
    
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    
    with col3:
        example_btn = st.button("📌 Load Example", use_container_width=True)
    
    # Handle buttons
    if submit_btn and prompt:
        with st.spinner("Submitting task..."):
            result = client.submit_task(prompt, agent_type)
            if result:
                st.success("✅ Task submitted successfully!")
                st.json(result)
                st.info(f"Task ID: `{result.get('id')}`")
    
    if clear_btn:
        st.rerun()
    
    if example_btn:
        st.info("Example task loaded!")

# ============================================================================
# TASKS PAGE
# ============================================================================

elif page == "📝 Tasks":
    st.markdown("# 📋 All Tasks")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox("Filter by Status", ["all", "pending", "running", "completed", "failed"])
    
    with col2:
        limit = st.slider("Limit", 10, 100, 50)
    
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    st.markdown("---")
    
    tasks = client.list_tasks(limit)
    
    if tasks:
        # Filter tasks
        if filter_status != "all":
            tasks = [t for t in tasks if t.get('status') == filter_status]
        
        # Display as table
        df = pd.DataFrame(tasks)
        df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        df['id'] = df['id'].str[:12] + '...'
        
        st.dataframe(
            df[['id', 'prompt', 'agent_type', 'status', 'created_at']],
            use_container_width=True,
            hide_index=True
        )
        
        # Detailed view
        st.markdown("---")
        st.markdown("### 📖 Task Details")
        
        selected_idx = st.selectbox("Select Task", range(len(tasks)))
        task = tasks[selected_idx]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Task Information**")
            st.text(f"ID: {task.get('id')}")
            st.text(f"Status: {task.get('status').upper()}")
            st.text(f"Agent Type: {task.get('agent_type')}")
            st.text(f"Created: {task.get('created_at')}")
        
        with col2:
            st.markdown("**Result**")
            if task.get('result'):
                st.text_area("Output", value=task.get('result'), height=150, disabled=True)
            else:
                st.info("No result yet")

# ============================================================================
# AGENTS PAGE
# ============================================================================

elif page == "🤖 Agents":
    st.markdown("# 🤖 Active Agents")
    
    if st.button("🔄 Refresh Agents"):
        st.rerun()
    
    st.markdown("---")
    
    agents = client.list_agents()
    
    if agents:
        for agent in agents:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"""
                ### {agent.get('agent_type').upper()} Agent
                **ID:** {agent.get('agent_id', '')[:16]}...
                """)
            
            with col2:
                status_text = agent.get('status', 'idle').upper()
                st.metric("Status", status_text)
            
            with col3:
                st.metric("Tasks Completed", agent.get('tasks_completed', 0))
            
            st.markdown("---")
    else:
        st.warning("No agents available")

# ============================================================================
# ANALYTICS PAGE
# ============================================================================

elif page == "📈 Analytics":
    st.markdown("# 📈 Analytics & Insights")
    
    tasks = client.list_tasks(100)
    
    if tasks:
        df = pd.DataFrame(tasks)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tasks over time
            tasks_per_hour = df.groupby(df['created_at'].dt.floor('H')).size()
            fig = px.line(
                x=tasks_per_hour.index,
                y=tasks_per_hour.values,
                title="Tasks Over Time",
                labels={"x": "Time", "y": "Count"}
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0A0E27",
                plot_bgcolor="#1A1F3A",
                font=dict(color="#E0E0E0")
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Agent type distribution
            agent_dist = df['agent_type'].value_counts()
            fig = px.bar(
                x=agent_dist.index,
                y=agent_dist.values,
                title="Tasks by Agent Type",
                labels={"x": "Agent Type", "y": "Count"}
            )
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="#0A0E27",
                plot_bgcolor="#1A1F3A",
                font=dict(color="#E0E0E0")
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No tasks data available yet")

# ============================================================================
# AUTO REFRESH
# ============================================================================

if auto_refresh:
    time.sleep(refresh_interval)
    st.rerun()
