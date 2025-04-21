import json
import logging
from enum import Enum
from typing import Any, Callable, Dict, Optional

import requests

import src.config.env as env
from src.app.models.llm_models import ChatHistory
from src.app.services.database_services import DatabaseService
from src.app.services.embedding_services import EmbeddingService

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    DIGITAL_OCEAN = "Digital Ocean"
    OLLAMA = "Ollama"


class LLMService:
    """Service for LLM operations"""

    @classmethod
    def generate_response(
        cls,
        context: str,
        query: str,
        provider: LLMProvider = LLMProvider.DIGITAL_OCEAN,
        stream_callback: Optional[Callable[[str], None]] = None,
        debug_mode: bool = False,
    ) -> str:
        """Generate a response using the selected LLM provider"""
        if provider == LLMProvider.DIGITAL_OCEAN:
            return cls.generate_digital_ocean_response(
                context, query, stream_callback, debug_mode
            )
        else:  # provider == LLMProvider.OLLAMA
            return cls.generate_ollama_response(context, query, stream_callback)

    @classmethod
    def generate_digital_ocean_response(
        cls,
        context: str,
        query: str,
        stream_callback: Optional[Callable[[str], None]] = None,
        debug_mode: bool = False,
    ) -> str:
        """Generate a response using Digital Ocean GenAI Agent API"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {env.DO_API_KEY}",
            }

            # Structured prompt for consistent output with emphasis on detailed answers
            prompt = f"""
            Response and think in Indonesia Language:
            Based on the following documents:
            {context}

            User question: {query}

            Please provide a structured response with the following sections:
            1. **Documents Referenced**: List the documents or state if none are relevant.
            2. **User Question**: Restate the user's question.
            3. **Answer**: Provide a comprehensive and detailed answer based solely on the documents. Include all relevant information, context, and nuances from the documents. Elaborate on key points, provide examples if available, and explain concepts thoroughly. If the documents do not contain the answer, state clearly that the information is not available and explain what specific aspects are missing.
            4. **Conclusion**: Summarize the key points from your detailed answer in a concise manner. Highlight the most important findings or confirm the lack of information.
            """

            # Payload for Digital Ocean AI API
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000,
                "stream": stream_callback is not None,
            }

            # Use the working API endpoint
            api_endpoint = f"{env.DO_API_URL}/api/v1/chat/completions"

            # Show debug information if requested
            if debug_mode:
                logger.debug(f"Sending request to: {api_endpoint}")
                logger.debug(f"Payload structure: {json.dumps(payload, indent=2)}")

            if stream_callback:
                return cls._handle_streaming_response(
                    api_endpoint, headers, payload, stream_callback, debug_mode
                )
            else:
                return cls._handle_normal_response(
                    api_endpoint, headers, payload, debug_mode
                )

        except Exception as e:
            error_msg = f"Error calling Digital Ocean AI: {str(e)}"
            logger.error(error_msg)
            return f"Error: {str(e)}"

    @classmethod
    def _handle_streaming_response(
        cls,
        api_endpoint: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        stream_callback: Callable[[str], None],
        debug_mode: bool = False,
    ) -> str:
        """Handle streaming response from Digital Ocean API"""
        full_response = ""

        try:
            with requests.post(
                api_endpoint,
                headers=headers,
                json=payload,
                stream=True,
            ) as response:
                if debug_mode:
                    logger.debug(f"Response status code: {response.status_code}")

                if response.status_code != 200:
                    error_content = response.text
                    error_msg = f"Error from Digital Ocean AI: {response.status_code}"
                    logger.error(error_msg)
                    if debug_mode:
                        logger.error(f"Error details: {error_content}")
                    return f"Error: {response.status_code}"

                # Process streaming response
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode("utf-8")
                            if line_text.startswith("data: "):
                                line_text = line_text[6:]  # Remove "data: " prefix

                            if line_text.strip() == "[DONE]" or line_text.strip() == "":
                                continue

                            json_line = json.loads(line_text)

                            if "choices" in json_line and json_line["choices"]:
                                if "delta" in json_line["choices"][0]:
                                    delta = json_line["choices"][0].get("delta", {})
                                    content = delta.get("content", "")
                                    if content:
                                        full_response += content
                                        if stream_callback:
                                            stream_callback(full_response)
                                elif "text" in json_line["choices"][0]:
                                    content = json_line["choices"][0].get("text", "")
                                    if content:
                                        full_response += content
                                        if stream_callback:
                                            stream_callback(full_response)
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            if debug_mode:
                                logger.warning(f"Error processing stream line: {e}")
                            continue

            return full_response
        except Exception as e:
            error_msg = f"Error in streaming response: {e}"
            logger.error(error_msg)
            return f"Error: {str(e)}"

    @classmethod
    def _handle_normal_response(
        cls,
        api_endpoint: str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
        debug_mode: bool = False,
    ) -> str:
        """Handle normal (non-streaming) response from Digital Ocean API"""
        try:
            response = requests.post(api_endpoint, headers=headers, json=payload)

            if debug_mode:
                logger.debug(f"Response status code: {response.status_code}")

            if response.status_code != 200:
                error_content = response.text
                error_msg = f"Error from Digital Ocean AI: {response.status_code}"
                logger.error(error_msg)
                if debug_mode:
                    logger.error(f"Error details: {error_content}")
                return f"Error: {response.status_code}"

            result = response.json()

            if debug_mode:
                logger.debug(f"Response structure: {json.dumps(result, indent=2)}")

            if "choices" in result and result["choices"]:
                return (
                    result["choices"][0]
                    .get("message", {})
                    .get("content", "No content in response")
                )

            return "No valid response content received"
        except Exception as e:
            error_msg = f"Error in non-streaming response: {e}"
            logger.error(error_msg)
            return f"Error: {str(e)}"

    @classmethod
    def generate_ollama_response(
        cls,
        context: str,
        query: str,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Generate a response from Ollama with DeepSeek-R1 and custom prompt"""
        system_prompt = """
        Response and think in Indonesia Language

        You are an AI assistant tasked with providing structured, accurate answers based solely on the provided documents. Follow this format for your response:

        1. **Documents Referenced**: List the documents used to answer the question (by filename or ID). If no documents are relevant, state "No relevant documents found."
        2. **User Question**: Restate the user's question verbatim.
        3. **Answer**: Provide a comprehensive and detailed answer based only on the documents. Include all relevant information, context, and nuances from the documents. Elaborate on key points, provide examples if available, and explain concepts thoroughly. If the documents do not contain the answer, state: "The provided documents do not contain sufficient information to answer this question" and explain what specific aspects are missing.
        4. **Conclusion**: Summarize the key points from your detailed answer in a concise manner. Highlight the most important findings or confirm that no answer was found in the documents.

        Do not invent or improvise information. If the answer is not in the documents, be honest and clear about it.
        """
        prompt = f"Documents:\n{context}\n\nUser Question: {query}"
        # Buat payload seperti biasa
        payload = {
            "model": env.OLLAMA_MODEL,
            "prompt": prompt,
            "system": system_prompt,
            "stream": stream_callback is not None,
        }

        # Log payload lengkap
        logger.info(f"Ollama request URL: {env.OLLAMA_API_URL}")
        logger.info(f"Ollama request payload: {json.dumps(payload, indent=2)}")

        # Handle either streaming or normal response based on callback presence
        try:
            if stream_callback:
                return cls._handle_ollama_streaming_response(payload, stream_callback)
            else:
                return cls._handle_ollama_normal_response(payload)
        except Exception as e:
            error_msg = f"Ollama request failed: {str(e)}"
            logger.error(error_msg)
            return f"Error: {str(e)}"  # Return error message as string instead of None

    @classmethod
    def _handle_ollama_streaming_response(
        cls, payload: Dict[str, Any], stream_callback: Callable[[str], None]
    ) -> str:
        """Handle streaming response from Ollama API"""
        full_response = ""

        try:
            with requests.post(
                env.OLLAMA_API_URL, json=payload, stream=True
            ) as response:
                response.raise_for_status()

                # Process streaming response
                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        # Decode the line
                        line_text = line.decode("utf-8")

                        # Parse JSON response
                        chunk = json.loads(line_text)

                        # Extract response content
                        if "response" in chunk:
                            content = chunk.get("response", "")
                            if content:
                                full_response += content
                                stream_callback(full_response)

                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.warning(f"Error processing Ollama stream chunk: {e}")
                        continue

            return full_response
        except Exception as e:
            error_msg = f"Error in Ollama streaming response: {e}"
            logger.error(error_msg)
            return f"Error: {str(e)}"

    @classmethod
    def _handle_ollama_normal_response(cls, payload: Dict[str, Any]) -> str:
        """Handle normal (non-streaming) response from Ollama"""
        try:
            response = requests.post(env.OLLAMA_API_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.RequestException as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error: {str(e)}"

    @classmethod
    def generate_chat_title(
        cls,
        query: str,
        response: str,
        provider: LLMProvider = LLMProvider.DIGITAL_OCEAN,
    ) -> str:
        """Generate a title for the chat using the LLM model"""
        prompt = f"""
        generate a concise title (5-10 words) that summarizes the conversation. Generate in Indonesia Language

        **User Question**: {query}
        **AI Response**: {response}

        Return only the title as a string.
        """

        try:
            if provider == LLMProvider.DIGITAL_OCEAN:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {env.DO_API_KEY}",
                }
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 50,
                    "stream": False,
                }
                response = requests.post(
                    f"{env.DO_API_URL}/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"].strip()
            else:  # provider == LLMProvider.OLLAMA
                payload = {
                    "model": env.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                }
                response = requests.post(env.OLLAMA_API_URL, json=payload)
                response.raise_for_status()
                return response.json().get("response", "Untitled Chat").strip()
        except requests.RequestException as e:
            logger.error(f"Error generating title: {e}")
            return "Untitled Chat"

    @classmethod
    def process_query(
        cls,
        query,
        context_limit,
        selected_doc_id,
        llm_provider,
        stream_callback=None,
        debug_mode=False,
    ):

        # Get context from embedding service
        sources, context = EmbeddingService.retrieve_context(
            query, context_limit, selected_doc_id
        )

        # Generate response using LLM
        response = cls.generate_response(
            context, query, llm_provider, stream_callback, debug_mode
        )

        # Generate title
        title = cls.generate_chat_title(query, response, llm_provider)

        # Create chat history entry
        chat = ChatHistory(query=query, response=response, sources=sources, title=title)

        # Save to database
        chat_id = DatabaseService.save_chat_to_db(chat)
        chat.id = chat_id

        # Return response data
        return {
            "id": chat_id,
            "query": query,
            "response": response,
            "sources": sources,
            "title": title,
            "timestamp": chat.timestamp,
        }
