#!/usr/bin/env python3
"""
Agent Tools - Function Calling for Agent Engineering Bootcamp
Tool 1: RAG Document Retrieval 
Tool 2: Web Search
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from vectorize_wrapper import VectorizeWrapper
from dotenv import load_dotenv

load_dotenv()


class AgentTools:
    """
    Function calling tools for the AI agent.
    """
    
    def __init__(self):
        """Initialize the agent tools."""
        # Initialize RAG source if available
        try:
            self.rag_source = VectorizeWrapper()
            self.has_rag = True
        except:
            self.rag_source = None
            self.has_rag = False
    
    def get_available_tools(self) -> List[Dict]:
        """Get the list of available tools for the AI agent."""
        tools = []
        
        # Tool 1: RAG Document Retrieval
        if self.has_rag:
            tools.append({
                "type": "function",
                "function": {
                    "name": "search_documents",
                    "description": "Search through uploaded documents to find relevant information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query to find relevant documents"
                            },
                            "num_results": {
                                "type": "integer", 
                                "description": "Number of documents to retrieve",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            })
        
        # Tool 2: Web Search  
        tools.append({
            "type": "function",
            "function": {
                "name": "search_web",
                "description": "Search the internet for current information and news.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query for web search"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of search results",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        })
        
        return tools
    
    def search_documents(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Tool 1: Search through RAG documents.
        
        Args:
            query (str): Search query
            num_results (int): Number of results to return
            
        Returns:
            Dict with search results
        """
        if not self.has_rag:
            return {
                "success": False,
                "error": "RAG source not available",
                "results": []
            }
        
        try:
            documents = self.rag_source.retrieve_documents(query, num_results)
            
            # Format results for the agent
            formatted_results = []
            for doc in documents:
                formatted_results.append({
                    "content": doc.get("content", ""),
                    "score": doc.get("metadata", {}).get("score", "N/A"),
                    "source": "knowledge_base"
                })
            
            return {
                "success": True,
                "query": query,
                "results": formatted_results,
                "total_found": len(formatted_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching documents: {str(e)}",
                "results": []
            }
    
    def search_web(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Tool 2: Search the web for current information."""
        try:
            # Check if this is a weather query and try to get better info
            if self._is_weather_query(query):
                weather_result = self._get_weather_info(query)
                if weather_result:
                    return {
                        "success": True,
                        "query": query,
                        "results": [weather_result],
                        "total_found": 1
                    }
            
            # Check if this is a news query and try to get better info
            if self._is_news_query(query):
                news_results = self._get_news_info(query)
                if news_results:
                    return {
                        "success": True,
                        "query": query,
                        "results": news_results,
                        "total_found": len(news_results)
                    }
            
            # First try DuckDuckGo instant answers
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            
            # Check for instant answer
            if data.get("Abstract") and len(data["Abstract"]) > 10:
                results.append({
                    "title": "Instant Answer",
                    "content": data["Abstract"],
                    "url": data.get("AbstractURL", ""),
                    "source": "web_search"
                })
            
            # Check for answer (often has good info)
            if data.get("Answer") and len(data["Answer"]) > 5:
                results.append({
                    "title": "Direct Answer",
                    "content": data["Answer"],
                    "url": "",
                    "source": "web_search"
                })
            
            # Get related topics with better filtering
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and topic.get("Text"):
                    text = topic.get("Text", "")
                    if len(text) > 20:  # Only include substantial content
                        results.append({
                            "title": text[:60] + "..." if len(text) > 60 else text,
                            "content": text,
                            "url": topic.get("FirstURL", ""),
                            "source": "web_search"
                        })
            
            # If we have good results, return them
            if results and any(len(r["content"]) > 20 for r in results):
                return {
                    "success": True,
                    "query": query,
                    "results": results[:max_results],
                    "total_found": len(results)
                }
            
            # Fallback: Try to provide contextual search suggestions
            weather_keywords = ["weather", "temperature", "climate", "forecast"]
            news_keywords = ["news", "latest", "current", "today", "recent"]
            price_keywords = ["price", "cost", "value", "bitcoin", "stock"]
            
            search_type = "general"
            if any(keyword in query.lower() for keyword in weather_keywords):
                search_type = "weather"
            elif any(keyword in query.lower() for keyword in news_keywords):
                search_type = "news"
            elif any(keyword in query.lower() for keyword in price_keywords):
                search_type = "financial"
            
            # Provide helpful contextual response
            contextual_responses = {
                "weather": f"For current weather information about '{query}', I recommend checking a dedicated weather service. Weather data changes frequently and requires real-time APIs.",
                "news": f"For the latest news about '{query}', I recommend checking current news websites as news updates happen in real-time.",
                "financial": f"For current financial information about '{query}', I recommend checking a financial data service as prices change constantly.",
                "general": f"I searched for '{query}' but didn't find substantial instant answers. This might require checking current websites directly."
            }
            
            # Add some useful suggestions
            suggestions = {
                "weather": ["OpenWeatherMap", "Weather.com", "AccuWeather"],
                "news": ["Google News", "BBC News", "Reuters"],
                "financial": ["Yahoo Finance", "Bloomberg", "MarketWatch"],
                "general": ["Google Search", "Bing", "DuckDuckGo"]
            }
            
            results.append({
                "title": f"Search Performed: {query}",
                "content": f"{contextual_responses[search_type]} Recommended sources: {', '.join(suggestions[search_type])}",
                "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                "source": "web_search"
            })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_found": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error searching web: {str(e)}",
                "results": []
            }
    
    def _is_weather_query(self, query: str) -> bool:
        """Check if query is weather-related."""
        weather_keywords = ["weather", "temperature", "climate", "forecast", "rain", "sunny", "cloudy"]
        return any(keyword in query.lower() for keyword in weather_keywords)
    
    def _is_news_query(self, query: str) -> bool:
        """Check if query is news-related."""
        news_keywords = ["news", "latest", "current", "today", "recent", "breaking", "updates"]
        return any(keyword in query.lower() for keyword in news_keywords)
    
    def _get_weather_info(self, query: str) -> Optional[Dict[str, Any]]:
        """Try to get weather information using a free weather API."""
        try:
            # Extract city name from query
            city = self._extract_city_from_query(query)
            if not city:
                return None
            
            # Use a free weather service (WeatherAPI or similar)
            # For demo purposes, we'll simulate getting weather data
            weather_info = self._simulate_weather_data(city)
            
            return {
                "title": f"Weather for {city}",
                "content": weather_info,
                "url": f"https://weather.com/weather/today/l/{city.replace(' ', '+')}",
                "source": "weather_api"
            }
            
        except Exception as e:
            return None
    
    def _get_news_info(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """Try to get news information using simulated news data."""
        try:
            # For demo purposes, simulate news results
            news_items = self._simulate_news_data(query)
            return news_items
            
        except Exception as e:
            return None
    
    def _extract_city_from_query(self, query: str) -> Optional[str]:
        """Extract city name from weather query."""
        # Simple extraction - look for common patterns
        query_lower = query.lower()
        
        # Remove weather-related words
        weather_words = ["weather", "temperature", "climate", "forecast", "in", "for", "at", "the", "what", "is", "how"]
        words = [word for word in query.split() if word.lower() not in weather_words]
        
        if words:
            return " ".join(words).title()
        return None
    
    def _simulate_weather_data(self, city: str) -> str:
        """Simulate weather data for demo purposes."""
        # In a real implementation, you'd call a weather API here
        import random
        
        temperatures = [20, 22, 25, 28, 30, 32, 35]
        conditions = ["Sunny", "Partly cloudy", "Cloudy", "Light rain", "Clear"]
        
        temp = random.choice(temperatures)
        condition = random.choice(conditions)
        humidity = random.randint(40, 80)
        
        return f"Current weather in {city}: {condition}, {temp}°C (feels like {temp+2}°C). Humidity: {humidity}%. Note: This is simulated data for demo purposes. For accurate weather, check a dedicated weather service."
    
    def _simulate_news_data(self, query: str) -> List[Dict[str, Any]]:
        """Simulate news data for demo purposes."""
        import random
        
        # Extract topic from query
        topic = self._extract_news_topic(query)
        
        # Simulate realistic news headlines and content
        ai_headlines = [
            "OpenAI Announces Major Breakthrough in Multimodal AI",
            "Google DeepMind Releases New Language Model with Enhanced Reasoning",
            "Microsoft Integrates Advanced AI into Office Suite",
            "AI Startup Raises $100M for Revolutionary Computer Vision Technology",
            "New Study Shows AI Improving Healthcare Diagnosis Accuracy by 40%"
        ]
        
        general_headlines = [
            "Tech Industry Sees Record Investment in Q2 2025",
            "New Breakthrough in Quantum Computing Announced",
            "Global Climate Summit Reaches Historic Agreement",
            "Space Exploration Mission Launches Successfully",
            "Economic Markets Show Strong Growth This Quarter"
        ]
        
        headlines = ai_headlines if "ai" in topic.lower() or "artificial intelligence" in topic.lower() else general_headlines
        
        news_results = []
        for i in range(min(3, len(headlines))):
            headline = random.choice(headlines)
            headlines.remove(headline)  # Don't repeat
            
            content = f"{headline}. This is simulated news content for demo purposes. In a real implementation, this would fetch actual current news from news APIs or RSS feeds. The content would include recent developments, expert opinions, and relevant details about {topic}."
            
            news_results.append({
                "title": headline,
                "content": content,
                "url": f"https://news.example.com/{headline.lower().replace(' ', '-')}",
                "source": "news_api"
            })
        
        return news_results
    
    def _extract_news_topic(self, query: str) -> str:
        """Extract the main topic from news query."""
        # Remove news-related words to get the core topic
        news_words = ["news", "latest", "current", "today", "recent", "breaking", "updates", "what", "are", "the", "in", "for", "about"]
        words = [word for word in query.split() if word.lower() not in news_words]
        
        if words:
            return " ".join(words)
        return "general"
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with given parameters.
        
        Args:
            tool_name (str): Name of the tool to execute
            **kwargs: Tool parameters
            
        Returns:
            Dict with tool execution results
        """
        if tool_name == "search_documents":
            return self.search_documents(**kwargs)
        elif tool_name == "search_web":
            return self.search_web(**kwargs)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "results": []
            } 