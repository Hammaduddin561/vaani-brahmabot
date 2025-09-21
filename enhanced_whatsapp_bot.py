# enhanced_whatsapp_bot.py
"""
Enhanced WhatsApp Bot for Vaani - Bharatiya Antariksh Hackathon
Advanced conversational AI with rich responses, context management, and interactive features
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from twilio.request_validator import RequestValidator  
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client as TwilioClient
from neo4j import GraphDatabase
from dotenv import load_dotenv

# from advanced_cypher_engine import AdvancedCypherEngine  # Disabled for space interface

load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserSession:
    """Track user conversation context"""
    user_id: str
    conversation_history: List[Dict]
    last_query: Optional[str] = None
    preferred_topics: List[str] = None
    interaction_count: int = 0
    last_activity: datetime = None

class EnhancedWhatsAppBot:
    def __init__(self):
        self.router = APIRouter()
        
        # Lazy initialization - don't connect immediately to save memory
        self.driver = None
        self._neo4j_initialized = False
        
        # Lazy initialization for memory efficiency
        self.cypher_engine = None
        self.twilio_client = None
        self.validator = None
        self._twilio_initialized = False
        
        # Memory-efficient session management with automatic cleanup
        self.user_sessions: Dict[str, UserSession] = {}
        self._max_sessions = 100  # Limit active sessions
        self._session_timeout = 1800  # 30 minutes
        
        # Setup routes
        self._setup_routes()
        
        # Bot personality - minimal memory footprint
        self.bot_name = "Vaani"
        self.bot_emoji = "🚀"
    
    def _initialize_twilio(self):
        """Lazy initialize Twilio when needed"""
        if self._twilio_initialized:
            return
            
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        if account_sid and auth_token:
            self.twilio_client = TwilioClient(account_sid, auth_token)
            self.validator = RequestValidator(auth_token)
            logger.info("✅ Twilio client initialized successfully")
        else:
            logger.warning("⚠️ Twilio credentials missing")
        
        self._twilio_initialized = True
    
    def _cleanup_old_sessions(self):
        """Remove old sessions to prevent memory buildup"""
        current_time = datetime.now()
        to_remove = []
        
        for user_id, session in self.user_sessions.items():
            if session.last_activity:
                time_diff = (current_time - session.last_activity).seconds
                if time_diff > self._session_timeout:
                    to_remove.append(user_id)
        
        for user_id in to_remove:
            del self.user_sessions[user_id]
        
        # Also limit total sessions
        if len(self.user_sessions) > self._max_sessions:
            # Remove oldest sessions
            sorted_sessions = sorted(
                self.user_sessions.items(),
                key=lambda x: x[1].last_activity or datetime.min
            )
            for user_id, _ in sorted_sessions[:len(sorted_sessions) - self._max_sessions]:
                del self.user_sessions[user_id]
        
        # Generate minimal quick responses on demand
        self.quick_responses = {
            "greeting": [
                f"🚀 Namaste! I'm {self.bot_name}, your space assistant!",
                "🌟 Ready to explore the cosmos of Indian space technology?",
                "",
                "Try asking me:",
                "• List ISRO satellites 🛰️",
                "• Tell me about Chandrayaan-3 🌙", 
                "• Compare PSLV and GSLV 🚀",
                "• ISRO achievements 🏆",
                "",
                "What would you like to know about space technology?"
            ],
            "help": [
                f"🤖 {self.bot_name} can help you with:",
                "",
                "🛰️ *Satellites*: List, search, and learn about satellites",
                "🚀 *Launch Vehicles*: PSLV, GSLV, LVM3 details",
                "🌍 *Missions*: Chandrayaan, Mars Mission, Gaganyaan",
                "🏢 *Agencies*: ISRO, NASA, and other space organizations",
                "⚙️ *Technologies*: Engines, propulsion systems",
                "👨‍🚀 *People*: Scientists and space leaders",
                "📍 *Locations*: Launch centers and facilities",
                "",
                "Just ask in simple English! Example:",
                "'What satellites did ISRO launch in 2023?'"
            ],
            "capabilities": [
                f"🧠 {self.bot_name}'s Intelligence Features:",
                "",
                "🔍 *Smart Search*: Find any space-related information",
                "📊 *Comparisons*: Compare satellites, rockets, missions",
                "📈 *Statistics*: Count missions, success rates, budgets",
                "📅 *Timeline*: Events by year, launch schedules",
                "🏆 *Achievements*: Milestones and accomplishments",
                "🌐 *Global*: Both Indian and international space data",
                "",
                "💡 *Pro tip*: Ask follow-up questions for deeper insights!"
            ]
        }
        
        # Featured content for suggestions
        self.featured_topics = [
            "🌙 Chandrayaan-3 lunar mission success",
            "🚀 PSLV: India's workhorse rocket", 
            "🔴 Mars Orbiter Mission achievements",
            "👨‍🚀 Gaganyaan human spaceflight program",
            "⚡ Cryogenic engine technology",
            "🛰️ NavIC navigation constellation",
            "🏢 ISRO vs NASA comparison",
            "📡 SHAR launch center details"
        ]

    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.router.post("/whatsapp")
        async def handle_whatsapp_message(request: Request):
            return await self._process_whatsapp_message(request)
        
        @self.router.get("/whatsapp/status")
        async def get_bot_status():
            """Health check endpoint"""
            return {
                "status": "active",
                "bot_name": self.bot_name,
                "active_sessions": len(self.user_sessions),
                "timestamp": datetime.now().isoformat()
            }

    async def _process_whatsapp_message(self, request: Request) -> Response:
        """Process incoming WhatsApp messages"""
        try:
            # Parse Twilio form data
            form = await request.form()
            params = dict(form)
            
            # Verify Twilio signature (security)
            url = str(request.url)
            signature = request.headers.get("X-Twilio-Signature", "")
            
            if not self.validator.validate(url, params, signature):
                logger.warning(f"Invalid Twilio signature for {url}")
                raise HTTPException(status_code=403, detail="Invalid signature")
            
            # Extract message details
            from_number = form.get("From", "")
            incoming_message = form.get("Body", "").strip()
            message_sid = form.get("MessageSid", "")
            
            logger.info(f"📱 WhatsApp message from {from_number}: {incoming_message}")
            
            # Get or create user session
            user_session = self._get_user_session(from_number)
            
            # Process the message and generate response
            response_text, quick_replies = await self._generate_response(
                incoming_message, user_session
            )
            
            # Update session
            self._update_user_session(user_session, incoming_message, response_text)
            
            # Create Twilio response
            resp = MessagingResponse()
            msg = resp.message()
            msg.body(response_text)
            
            # Add quick reply buttons if available (Twilio supports limited interactive features)
            if quick_replies and len(quick_replies) <= 3:
                for reply in quick_replies:
                    # Note: Full interactive buttons require Twilio Conversations API
                    # For basic WhatsApp, we include suggestions in the message
                    pass
            
            return Response(content=str(resp), media_type="application/xml")
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            
            # Error response
            resp = MessagingResponse()
            msg = resp.message()
            msg.body(f"🔧 Oops! {self.bot_name} encountered a technical issue. Please try again in a moment.")
            
            return Response(content=str(resp), media_type="application/xml")

    def _get_user_session(self, user_id: str) -> UserSession:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = UserSession(
                user_id=user_id,
                conversation_history=[],
                preferred_topics=[],
                last_activity=datetime.now()
            )
        
        session = self.user_sessions[user_id]
        session.last_activity = datetime.now()
        return session

    def _update_user_session(self, session: UserSession, user_message: str, bot_response: str):
        """Update user session with new interaction"""
        session.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "bot_response": bot_response[:100] + "..." if len(bot_response) > 100 else bot_response
        })
        
        # Keep only last 10 interactions to manage memory
        if len(session.conversation_history) > 10:
            session.conversation_history = session.conversation_history[-10:]
        
        session.interaction_count += 1
        session.last_query = user_message

    async def _generate_response(self, message: str, session: UserSession) -> Tuple[str, List[str]]:
        """Generate intelligent response to user message"""
        message_lower = message.lower().strip()
        
        # Handle special commands and greetings
        if self._is_greeting(message_lower):
            return self._format_response(self.quick_responses["greeting"]), []
        
        if message_lower in ['help', 'menu', 'options', 'what can you do']:
            return self._format_response(self.quick_responses["help"]), []
        
        if message_lower in ['features', 'capabilities', 'abilities']:
            return self._format_response(self.quick_responses["capabilities"]), []
        
        if message_lower in ['suggest', 'suggestions', 'topics', 'examples']:
            return self._generate_suggestions(), []
        
        if message_lower in ['thanks', 'thank you', 'bye', 'goodbye']:
            return self._generate_farewell_message(session), []
        
        # Generate Cypher query
        cypher_query = self.cypher_engine.generate_cypher(message)
        
        # Handle special query types
        if cypher_query == "__greeting__":
            return self._format_response(self.quick_responses["greeting"]), []
        
        if cypher_query == "__suggestion__":
            return self._generate_suggestions(), []
        
        # Execute query and format response
        try:
            results = await self._execute_cypher_query(cypher_query)
            return self._format_query_results(message, results, cypher_query), []
            
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            return self._generate_error_response(message), []

    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = [
            'hi', 'hello', 'hey', 'namaste', 'start', 'begin',
            'good morning', 'good afternoon', 'good evening'
        ]
        return any(greeting in message for greeting in greetings)

    async def _execute_cypher_query(self, cypher: str) -> List[Dict]:
        """Execute Cypher query against Neo4j"""
        if not cypher or cypher.startswith("__"):
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(cypher)
                records = [record.data() for record in result]
                return records
        except Exception as e:
            logger.error(f"Neo4j query error: {e}")
            raise

    def _format_query_results(self, original_query: str, results: List[Dict], cypher: str) -> str:
        """Format query results into user-friendly WhatsApp message"""
        if not results:
            return self._generate_no_results_message(original_query)
        
        # Determine result type and format accordingly
        result_type = self._detect_result_type(results)
        
        if result_type == "satellite_list":
            return self._format_satellite_results(results)
        elif result_type == "mission_info":
            return self._format_mission_results(results)
        elif result_type == "vehicle_info":
            return self._format_vehicle_results(results)
        elif result_type == "agency_info":
            return self._format_agency_results(results)
        elif result_type == "comparison":
            return self._format_comparison_results(results)
        elif result_type == "statistics":
            return self._format_statistics_results(results)
        else:
            return self._format_generic_results(results)

    def _detect_result_type(self, results: List[Dict]) -> str:
        """Detect the type of results to format appropriately"""
        if not results:
            return "empty"
        
        first_result = results[0]
        
        if "satellite_name" in first_result:
            return "satellite_list"
        elif "mission_name" in first_result:
            return "mission_info"
        elif "vehicle_name" in first_result:
            return "vehicle_info"
        elif "agency_name" in first_result:
            return "agency_info"
        elif "comparison_values" in first_result:
            return "comparison"
        elif any(key.endswith("_count") for key in first_result.keys()):
            return "statistics"
        else:
            return "generic"

    def _format_satellite_results(self, results: List[Dict]) -> str:
        """Format satellite query results"""
        response = [f"🛰️ *Satellite Information* ({len(results)} found):", ""]
        
        for i, satellite in enumerate(results[:8], 1):  # Limit to 8 results for WhatsApp
            name = satellite.get("satellite_name", "Unknown")
            purpose = satellite.get("purpose", "N/A")
            launch_date = satellite.get("launch_date", "N/A")
            launch_vehicle = satellite.get("launch_vehicle", "")
            
            response.append(f"*{i}. {name}*")
            response.append(f"   📅 Launch: {launch_date}")
            response.append(f"   🎯 Purpose: {purpose}")
            if launch_vehicle:
                response.append(f"   🚀 Vehicle: {launch_vehicle}")
            response.append("")
        
        if len(results) > 8:
            response.append(f"... and {len(results) - 8} more satellites")
            response.append("")
        
        response.append("💡 Ask for details about any specific satellite!")
        
        return self._format_response(response)

    def _format_mission_results(self, results: List[Dict]) -> str:
        """Format mission query results"""
        response = [f"🚀 *Mission Information* ({len(results)} found):", ""]
        
        for i, mission in enumerate(results[:5], 1):
            name = mission.get("mission_name", "Unknown")
            objective = mission.get("objective", "N/A")
            status = mission.get("status", "N/A")
            agency = mission.get("agency", "")
            achievements = mission.get("achievements", [])
            
            response.append(f"*{i}. {name}*")
            response.append(f"   🎯 Goal: {objective}")
            response.append(f"   📊 Status: {status}")
            if agency:
                response.append(f"   🏢 Agency: {agency}")
            
            if achievements and isinstance(achievements, list):
                response.append(f"   🏆 Key achievements:")
                for achievement in achievements[:2]:  # Limit achievements
                    response.append(f"     • {achievement}")
            response.append("")
        
        return self._format_response(response)

    def _format_vehicle_results(self, results: List[Dict]) -> str:
        """Format launch vehicle query results"""
        response = [f"🚀 *Launch Vehicle Information*:", ""]
        
        for vehicle in results[:3]:  # Limit to 3 vehicles
            name = vehicle.get("vehicle_name", "Unknown")
            full_name = vehicle.get("full_name", "")
            capacity = vehicle.get("payload_capacity_kg", "N/A")
            success_rate = vehicle.get("success_rate", "N/A")
            first_flight = vehicle.get("first_flight", "N/A")
            
            response.append(f"*🚀 {name}*")
            if full_name and full_name != name:
                response.append(f"   Full name: {full_name}")
            response.append(f"   📦 Payload: {capacity} kg")
            response.append(f"   ✅ Success rate: {success_rate}%")
            response.append(f"   🗓️ First flight: {first_flight}")
            response.append("")
        
        return self._format_response(response)

    def _format_agency_results(self, results: List[Dict]) -> str:
        """Format agency query results"""
        response = [f"🏢 *Space Agencies*:", ""]
        
        for agency in results[:4]:
            name = agency.get("agency_name", "Unknown")
            full_name = agency.get("full_name", "")
            country = agency.get("country", "N/A")
            budget = agency.get("budget_usd", "")
            
            response.append(f"*{name}*")
            if full_name and full_name != name:
                response.append(f"   {full_name}")
            response.append(f"   🌍 Country: {country}")
            if budget:
                budget_billions = budget / 1_000_000_000
                response.append(f"   💰 Budget: ${budget_billions:.1f}B USD")
            response.append("")
        
        return self._format_response(response)

    def _format_statistics_results(self, results: List[Dict]) -> str:
        """Format statistical query results"""
        response = ["📊 *Statistics*:", ""]
        
        for stat in results:
            for key, value in stat.items():
                if key.endswith("_count") or key == "count":
                    category = key.replace("_count", "").replace("_", " ").title()
                    response.append(f"📈 {category}: *{value}*")
                elif key == "total_satellites":
                    response.append(f"🛰️ Total Satellites: *{value}*")
                elif key == "total_missions":
                    response.append(f"🚀 Total Missions: *{value}*")
        
        return self._format_response(response)

    def _format_generic_results(self, results: List[Dict]) -> str:
        """Format generic query results"""
        response = [f"🔍 *Search Results* ({len(results)} found):", ""]
        
        for i, result in enumerate(results[:6], 1):
            # Find the most important fields to display
            name = result.get("name") or result.get("satellite_name") or result.get("mission_name") or "Item"
            description = result.get("description") or result.get("purpose") or result.get("objective") or ""
            
            response.append(f"*{i}. {name}*")
            if description:
                response.append(f"   {description}")
            response.append("")
        
        return self._format_response(response)

    def _format_comparison_results(self, results: List[Dict]) -> str:
        """Format comparison query results"""
        if not results:
            return "No comparison data available."
        
        comparison = results[0]
        entity1 = comparison.get("first_entity", "Entity 1")
        entity2 = comparison.get("second_entity", "Entity 2") 
        values = comparison.get("comparison_values", [])
        
        response = [
            "🔄 *Comparison Results*:",
            "",
            f"*{entity1}* vs *{entity2}*"
        ]
        
        if len(values) >= 2:
            response.append(f"📊 Values: {values[0]} vs {values[1]}")
        
        return self._format_response(response)

    def _generate_suggestions(self) -> str:
        """Generate topic suggestions"""
        response = [
            f"💡 *{self.bot_name}'s Featured Topics*:",
            "",
            "Here are some interesting space topics to explore:"
        ]
        
        # Add featured topics
        for i, topic in enumerate(self.featured_topics[:6], 1):
            response.append(f"{i}. {topic}")
        
        response.extend([
            "",
            "Just type your question naturally!",
            "Example: 'Tell me about Chandrayaan-3'"
        ])
        
        return self._format_response(response)

    def _generate_no_results_message(self, query: str) -> str:
        """Generate message for no results found"""
        response = [
            "🔍 *No results found*",
            "",
            f"I couldn't find information about '{query}'.",
            "",
            "💡 *Try these instead*:",
            "• Use simpler terms (e.g., 'ISRO satellites')",
            "• Check spelling",
            "• Ask about Indian space missions",
            "• Type 'help' for more options"
        ]
        
        return self._format_response(response)

    def _generate_error_response(self, query: str) -> str:
        """Generate error response"""
        return self._format_response([
            "🔧 *Technical Issue*",
            "",
            f"Sorry, I encountered a problem processing '{query}'.",
            "",
            "Please try:",
            "• Asking a simpler question",
            "• Typing 'help' for options",
            "• Trying again in a moment"
        ])

    def _generate_farewell_message(self, session: UserSession) -> str:
        """Generate personalized farewell"""
        interaction_count = session.interaction_count
        
        if interaction_count <= 1:
            farewell = "Thanks for trying Vaani! 🚀"
        elif interaction_count <= 5:
            farewell = f"Thanks for the {interaction_count} questions! Keep exploring space! 🌟"
        else:
            farewell = f"Wow, {interaction_count} questions! You're a space enthusiast! 🚀🌟"
        
        return self._format_response([
            farewell,
            "",
            "Feel free to come back anytime to explore",
            "the fascinating world of space technology!",
            "",
            "🚀 Keep reaching for the stars! 🌟"
        ])

    def _format_response(self, lines: List[str]) -> str:
        """Format response lines into WhatsApp message"""
        # Add bot signature
        formatted_lines = [f"🚀 *{self.bot_name}* - Space Knowledge AI"] + [""] + lines
        
        # Join lines and ensure proper WhatsApp formatting
        response = "\n".join(formatted_lines)
        
        # Ensure message isn't too long (WhatsApp has 4096 character limit)
        if len(response) > 4000:
            response = response[:3900] + "\n\n... (truncated)\nAsk for more specific details!"
        
        return response

    def cleanup_old_sessions(self):
        """Clean up old user sessions (call periodically)"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        sessions_to_remove = [
            user_id for user_id, session in self.user_sessions.items()
            if session.last_activity < cutoff_time
        ]
        
        for user_id in sessions_to_remove:
            del self.user_sessions[user_id]
        
        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")

    async def process_message(self, message_body: str, sender_number: str, message_sid: str) -> dict:
        """Process incoming WhatsApp message"""
        try:
            # Get or create user session
            user_id = sender_number.replace("whatsapp:", "")
            session = self._get_or_create_session(user_id)
            
            # Update session
            session.conversation_history.append({
                "timestamp": datetime.now(),
                "user_message": message_body,
                "message_id": message_sid
            })
            session.interaction_count += 1
            session.last_activity = datetime.now()
            
            # Generate response
            response_text, suggestions = await self._generate_response(message_body, session)
            
            # Store response in session
            session.conversation_history[-1]["bot_response"] = response_text
            
            # Send WhatsApp message
            twilio_response = self._send_whatsapp_message(sender_number, response_text)
            
            return {
                "success": True,
                "response": response_text,
                "suggestions": suggestions,
                "twilio_response": twilio_response
            }
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_whatsapp_message(self, to_number: str, message_text: str) -> dict:
        """Send a WhatsApp message using Twilio"""
        try:
            if not self.twilio_client:
                return {
                    "success": False,
                    "error": "Twilio client not initialized"
                }
            
            if not self.twilio_phone_number:
                return {
                    "success": False,
                    "error": "Twilio phone number not configured"
                }
            
            # Format numbers for WhatsApp
            from_number = self.twilio_phone_number
            if not from_number.startswith("whatsapp:"):
                from_number = f"whatsapp:{from_number}"
            
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"
            
            # Send message
            message = self.twilio_client.messages.create(
                body=message_text,
                from_=from_number,
                to=to_number
            )
            
            logger.info(f"✅ WhatsApp message sent: {message.sid}")
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close(self):
        """Close database connections"""
        if self.driver:
            self.driver.close()

# Global bot instance
enhanced_whatsapp_bot = EnhancedWhatsAppBot()

# FastAPI router for integration
router = enhanced_whatsapp_bot.router