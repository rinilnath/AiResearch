"""
Manufacturing Defect AI Agent - Main Application
Streamlit UI for defect management system
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Import our modules
from ai_agent import AIDefectAgent
from database import DefectDatabase

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Manufacturing Defect AI Agent",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "db" not in st.session_state:
    st.session_state.db = DefectDatabase()

if "ai_agent" not in st.session_state:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        st.session_state.ai_agent = AIDefectAgent(api_key)
    else:
        st.warning("⚠️ No API key found. Set ANTHROPIC_API_KEY in .env file.")
        st.session_state.ai_agent = None

# Initialize defect text in session state
if "defect_text" not in st.session_state:
    st.session_state.defect_text = ""

# Sidebar navigation
st.sidebar.title("🏭 Defect Management")
page = st.sidebar.radio(
    "Navigate to:",
    ["📝 Report Defect", "📊 Dashboard", "🎯 Defect Tracker", "📈 Reports & Analytics"],
)

st.sidebar.markdown("---")
st.sidebar.markdown("### System Status")
stats = st.session_state.db.get_summary_stats()
st.sidebar.metric("🎫 Total Defects", stats["total_defects"])
st.sidebar.metric("🔴 Critical", stats["critical_count"])
st.sidebar.metric("⚠️ High Priority", stats["high_count"])
st.sidebar.metric("✅ Resolved", stats["resolved_count"])


# ============================================
# PAGE 1: REPORT DEFECT
# ============================================
if page == "📝 Report Defect":
    st.title("🏭 Report Manufacturing Defect")
    st.markdown("### Submit a defect report using natural language")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Defect input form
        st.markdown("#### Describe the Defect")

        # Input method selection
        input_method = st.radio(
            "Input Method:",
            ["✍️ Text Input", "🎤 Voice Input (Demo)", "📸 Image + Text"],
            horizontal=True,
        )

        defect_text = ""

        if input_method == "✍️ Text Input":
            defect_text = st.text_area(
                "Describe the defect in detail:",
                value=st.session_state.defect_text,
                placeholder="Example: Hydraulic press on Line 3 is leaking oil near the base. Worker reported slippery floor and safety concern.",
                height=150,
            )
            # Update session state
            st.session_state.defect_text = defect_text

        elif input_method == "🎤 Voice Input (Demo)":
            st.info(
                "🎤 Voice input feature - In production, this would use speech recognition"
            )
            defect_text = st.text_area(
                "Voice input will appear here (simulated):",
                value=st.session_state.defect_text,
                placeholder="Click 'Use Sample Voice Input' button below",
                height=150,
                key="voice_input",
            )
            st.session_state.defect_text = defect_text
            if st.button("🎤 Use Sample Voice Input"):
                st.session_state.defect_text = "CNC machine 7 spindle motor making unusual grinding noise and vibration detected. May need bearing replacement soon."
                st.rerun()
        
        else:  # Image + Text
            st.info("📸 Image upload feature - In production, this would use OCR")
            uploaded_file = st.file_uploader("Upload defect image", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded Image", width=300)
            defect_text = st.text_area(
                "Additional description:",
                placeholder="Describe what's shown in the image...",
                height=100
            )

        # Quick templates - FIXED VERSION
        with st.expander("📋 Use Quick Templates"):
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🔧 Mechanical Issue", use_container_width=True):
                    st.session_state.defect_text = "Conveyor belt motor overheating on Line 2. Temperature gauge showing 85°C. Production slowed down by 30%."
                    st.rerun()
                if st.button("✨ Quality Issue", use_container_width=True):
                    st.session_state.defect_text = "Paint finish uneven on batch 4521. Multiple units affected. Spray nozzle may need adjustment."
                    st.rerun()
            with col_b:
                if st.button("⚡ Electrical Issue", use_container_width=True):
                    st.session_state.defect_text = "PLC error code E47 on assembly line controller. System intermittently stops. Need immediate engineering review."
                    st.rerun()
                if st.button("⚠️ Safety Issue", use_container_width=True):
                    st.session_state.defect_text = "Emergency stop button not responding on Station 7. Immediate safety hazard. Production must halt."
                    st.rerun()

        # Submit button
        st.markdown("---")
        if st.button(
            "🚀 Submit Defect Report", type="primary", use_container_width=True
        ):
            if defect_text.strip() and st.session_state.ai_agent:
                with st.spinner("🤖 AI is analyzing your defect report..."):
                    # Get historical data for context
                    historical_data = st.session_state.db.get_historical_defects()

                    # Process with AI
                    ai_result = st.session_state.ai_agent.process_defect_report(
                        defect_text,
                        historical_data if not historical_data.empty else None,
                    )

                    # Save to database
                    ticket_id = st.session_state.db.create_defect(ai_result)

                    # Show success
                    st.success(
                        f"✅ Defect reported successfully! Ticket ID: **{ticket_id}**"
                    )

                    # Store in session state for display
                    st.session_state.last_result = ai_result
                    st.session_state.last_ticket_id = ticket_id
                    st.session_state.defect_text = ""  # Clear input
                    st.rerun()
            elif not st.session_state.ai_agent:
                st.error(
                    "AI Agent not initialized. Please check your API key in .env file."
                )
            else:
                st.error("Please enter a defect description")

    with col2:
        st.markdown("#### 💡 Tips for Better Results")
        st.info(
            """
        **Include these details:**
        - 🏷️ Equipment/machine name
        - 📍 Location (Line, Station)
        - ⚠️ Problem description
        - 🔍 Observable symptoms
        - ⏱️ When it started
        - 🎯 Impact on production
        """
        )

        st.markdown("#### ✨ AI Capabilities")
        st.success(
            """
        **AI will automatically:**
        - 🎯 Categorize defect type
        - 📊 Assign priority level
        - 👥 Route to correct team
        - 💡 Suggest solutions
        - 📋 Create tracking ticket
        """
        )

    # Show last processed result
    if "last_result" in st.session_state and "last_ticket_id" in st.session_state:
        st.markdown("---")
        st.markdown("### 🎯 AI Analysis Result")

        result = st.session_state.last_result
        ticket_id = st.session_state.last_ticket_id

        # Display in nice format
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            priority_color = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢",
            }
            st.metric(
                "Priority",
                f"{priority_color.get(result['priority'], '⚪')} {result['priority']}",
            )

        with col2:
            st.metric("Category", result["category"])

        with col3:
            st.metric("Assigned Team", result["assigned_team"])

        with col4:
            st.metric("Est. Time", result.get("estimated_resolution_time", "N/A"))

        # Details in expandable sections
        col1, col2 = st.columns(2)

        with col1:
            with st.expander("📋 Extracted Information", expanded=True):
                info = result.get("extracted_info", {})
                st.write(f"**Equipment:** {info.get('equipment', 'N/A')}")
                st.write(f"**Location:** {info.get('location', 'N/A')}")
                st.write(f"**Issue:** {info.get('issue', 'N/A')}")
                if "severity_signals" in info:
                    st.write(
                        f"**Severity Signals:** {', '.join(info.get('severity_signals', []))}"
                    )

        with col2:
            with st.expander("🎯 Priority Reasoning", expanded=True):
                st.write(result.get("priority_reasoning", "No reasoning provided"))

        with st.expander("💡 Recommended Actions", expanded=True):
            actions = result.get("recommended_actions", [])
            for i, action in enumerate(actions, 1):
                st.write(f"{i}. {action}")

        # 🆕 ADD THIS NEW SECTION HERE
        if result.get("similar_cases") and len(result["similar_cases"]) > 0:
            with st.expander("🔍 Similar Past Defects (AI-Found)", expanded=True):
                st.markdown("*Based on semantic similarity search*")
                for i, case in enumerate(result["similar_cases"], 1):
                    with st.container():
                        col_a, col_b = st.columns([3, 1])
                        with col_a:
                            st.markdown(f"**{i}. {case['ticket_id']}** - {case['category']}")
                            st.caption(case['description'][:100] + "..." if len(case['description']) > 100 else case['description'])
                        with col_b:
                            st.metric("Similarity", f"{case['similarity_score']*100:.0f}%")
                            st.caption(f"Priority: {case['priority']}")
                        
                        if case.get('resolution'):
                            st.success(f"✅ Resolution: {case['resolution']}")
                        st.markdown("---")

        # Clear button
        if st.button("🔄 Report Another Defect"):
            del st.session_state.last_result
            del st.session_state.last_ticket_id
            st.rerun()


# ============================================
# PAGE 2: DASHBOARD
# ============================================
elif page == "📊 Dashboard":
    st.title("📊 Defect Management Dashboard")

    # Get statistics
    stats = st.session_state.db.get_summary_stats()

    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🎫 Total Defects", stats["total_defects"])
    with col2:
        st.metric("📖 Open", stats["open_count"])
    with col3:
        st.metric("🔄 In Progress", stats["in_progress_count"])
    with col4:
        st.metric("✅ Resolved", stats["resolved_count"])
    with col5:
        resolution_rate = (
            (stats["resolved_count"] / stats["total_defects"] * 100)
            if stats["total_defects"] > 0
            else 0
        )
        st.metric("📈 Resolution Rate", f"{resolution_rate:.1f}%")

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        # Priority distribution
        st.markdown("### 📊 Defects by Priority")
        if stats["by_priority"]:
            priority_df = pd.DataFrame(
                list(stats["by_priority"].items()), columns=["Priority", "Count"]
            )
            # Only sort by priorities that exist in the data
            priority_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            existing_priorities = [p for p in priority_order if p in priority_df["Priority"].values]
            priority_df["Priority"] = pd.Categorical(
                priority_df["Priority"], categories=existing_priorities, ordered=True
            )
            priority_df = priority_df.sort_values("Priority")

            color_map = {
                "CRITICAL": "#d62728",
                "HIGH": "#ff7f0e",
                "MEDIUM": "#ffbb00",
                "LOW": "#2ca02c",
            }

            fig = px.bar(
                priority_df,
                x="Priority",
                y="Count",
                color="Priority",
                color_discrete_map=color_map,
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    with col2:
        # Category distribution
        st.markdown("### 🏷️ Defects by Category")
        if stats["by_category"]:
            category_df = pd.DataFrame(
                list(stats["by_category"].items()), columns=["Category", "Count"]
            )

            fig = px.pie(category_df, values="Count", names="Category", hole=0.4)
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    # Recent trend
    st.markdown("### 📈 Defects Trend (Last 7 Days)")
    if stats["recent_trend"]:
        trend_df = pd.DataFrame(stats["recent_trend"], columns=["Date", "Count"])
        fig = px.line(trend_df, x="Date", y="Count", markers=True)
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No trend data available")

    # Team workload
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 👥 Team Workload")
        if stats["by_team"]:
            team_df = pd.DataFrame(
                list(stats["by_team"].items()), columns=["Team", "Assigned"]
            )
            fig = px.bar(team_df, x="Team", y="Assigned", color="Assigned")
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")

    with col2:
        st.markdown("### 🚦 Status Distribution")
        if stats["by_status"]:
            status_df = pd.DataFrame(
                list(stats["by_status"].items()), columns=["Status", "Count"]
            )
            fig = px.bar(
                status_df,
                x="Status",
                y="Count",
                color="Status",
                color_discrete_map={
                    "OPEN": "#ff7f0e",
                    "IN_PROGRESS": "#ffbb00",
                    "RESOLVED": "#2ca02c",
                },
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")


# ============================================
# PAGE 3: DEFECT TRACKER
# ============================================
elif page == "🎯 Defect Tracker":
    st.title("🎯 Defect Tracking System")

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        status_filter = st.selectbox(
            "Filter by Status", ["All", "OPEN", "IN_PROGRESS", "RESOLVED"]
        )
    with col2:
        priority_filter = st.selectbox(
            "Filter by Priority", ["All", "CRITICAL", "HIGH", "MEDIUM", "LOW"]
        )
    with col3:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All", "Mechanical", "Electrical", "Quality Control", "Safety", "Process"],
        )
    with col4:
        team_filter = st.selectbox(
            "Filter by Team",
            [
                "All",
                "Maintenance",
                "Quality Control",
                "Safety",
                "Engineering",
                "Production",
            ],
        )

    # Get defects
    defects_df = st.session_state.db.get_all_defects()

    if not defects_df.empty:
        # Apply filters
        if status_filter != "All":
            defects_df = defects_df[defects_df["status"] == status_filter]
        if priority_filter != "All":
            defects_df = defects_df[defects_df["priority"] == priority_filter]
        if category_filter != "All":
            defects_df = defects_df[defects_df["category"] == category_filter]
        if team_filter != "All":
            defects_df = defects_df[defects_df["assigned_team"] == team_filter]

        st.markdown(f"### Found {len(defects_df)} defects")

        # Display defects
        for idx, row in defects_df.iterrows():
            with st.expander(
                f"🎫 {row['ticket_id']} - {row['priority']} - {row['category']}"
            ):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**Status:** {row['status']}")
                    st.markdown(f"**Reported:** {row['timestamp'][:19]}")
                    st.markdown(f"**Equipment:** {row['equipment']}")
                    st.markdown(f"**Location:** {row['location']}")
                    st.markdown(f"**Issue:** {row['issue']}")

                    # Show actions
                    try:
                        actions = json.loads(row["recommended_actions"])
                        st.markdown("**Recommended Actions:**")
                        for i, action in enumerate(actions, 1):
                            st.write(f"{i}. {action}")
                    except:
                        pass

                with col2:
                    st.markdown(f"**Priority:** {row['priority']}")
                    st.markdown(f"**Category:** {row['category']}")
                    st.markdown(f"**Team:** {row['assigned_team']}")
                    st.markdown(f"**Est. Time:** {row['estimated_resolution_time']}")

                    # Status update
                    st.markdown("**Update Status:**")
                    new_status = st.selectbox(
                        "Change to:",
                        ["OPEN", "IN_PROGRESS", "RESOLVED"],
                        key=f"status_{row['ticket_id']}",
                        index=["OPEN", "IN_PROGRESS", "RESOLVED"].index(row["status"]),
                    )

                    notes = st.text_area(
                        "Resolution Notes:", key=f"notes_{row['ticket_id']}", height=80
                    )

                    if st.button("💾 Update", key=f"update_{row['ticket_id']}"):
                        if st.session_state.db.update_defect_status(
                            row["ticket_id"], new_status, notes
                        ):
                            st.success("✅ Status updated!")
                            st.rerun()

    else:
        st.info("No defects found. Report your first defect!")


# ============================================
# PAGE 4: REPORTS & ANALYTICS
# ============================================
elif page == "📈 Reports & Analytics":
    st.title("📈 Reports & Analytics")

    stats = st.session_state.db.get_summary_stats()
    defects_df = st.session_state.db.get_all_defects()

    if not defects_df.empty:
        # Summary Report
        st.markdown("## 📊 Executive Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### Defect Overview")
            st.write(f"**Total Defects:** {stats['total_defects']}")
            st.write(f"**Open:** {stats['open_count']}")
            st.write(f"**Resolved:** {stats['resolved_count']}")
            resolution_rate = (
                (stats["resolved_count"] / stats["total_defects"] * 100)
                if stats["total_defects"] > 0
                else 0
            )
            st.write(f"**Resolution Rate:** {resolution_rate:.1f}%")

        with col2:
            st.markdown("### Priority Breakdown")
            for priority, count in sorted(
                stats["by_priority"].items(),
                key=lambda x: ["CRITICAL", "HIGH", "MEDIUM", "LOW"].index(x[0]),
            ):
                percentage = (
                    (count / stats["total_defects"] * 100)
                    if stats["total_defects"] > 0
                    else 0
                )
                st.write(f"**{priority}:** {count} ({percentage:.1f}%)")

        with col3:
            st.markdown("### Top Categories")
            sorted_categories = sorted(
                stats["by_category"].items(), key=lambda x: x[1], reverse=True
            )
            for category, count in sorted_categories[:3]:
                percentage = (
                    (count / stats["total_defects"] * 100)
                    if stats["total_defects"] > 0
                    else 0
                )
                st.write(f"**{category}:** {count} ({percentage:.1f}%)")

        st.markdown("---")

        # Detailed table
        st.markdown("## 📋 Detailed Defect Report")

        # Prepare display dataframe
        display_df = defects_df[
            [
                "ticket_id",
                "timestamp",
                "category",
                "priority",
                "status",
                "equipment",
                "location",
                "assigned_team",
            ]
        ].copy()

        display_df["timestamp"] = pd.to_datetime(display_df["timestamp"]).dt.strftime(
            "%Y-%m-%d %H:%M"
        )

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Download report
        csv = defects_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Report (CSV)",
            data=csv,
            file_name=f"defect_report_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    else:
        st.info("📊 No data available yet. Start by reporting defects!")


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏭 Powered by AI")
st.sidebar.caption("Manufacturing Defect Management System")
