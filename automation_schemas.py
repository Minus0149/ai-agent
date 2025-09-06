"""Structured output schemas for browser automation tasks."""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class ActionType(str, Enum):
    """Types of browser actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    INPUT_TEXT = "input_text"
    EXTRACT_DATA = "extract_data"
    WAIT = "wait"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    DOWNLOAD = "download"
    UPLOAD = "upload"

class DataExtractionSchema(BaseModel):
    """Schema for data extraction results."""
    url: str = Field(description="URL where data was extracted")
    timestamp: datetime = Field(description="When the data was extracted")
    data: Dict[str, Any] = Field(description="Extracted data")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class LoginResult(BaseModel):
    """Schema for login automation results."""
    success: bool = Field(description="Whether login was successful")
    username: Optional[str] = Field(default=None, description="Username used for login")
    email: Optional[str] = Field(default=None, description="Email used for login")
    temp_email: Optional[str] = Field(default=None, description="Temporary email if used")
    login_url: str = Field(description="URL where login was performed")
    error_message: Optional[str] = Field(default=None, description="Error message if login failed")
    additional_steps_required: Optional[List[str]] = Field(default=None, description="Additional steps needed")

class FormFillResult(BaseModel):
    """Schema for form filling results."""
    form_url: str = Field(description="URL of the form")
    fields_filled: List[str] = Field(description="List of field names that were filled")
    submission_successful: bool = Field(description="Whether form submission was successful")
    confirmation_message: Optional[str] = Field(default=None, description="Confirmation message received")
    errors: Optional[List[str]] = Field(default=None, description="Any errors encountered")

class SearchResult(BaseModel):
    """Schema for search operation results."""
    query: str = Field(description="Search query used")
    search_engine: str = Field(description="Search engine or site used")
    results_count: int = Field(description="Number of results found")
    top_results: List[Dict[str, str]] = Field(description="Top search results with title and URL")
    extracted_info: Optional[Dict[str, Any]] = Field(default=None, description="Specific information extracted")

class EcommerceActionResult(BaseModel):
    """Schema for e-commerce related actions."""
    action_type: str = Field(description="Type of e-commerce action performed")
    product_info: Optional[Dict[str, Any]] = Field(default=None, description="Product information")
    cart_items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Items in cart")
    total_price: Optional[float] = Field(default=None, description="Total price")
    order_id: Optional[str] = Field(default=None, description="Order ID if purchase completed")
    success: bool = Field(description="Whether the action was successful")

class SocialMediaResult(BaseModel):
    """Schema for social media automation results."""
    platform: str = Field(description="Social media platform")
    action: str = Field(description="Action performed (post, like, follow, etc.)")
    content: Optional[str] = Field(default=None, description="Content posted or interacted with")
    engagement_metrics: Optional[Dict[str, int]] = Field(default=None, description="Likes, shares, comments, etc.")
    success: bool = Field(description="Whether the action was successful")

class WebScrapingResult(BaseModel):
    """Schema for web scraping results."""
    target_url: str = Field(description="URL that was scraped")
    data_points: int = Field(description="Number of data points extracted")
    structured_data: Dict[str, Any] = Field(description="Scraped data in structured format")
    pagination_info: Optional[Dict[str, Any]] = Field(default=None, description="Pagination details if applicable")
    scraping_duration: float = Field(description="Time taken to scrape in seconds")

class FileOperationResult(BaseModel):
    """Schema for file operation results."""
    operation: str = Field(description="Type of file operation (download, upload, read)")
    file_path: str = Field(description="Path to the file")
    file_size: Optional[int] = Field(default=None, description="File size in bytes")
    file_type: Optional[str] = Field(default=None, description="File type/extension")
    success: bool = Field(description="Whether the operation was successful")
    error_message: Optional[str] = Field(default=None, description="Error message if operation failed")

class NavigationResult(BaseModel):
    """Schema for navigation results."""
    start_url: str = Field(description="Starting URL")
    end_url: str = Field(description="Final URL reached")
    pages_visited: List[str] = Field(description="List of URLs visited during navigation")
    navigation_time: float = Field(description="Total navigation time in seconds")
    success: bool = Field(description="Whether navigation was successful")

class ComprehensiveAutomationResult(BaseModel):
    """Comprehensive schema that can handle multiple types of automation results."""
    task_type: str = Field(description="Type of automation task performed")
    success: bool = Field(description="Overall success of the task")
    duration: float = Field(description="Task duration in seconds")
    
    # Optional specific results based on task type
    login_result: Optional[LoginResult] = None
    form_result: Optional[FormFillResult] = None
    search_result: Optional[SearchResult] = None
    ecommerce_result: Optional[EcommerceActionResult] = None
    social_media_result: Optional[SocialMediaResult] = None
    scraping_result: Optional[WebScrapingResult] = None
    file_result: Optional[FileOperationResult] = None
    navigation_result: Optional[NavigationResult] = None
    
    # General fields
    extracted_data: Optional[Dict[str, Any]] = Field(default=None, description="Any additional extracted data")
    screenshots: Optional[List[str]] = Field(default=None, description="Paths to screenshots taken")
    errors: Optional[List[str]] = Field(default=None, description="Any errors encountered")
    recommendations: Optional[List[str]] = Field(default=None, description="Recommendations for improvement")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Predefined schemas for common automation tasks
COMMON_SCHEMAS = {
    "login_automation": LoginResult.model_json_schema(),
    "form_filling": FormFillResult.model_json_schema(),
    "web_search": SearchResult.model_json_schema(),
    "ecommerce_automation": EcommerceActionResult.model_json_schema(),
    "social_media_automation": SocialMediaResult.model_json_schema(),
    "web_scraping": WebScrapingResult.model_json_schema(),
    "file_operations": FileOperationResult.model_json_schema(),
    "navigation_task": NavigationResult.model_json_schema(),
    "comprehensive_automation": ComprehensiveAutomationResult.model_json_schema(),
    "data_extraction": DataExtractionSchema.model_json_schema()
}

def get_schema_for_task(task_description: str) -> Optional[Dict[str, Any]]:
    """Automatically select appropriate schema based on task description."""
    task_lower = task_description.lower()
    
    # Login related keywords
    if any(keyword in task_lower for keyword in ['login', 'sign in', 'authenticate', 'temp mail', 'temporary email']):
        return COMMON_SCHEMAS["login_automation"]
    
    # Form filling keywords
    elif any(keyword in task_lower for keyword in ['form', 'fill', 'submit', 'register', 'signup']):
        return COMMON_SCHEMAS["form_filling"]
    
    # Search related keywords
    elif any(keyword in task_lower for keyword in ['search', 'find', 'look for', 'google', 'bing']):
        return COMMON_SCHEMAS["web_search"]
    
    # E-commerce keywords
    elif any(keyword in task_lower for keyword in ['buy', 'purchase', 'cart', 'checkout', 'product', 'shop']):
        return COMMON_SCHEMAS["ecommerce_automation"]
    
    # Social media keywords
    elif any(keyword in task_lower for keyword in ['post', 'tweet', 'facebook', 'instagram', 'linkedin', 'social']):
        return COMMON_SCHEMAS["social_media_automation"]
    
    # Web scraping keywords
    elif any(keyword in task_lower for keyword in ['scrape', 'extract', 'collect data', 'harvest']):
        return COMMON_SCHEMAS["web_scraping"]
    
    # File operations keywords
    elif any(keyword in task_lower for keyword in ['download', 'upload', 'file', 'document', 'pdf']):
        return COMMON_SCHEMAS["file_operations"]
    
    # Navigation keywords
    elif any(keyword in task_lower for keyword in ['navigate', 'go to', 'visit', 'browse']):
        return COMMON_SCHEMAS["navigation_task"]
    
    # Default to comprehensive schema for complex tasks
    else:
        return COMMON_SCHEMAS["comprehensive_automation"]

def create_custom_schema(fields: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Create a custom schema dynamically.
    
    Args:
        fields: Dictionary where keys are field names and values are field definitions
                Example: {
                    "product_name": {"type": "string", "description": "Name of the product"},
                    "price": {"type": "number", "description": "Product price"}
                }
    """
    properties = {}
    required = []
    
    for field_name, field_def in fields.items():
        properties[field_name] = {
            "type": field_def.get("type", "string"),
            "description": field_def.get("description", "")
        }
        
        if field_def.get("required", False):
            required.append(field_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }