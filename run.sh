#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "No .env file found. Running setup-env.sh to create one..."
    ./setup-env.sh
    
    echo "Please edit the .env file to add your Gemini API key before continuing."
    echo "Press Enter when ready to continue, or Ctrl+C to exit..."
    read
fi

# Check if GOOGLE_API_KEY is set in .env
if ! grep -q "GOOGLE_API_KEY=.*[a-zA-Z0-9]" .env; then
    echo "Warning: GOOGLE_API_KEY doesn't appear to be set in .env"
    echo "Do you want to continue anyway? (y/n)"
    read continue_response
    if [[ ! "$continue_response" =~ ^[Yy]$ ]]; then
        echo "Exiting. Please set your GOOGLE_API_KEY in .env and try again."
        exit 1
    fi
fi

# Ask which action to take
echo ""
echo "Research Feed with Gemini"
echo "========================="
echo "Choose an option:"
echo "1) Test Gemini API connection"
echo "2) Run Gemini examples"
echo "3) Start Research Feed application"
echo "4) Do all of the above"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        # Test Gemini API connection
        echo "Testing Gemini API connection..."
        python test_gemini.py
        ;;
    2)
        # Run Gemini examples
        echo "Running Gemini examples..."
        python gemini_examples.py
        
        echo ""
        echo "To see available models, run: python gemini_examples.py --list-models"
        echo "To use a specific model, run: python gemini_examples.py --model MODEL_NAME"
        ;;
    3)
        # Start the application
        echo "Starting Research Feed application..."
        docker-compose up -d
        
        echo "Checking service health..."
        sleep 5
        
        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            echo "✅ Research Feed is now running!"
            echo "Frontend: http://localhost:3000"
            echo "API: http://localhost:8000"
            echo "API Documentation: http://localhost:8000/docs"
        else
            echo "❌ Some services failed to start. Check docker-compose logs for details:"
            echo "docker-compose logs"
        fi
        ;;
    4)
        # Test Gemini API connection
        echo "Testing Gemini API connection..."
        python test_gemini.py
        test_result=$?
        
        if [ $test_result -ne 0 ]; then
            echo "Gemini API test failed."
            echo "Do you want to continue? (y/n)"
            read continue_response
            if [[ ! "$continue_response" =~ ^[Yy]$ ]]; then
                echo "Exiting. Please check your API key and try again."
                exit 1
            fi
        fi
        
        # Run Gemini examples
        echo "Running Gemini examples..."
        python gemini_examples.py
        
        # Start the application
        echo "Starting Research Feed application..."
        docker-compose up -d
        
        echo "Checking service health..."
        sleep 5
        
        # Check if services are running
        if docker-compose ps | grep -q "Up"; then
            echo "✅ Research Feed is now running!"
            echo "Frontend: http://localhost:3000"
            echo "API: http://localhost:8000"
            echo "API Documentation: http://localhost:8000/docs"
        else
            echo "❌ Some services failed to start. Check docker-compose logs for details:"
            echo "docker-compose logs"
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac 