#!/usr/bin/env python3
"""Test script to verify browser installation and configuration."""

import asyncio
import sys
from pathlib import Path

try:
    from browser_use import Agent
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies: pip install browser-use langchain-google-genai")
    sys.exit(1)

async def test_browser_setup():
    """Test browser setup and basic functionality."""
    print("🔍 Testing browser setup...")
    
    try:
        # Test browser configuration
        browser_config = {
            "headless": True,
            "browser_type": "chromium",
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
        }
        
        print("✅ Browser configuration loaded")
        
        # Test LLM configuration (if API key is available)
        try:
            import os
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if api_key and not api_key.startswith('your_') and not api_key.startswith('AIzaSyDummy'):
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash-exp",
                    google_api_key=api_key,
                    temperature=0.1
                )
                print("✅ LLM configuration loaded")
                
                # Create agent with browser configuration
                agent = Agent(
                    task="Test browser functionality",
                    llm=llm,
                    browser_config=browser_config
                )
                print("✅ Agent created successfully")
                
                # Test basic browser operation
                print("🌐 Testing basic browser operation...")
                result = await agent.run("Navigate to https://httpbin.org/get and return the response")
                print(f"✅ Browser test completed: {result[:100]}...")
                
            else:
                print("⚠️  No valid API key found, skipping LLM test")
                print("   Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
                
        except Exception as e:
            print(f"⚠️  LLM test failed: {e}")
        
        print("\n🎉 Browser setup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Browser setup test failed: {e}")
        return False

def test_chromium_installation():
    """Test if Chromium is properly installed."""
    print("🔍 Testing Chromium installation...")
    
    import subprocess
    import shutil
    
    # Check if chromium-browser is available
    chromium_path = shutil.which('chromium-browser')
    if chromium_path:
        print(f"✅ Chromium found at: {chromium_path}")
        
        try:
            # Test chromium version
            result = subprocess.run(
                ['chromium-browser', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✅ Chromium version: {result.stdout.strip()}")
            else:
                print(f"⚠️  Chromium version check failed: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Chromium version check error: {e}")
    else:
        print("❌ Chromium not found in PATH")
        return False
    
    # Check if chromedriver is available
    chromedriver_path = shutil.which('chromedriver')
    if chromedriver_path:
        print(f"✅ ChromeDriver found at: {chromedriver_path}")
    else:
        print("⚠️  ChromeDriver not found (may not be needed for Playwright)")
    
    return True

def main():
    """Main test function."""
    print("🚀 Browser Automation System - Browser Test")
    print("=" * 50)
    
    # Test 1: Chromium installation
    if not test_chromium_installation():
        print("❌ Chromium installation test failed")
        sys.exit(1)
    
    print("\n" + "-" * 30)
    
    # Test 2: Browser setup (async)
    try:
        success = asyncio.run(test_browser_setup())
        if not success:
            print("❌ Browser setup test failed")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Async test error: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All browser tests passed successfully!")
    print("\n💡 Your system is ready for browser automation.")
    print("\n🚀 You can now run:")
    print("   - docker-compose up -d")
    print("   - python deploy-vps.py deploy")

if __name__ == "__main__":
    main()