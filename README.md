SportIA1: AI-Driven Fitness Agentic Architecture (V2)
SportIA1 is an advanced fitness ecosystem designed to revolutionize personal training through an Agentic Architecture. By bridging local performance data with high-level cloud reasoning, this project transforms raw workout logs into actionable, data-driven coaching insights.

Project Overview
Developed as a technical solution for automated athletic tracking, SportIA1 utilizes the Model Context Protocol (MCP) to create a seamless interface between a user's local environment and Large Language Models.

Key Features
Automated Workout Registration: Seamlessly logs exercises, weights, sets, and reps into a structured JSON database.

Intelligent Progress Evaluation: Implements a Progressive Overload algorithm to detect plateaus and suggest technical adjustments.

Context-Aware Expert Chat: Leverages GPT-4o via Azure OpenAI to provide coaching based on the user's real-time training history.

Extended Exercise Library: Supports a wide range of movements across chest, back, shoulders, and arms.

Technical Stack
Generative AI Models: GPT-4o (Azure OpenAI / GitHub Models).

Agent Framework: FastMCP (Model Context Protocol).

Python Libraries: openai, mcp, python-dotenv, json.

Infrastucture: Azure AI Foundry / MCP Inspector.

Implementation Details
The solution utilizes a Tool-Augmented LLM approach. By using the @mcp.tool decorator, the AI agent is granted "agency" to perform the following:

Read/Write: Interact with datos_entreno.json for persistent storage.

Analyze: Execute Python logic to evaluate strength trends.

Consult: Perform RAG-lite (Retrieval-Augmented Generation) by injecting local history into the AI's prompt context.