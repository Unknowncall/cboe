#!/bin/bash

# Install LangChain dependencies for the trail search server
echo "Installing LangChain dependencies..."

cd server

# Install the new requirements
pip install langchain>=0.1.0 langchain-openai>=0.1.0 langchain-community>=0.1.0

echo "LangChain dependencies installed successfully!"
echo ""
echo "Available agents:"
echo "- custom: Direct OpenAI API implementation (default)"
echo "- langchain: LangChain framework-based agent with memory"
echo ""
echo "You can now select between agents in the frontend UI."
