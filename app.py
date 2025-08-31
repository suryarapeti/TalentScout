import streamlit as st
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional
import re
import pandas as pd

from modules.conversation import ConversationManager
from modules.candidate_info import CandidateInfoCollector
from modules.tech_questions import TechQuestionGenerator
from config.config import Config

st.set_page_config(
    page_title=f"{Config.APP_NAME}",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
with open("static/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    defaults = {
        'conversation_manager': ConversationManager(),
        'candidate_collector': CandidateInfoCollector(),
        'question_generator': TechQuestionGenerator(),
        'messages': [],
        'current_stage': "greeting",
        'candidate_info': {},
        'tech_stack': [],
        'questions_generated': False,
        'session_start_time': datetime.now(),
        'current_questions': [],
        'interview_complete': False,
        'current_question_index': 0,
        'answered_questions': 0,
        'skipped_questions': 0,
        'questions_intro_shown': False
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def get_progress_percentage():
    stages = {
        "greeting": 5, "collect_name": 15, "collect_email": 25,
        "collect_phone": 35, "collect_experience": 45, "collect_position": 55,
        "collect_location": 65, "collect_tech_stack": 75, "generate_questions": 85,
        "interview_complete": 100
    }
    
    # If we're in the question stage, calculate progress based on questions answered
    if st.session_state.current_stage == "generate_questions" and st.session_state.current_questions:
        base_progress = stages["generate_questions"]
        # Calculate progress based on questions completed (answered + skipped)
        completed_questions = st.session_state.answered_questions + st.session_state.skipped_questions
        question_progress = (completed_questions / len(st.session_state.current_questions)) * 10
        return min(base_progress + question_progress, 95)
    
    return stages.get(st.session_state.current_stage, 0)

def get_status_info():
    stage = st.session_state.current_stage
    if stage in ["greeting", "collect_name", "collect_email", "collect_phone", 
                "collect_experience", "collect_position", "collect_location"]:
        return ("📝 Collecting Information", "status-collecting")
    elif stage == "collect_tech_stack":
        return ("💻 Tech Stack Analysis", "status-collecting")
    elif stage == "generate_questions":
        if st.session_state.current_questions:
            # Show the next question to be answered
            current_q = st.session_state.current_question_index + 1
            total_q = len(st.session_state.current_questions)
            return (f"🎯 Question {current_q}/{total_q}", "status-ready")
        return ("🎯 Interview Ready", "status-ready")
    elif stage == "interview_complete":
        return ("✅ Complete", "status-complete")
    return ("", "")

def add_message(role: str, content: str):
    st.session_state.messages.append({
        "role": role, 
        "content": content,
        "timestamp": datetime.now().strftime("%H:%M")
    })

def display_chat():
    """Display chat messages with better formatting"""
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            # Use markdown formatting instead of HTML
            st.markdown(f"**🤖 TalentScout** ({message['timestamp']})")
            # Debug: print the message content
            print(f"DEBUG - Assistant message content: {repr(message['content'])}")
            # Clean the content to ensure no HTML-like characters cause issues
            clean_content = message['content'].replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(clean_content)
            st.divider()
        else:
            # Use markdown formatting instead of HTML
            st.markdown(f"**👤 You** ({message['timestamp']})")
            # Clean the content to ensure no HTML-like characters cause issues
            clean_content = message['content'].replace('<', '&lt;').replace('>', '&gt;')
            st.markdown(clean_content)
            st.divider()


def handle_user_input(user_input: str):
    """Handle user input based on current stage"""
    add_message("user", user_input)
    stage = st.session_state.current_stage
    manager = st.session_state.conversation_manager
    collector = st.session_state.candidate_collector
    
    if manager.is_conversation_ending(user_input):

        exit_response = "👋 Interview session terminated. Starting fresh..."
        
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        

        initialize_session_state()
        
        add_message("assistant", exit_response)
        
        new_greeting = st.session_state.conversation_manager.get_greeting()
        add_message("assistant", new_greeting)
        
        st.rerun()
        
        return 
    
    if stage == "greeting":
        # First, ask for the name
        st.session_state.current_stage = "collect_name"
        response = manager.get_name_prompt()
    
    elif stage == "collect_name":
        st.session_state.candidate_info["name"] = user_input.strip()
        st.session_state.current_stage = "collect_email"
        response = manager.get_email_prompt()
    
    elif stage == "collect_email":
        if collector.validate_email(user_input):
            st.session_state.candidate_info["email"] = user_input.strip()
            st.session_state.current_stage = "collect_phone"
            response = manager.get_phone_prompt()
        else:
            response = "⚠️ Please provide a valid email address (e.g., john@example.com)"
    
    elif stage == "collect_phone":
        if collector.validate_phone(user_input):
            st.session_state.candidate_info["phone"] = user_input.strip()
            st.session_state.current_stage = "collect_experience"
            response = manager.get_experience_prompt()
        else:
            response = "⚠️ Please provide a valid phone number (10-15 digits)"
    
    elif stage == "collect_experience":
        st.session_state.candidate_info["experience"] = user_input.strip()
        st.session_state.current_stage = "collect_position"
        response = manager.get_position_prompt()
    
    elif stage == "collect_position":
        st.session_state.candidate_info["position"] = user_input.strip()
        st.session_state.current_stage = "collect_location"
        response = manager.get_location_prompt()
    
    elif stage == "collect_location":
        st.session_state.candidate_info["location"] = user_input.strip()
        st.session_state.current_stage = "collect_tech_stack"
        response = manager.get_tech_stack_prompt()
    
    elif stage == "collect_tech_stack":
        st.session_state.tech_stack = collector.parse_tech_stack(user_input)
        st.session_state.current_stage = "generate_questions"
        
        # Generate combined questions based on experience
        questions_list = st.session_state.question_generator.generate_combined_questions(
            st.session_state.tech_stack, 
            st.session_state.candidate_info.get("experience", "1")
        )
        st.session_state.current_questions = questions_list
        
        # Show questions introduction and first question
        intro_response = manager.format_questions_intro(questions_list, st.session_state.candidate_info.get("experience", "1"))
        first_question_response = manager.format_single_question(
            questions_list[0],
            0,
            len(questions_list)
        )
        # Combine responses with proper formatting
        response = f"{intro_response}\n\n{first_question_response}"
        # Debug: print the response to see if there are any HTML tags
        print(f"DEBUG - Response content: {repr(response)}")
        st.session_state.questions_intro_shown = True
    
    elif stage == "generate_questions":
        user_lower = user_input.lower().strip()
        
        if user_lower in ["summary", "profile", "info"]:
            profile_data = st.session_state.candidate_info.copy()
            profile_data["tech_stack"] = ", ".join(st.session_state.tech_stack)
            
            summary_text = "\n".join([f"**{k.title()}:** {v}" for k, v in profile_data.items()])
            duration = datetime.now() - st.session_state.session_start_time
            duration_str = f"{int(duration.total_seconds() / 60)} minutes"
            
            response = f"""
            📊 **Your Complete Profile:**
            
            {summary_text}
            
            **Generated Questions:** {len(st.session_state.current_questions)}
            **Session Duration:** {duration_str}
            
            Would you like to download your profile or generate more questions?
            """
        
        elif user_lower in ["next", "more", "continue"]:
            response = "I can't generate more questions at this moment. You can provide your answers to the current questions or type 'done' to finish."
        
        elif user_lower == "skip":
            # Handle skip request
            if st.session_state.current_question_index < len(st.session_state.current_questions):
                st.session_state.skipped_questions += 1
                
                if st.session_state.current_question_index + 1 >= len(st.session_state.current_questions):
                    # All questions completed
                    response = manager.format_question_completion(
                        len(st.session_state.current_questions),
                        st.session_state.answered_questions,
                        st.session_state.skipped_questions
                    )
                    st.session_state.current_stage = "interview_complete"
                else:
                    # Move to next question
                    st.session_state.current_question_index += 1
                    next_question = st.session_state.current_questions[st.session_state.current_question_index]
                    response = manager.format_single_question(
                        next_question,
                        st.session_state.current_question_index,
                        len(st.session_state.current_questions)
                    )
            else:
                response = "All questions have been completed!"
        
        elif user_lower == "done":
            # Handle early completion
            response = manager.format_question_completion(
                len(st.session_state.current_questions),
                st.session_state.answered_questions,
                st.session_state.skipped_questions
            )
            st.session_state.current_stage = "interview_complete"
        
        else:
            # Handle question answers
            if not st.session_state.questions_intro_shown:
                # Show first question if intro hasn't been shown
                first_question = st.session_state.current_questions[0]
                response = manager.format_single_question(
                    first_question,
                    0,
                    len(st.session_state.current_questions)
                )
                st.session_state.questions_intro_shown = True
            else:
                # Process the answer and move to next question
                if st.session_state.current_question_index < len(st.session_state.current_questions):
                    st.session_state.answered_questions += 1
                    
                    if st.session_state.current_question_index + 1 >= len(st.session_state.current_questions):
                        # All questions completed
                        response = manager.format_question_completion(
                            len(st.session_state.current_questions),
                            st.session_state.answered_questions,
                            st.session_state.skipped_questions
                        )
                        st.session_state.current_stage = "interview_complete"
                    else:
                        # Move to next question
                        st.session_state.current_question_index += 1
                        next_question = st.session_state.current_questions[st.session_state.current_question_index]
                        response = manager.format_single_question(
                            next_question,
                            st.session_state.current_question_index,
                            len(st.session_state.current_questions)
                        )
                else:
                    # All questions completed
                    response = manager.format_question_completion(
                        len(st.session_state.current_questions),
                        st.session_state.answered_questions,
                        st.session_state.skipped_questions
                    )
                    st.session_state.current_stage = "interview_complete"
            
    else:
        response = manager.get_end_conversation_message()
    
    add_message("assistant", response)

def export_profile():
    """Export candidate profile as JSON"""
    profile = {
        "candidate_info": st.session_state.candidate_info,
        "tech_stack": st.session_state.tech_stack,
        "questions": st.session_state.current_questions,
        "session_date": datetime.now().isoformat(),
        "duration": str(datetime.now() - st.session_state.session_start_time)
    }
    return json.dumps(profile, indent=2)

def main():
    initialize_session_state()
    
    # Enhanced Sidebar with better organization
    with st.sidebar:
        # App Title with better styling
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="margin: 0; color: #667eea; font-weight: 700;">🎯 {Config.APP_NAME}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Progress Section with enhanced styling
        st.markdown("**📊 Progress Overview**")
        progress = get_progress_percentage()
        
        # Enhanced progress display
        col_prog1, col_prog2 = st.columns([3, 1])
        with col_prog1:
            st.progress(progress / 100)
        with col_prog2:
            st.markdown(f"**{progress}%**")
        
        st.markdown(f"<small>Stage: {st.session_state.current_stage.replace('_', ' ').title()}</small>", unsafe_allow_html=True)
        
        st.divider()
        
        # Status Section
        status_text, status_class = get_status_info()
        if status_text:
            st.markdown("**🎯 Current Status**")
            st.markdown(f'<div class="status-badge {status_class}">{status_text}</div>', 
                       unsafe_allow_html=True)
            st.divider()
        
        # Candidate Info Section with better organization
        if st.session_state.candidate_info:
            st.markdown("**👤 Candidate Profile**")
            
            # Create a nice info display
            for key, value in st.session_state.candidate_info.items():
                if value:  # Only show if value exists
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                        <strong>{key.title()}:</strong> {value}
                    </div>
                    """, unsafe_allow_html=True)
            
            st.divider()
        
        # Tech Stack Section
        if st.session_state.tech_stack:
            st.markdown("**💻 Technology Stack**")
            tech_display = ", ".join(st.session_state.tech_stack)
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 0.75rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                {tech_display}
            </div>
            """, unsafe_allow_html=True)
            st.divider()
        
        # Interview Progress Section
        if st.session_state.current_stage == "generate_questions" and st.session_state.current_questions:
            st.markdown("**🎯 Interview Progress**")
            
            current_q = st.session_state.current_question_index + 1
            total_q = len(st.session_state.current_questions)
            completed_q = st.session_state.answered_questions + st.session_state.skipped_questions
            
            # Progress metrics
            col_met1, col_met2 = st.columns(2)
            with col_met1:
                st.metric("Current", f"Q{current_q}")
                st.metric("Completed", f"{completed_q}/{total_q}")
            with col_met2:
                st.metric("Answered", st.session_state.answered_questions)
                st.metric("Skipped", st.session_state.skipped_questions)
            
            st.divider()
        
        # Action Buttons Section
        st.markdown("**⚡ Quick Actions**")
        
        # Exit functionality hint
        st.info("💡 Type 'bye' or 'exit' anytime to restart")
        
        # Export functionality
        if st.session_state.current_stage in ["generate_questions", "interview_complete"]:
            if st.button("📥 Export Profile", use_container_width=True, type="primary"):
                profile_data = export_profile()
                st.download_button(
                    label="💾 Download JSON",
                    data=profile_data,
                    file_name=f"candidate_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        # Reset functionality
        if st.button("🔄 Start Over", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.divider()
        
        # Footer
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; color: rgba(255,255,255,0.6);">
            <small>Powered by AI 🤖</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Main Content Area with improved layout
    # Use a centered layout with proper spacing
    col_main1, col_main2, col_main3 = st.columns([1, 10, 1])
    
    with col_main2:
        # Enhanced Header Section
        st.markdown(f'<h1 class="main-header">{Config.APP_NAME}</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">🚀 AI-powered recruitment made simple and effective</p>', unsafe_allow_html=True)
        
        # Enhanced Progress Bar with better spacing
        st.markdown("<br>", unsafe_allow_html=True)
        progress = get_progress_percentage()
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress}%"></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Chat Interface with enhanced container
        if not st.session_state.messages:
            greeting = st.session_state.conversation_manager.get_greeting()
            add_message("assistant", greeting)
        
        # Enhanced chat display with better spacing
        st.markdown("**💬 Interview Conversation**")
        
        # Chat container with better styling
        chat_container = st.container()
        with chat_container:
            # Add some padding around the chat
            st.markdown("<div style='padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 1rem; margin: 1rem 0;'>", unsafe_allow_html=True)
            display_chat()
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced Input Section
        if st.session_state.current_stage != "interview_complete":
            st.markdown("**💭 Your Response**")
            
            # Add helpful hint about exit functionality
            st.info("💡 **Tip:** You can type 'bye' or 'exit' at any time to start a new interview session.")
            
            # Use st.form for better input handling
            with st.form("chat_form", clear_on_submit=True):
                # Enhanced input field
                user_input = st.text_input(
                    "Your response:", 
                    key="user_input",
                    placeholder="Type your message here...",
                    label_visibility="collapsed"
                )
                
                # Better button layout
                col_input1, col_input2, col_input3 = st.columns([6, 1, 1])
                with col_input2:
                    submitted = st.form_submit_button("Send 📤", use_container_width=True, type="primary")
                with col_input3:
                    if st.form_submit_button("⏭️ Skip", use_container_width=True):
                        handle_user_input("skip")
                        st.rerun()
                
                # Handle input if form is submitted
                if submitted and user_input.strip():
                    handle_user_input(user_input)
                    st.rerun()
        else:
            # Enhanced completion message
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: rgba(16, 185, 129, 0.1); border-radius: 1rem; margin: 2rem 0;">
                <h2 style="color: #059669;">🎉 Interview Session Completed!</h2>
                <p style="color: #065f46;">Great job! You've successfully completed the interview process.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Final actions with better layout
            st.markdown("**📋 Final Actions**")
            col_final1, col_final2, col_final3 = st.columns([1, 1, 1])
            
            with col_final1:
                if st.button("📊 View Summary", use_container_width=True, type="secondary"):
                    st.session_state.current_stage = "generate_questions"
                    handle_user_input("summary")
                    st.rerun()
            
            with col_final2:
                if st.button("🔄 New Session", use_container_width=True, type="primary"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
            
            with col_final3:
                if st.button("📥 Export Profile", use_container_width=True, type="secondary"):
                    profile_data = export_profile()
                    st.download_button(
                        label="💾 Download",
                        data=profile_data,
                        file_name=f"candidate_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
        
        # Enhanced Quick Actions Section
        if st.session_state.current_stage == "generate_questions":
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**⚡ Quick Actions**")
            
            # Better button grid layout
            col_q1, col_q2, col_q3, col_q4 = st.columns(4)
            
            with col_q1:
                if st.button("📋 Summary", use_container_width=True, type="secondary"):
                    handle_user_input("summary")
                    st.rerun()
            
            with col_q2:
                if st.button("⏭️ Skip", use_container_width=True, type="secondary"):
                    handle_user_input("skip")
                    st.rerun()
            
            with col_q3:
                if st.button("✅ Done", use_container_width=True, type="primary"):
                    handle_user_input("done")
                    st.rerun()
            
            with col_q4:
                if st.button("🔄 Reset", use_container_width=True, type="secondary"):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
        
        # Add some bottom spacing
        st.markdown("<br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()