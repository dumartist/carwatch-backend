import os

def initialize_app():
    """Initialize the application directories."""
    # Create required directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('uploads', exist_ok=True) 
    os.makedirs('models', exist_ok=True)
    print("Directories initialized")

if __name__ == "__main__":
    initialize_app()