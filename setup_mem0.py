"""
Quick Setup Script for Mem0 Integration
This script helps set up and test the Mem0 integration.
"""

import os
import sys


def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = ["CLUSTER_URL", "AUTH_CLIENT_SECRET", "GOOGLE_API_KEY"]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file")
        return False

    print("✅ All environment variables are set")
    return True


def test_mem0_connection():
    """Test connection to Mem0/Weaviate."""
    try:
        from mem0_config import memory_agent

        print("✅ Mem0 configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to load Mem0 configuration: {str(e)}")
        return False


def test_mem0_service():
    """Test the Mem0 service."""
    try:
        sys.path.append("language-learning-platform")
        from app.services.mem0_service import mem0_service

        print("✅ Mem0 service imported successfully")

        # Test basic functionality
        test_user_id = 99999  # Test user ID

        # Add a test memory
        result = mem0_service.add_user_interaction(
            user_id=test_user_id,
            message="This is a test memory for setup verification",
            context={"type": "setup_test"},
        )

        if result.get("success"):
            print("✅ Successfully added test memory")
        else:
            print(f"⚠️  Warning: {result.get('message')}")

        # Retrieve memories
        memories = mem0_service.get_user_memories(test_user_id, limit=1)
        if memories:
            print(f"✅ Successfully retrieved {len(memories)} test memory(ies)")
        else:
            print("⚠️  No memories retrieved (this might be normal for first run)")

        return True

    except Exception as e:
        print(f"❌ Failed to test Mem0 service: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


def create_example_env_file():
    """Create an example .env file."""
    env_example = """# Mem0 Configuration
# Weaviate Vector Database
CLUSTER_URL=https://your-cluster-url.weaviate.network
AUTH_CLIENT_SECRET=your_weaviate_auth_secret

# Google AI API
GOOGLE_API_KEY=your_google_ai_api_key

# Database (if not already set)
DATABASE_URL=sqlite:///telugu_english_learning.db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
"""

    if not os.path.exists(".env"):
        with open(".env.example", "w") as f:
            f.write(env_example)
        print("✅ Created .env.example file")
        print("   Please copy it to .env and fill in your credentials")
    else:
        print("ℹ️  .env file already exists")


def main():
    """Main setup function."""
    print("=" * 60)
    print("Mem0 Integration Setup")
    print("=" * 60)
    print()

    # Step 1: Create example env file
    print("Step 1: Checking environment file...")
    create_example_env_file()
    print()

    # Step 2: Check environment variables
    print("Step 2: Checking environment variables...")
    if not check_environment_variables():
        print("\n⚠️  Setup incomplete. Please set environment variables and run again.")
        return
    print()

    # Step 3: Test Mem0 connection
    print("Step 3: Testing Mem0 connection...")
    if not test_mem0_connection():
        print("\n⚠️  Setup incomplete. Please check your Mem0 configuration.")
        return
    print()

    # Step 4: Test Mem0 service
    print("Step 4: Testing Mem0 service...")
    if not test_mem0_service():
        print("\n⚠️  Setup incomplete. Please check the error messages above.")
        return
    print()

    print("=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start your Flask application")
    print("2. Test the new endpoints:")
    print("   - GET /api/chat/user-memories")
    print("   - POST /api/chat/search-memories")
    print("   - GET /api/chat/personalized-suggestions")
    print("   - GET /api/chat/user-learning-context")
    print()
    print("3. See MEM0_INTEGRATION_GUIDE.md for detailed usage")
    print()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    main()
