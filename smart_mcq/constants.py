# Smart MCQ Platform - Global Constants
# This file contains all standardized constants to prevent inconsistencies and magic numbers

from django.utils.translation import gettext_lazy as _

# ============================================================================
# DATE/TIME FORMAT CONSTANTS
# ============================================================================

class DateTimeFormats:
    """Standard date/time formats for consistent use across templates and JavaScript"""
    
    # Django Template Filters
    DISPLAY_DATETIME = "M d, Y g:i A"  # "Jan 15, 2024 2:30 PM" - User-friendly display
    DISPLAY_DATE = "M d, Y"           # "Jan 15, 2024" - Date only display
    DATABASE_DATETIME = "Y-m-d H:i:s" # "2024-01-15 14:30:00" - Database format
    ISO_8601 = "c"                    # ISO 8601 format for JavaScript consumption
    
    # JavaScript Compatible Formats
    JS_COMPATIBLE = ISO_8601          # Always use ISO 8601 for JavaScript parsing
    
    # Form Input Formats
    FORM_DATETIME_LOCAL = "Y-m-d\TH:i" # HTML datetime-local input format


# ============================================================================
# ACCESS CODE CONSTANTS
# ============================================================================

class AccessCode:
    """Constants for test session access codes"""
    
    LENGTH = 6                        # Access code length (e.g., "ABC123")
    MAX_LENGTH = 6                    # Database field max_length
    ALLOWED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # Valid characters
    

# ============================================================================
# MULTIPLE CHOICE CONSTANTS
# ============================================================================

class MultipleChoice:
    """Constants for multiple choice questions"""
    
    # Choice Labels
    CHOICE_A = 'A'
    CHOICE_B = 'B'
    CHOICE_C = 'C'
    CHOICE_D = 'D'
    
    # Choice Configuration
    VALID_CHOICES = [CHOICE_A, CHOICE_B, CHOICE_C, CHOICE_D]
    CHOICE_LABELS = [
        (CHOICE_A, CHOICE_A),
        (CHOICE_B, CHOICE_B),
        (CHOICE_C, CHOICE_C),
        (CHOICE_D, CHOICE_D),
    ]
    
    NUMBER_OF_CHOICES = 4             # Fixed number of choices per question
    MIN_CHOICES = 4                   # Minimum required choices
    MAX_CHOICES = 4                   # Maximum allowed choices
    
    # Field Lengths
    CHOICE_LABEL_MAX_LENGTH = 1       # Single character for choice labels


# ============================================================================
# USER ROLE CONSTANTS
# ============================================================================

class UserRoles:
    """Constants for user roles and permissions"""
    
    # Role Values
    STUDENT = 'student'
    TEACHER = 'teacher'
    
    # Role Choices for Django fields
    ROLE_CHOICES = [
        (STUDENT, _('Student')),
        (TEACHER, _('Teacher')),
    ]
    
    # Group Names (Django Groups)
    GROUP_STUDENTS = 'Students'
    GROUP_TEACHERS = 'Teachers'
    
    # Field Configuration
    ROLE_MAX_LENGTH = 10


# ============================================================================
# FIELD LENGTH CONSTANTS
# ============================================================================

class FieldLengths:
    """Standard field lengths for consistent database schema"""
    
    # Organization
    ORGANIZATION_NAME_MAX_LENGTH = 200
    
    # Questions
    QUESTION_TITLE_MAX_LENGTH = 500
    QUESTION_CATEGORY_MAX_LENGTH = 100
    QUESTION_DIFFICULTY_MAX_LENGTH = 10
    QUESTION_TITLE_TRUNCATE_LENGTH = 100
    CHOICE_TEXT_TRUNCATE_LENGTH = 50
    
    # Tests
    TEST_TITLE_MAX_LENGTH = 200
    TEST_CATEGORY_MAX_LENGTH = 100
    
    # General
    CATEGORY_MAX_LENGTH = 100
    SHORT_TEXT_MAX_LENGTH = 100
    MEDIUM_TEXT_MAX_LENGTH = 200
    LONG_TEXT_MAX_LENGTH = 500


# ============================================================================
# DIFFICULTY LEVEL CONSTANTS
# ============================================================================

class DifficultyLevels:
    """Constants for question difficulty levels"""
    
    # Difficulty Values
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    
    # Difficulty Choices for Django fields
    DIFFICULTY_CHOICES = [
        (EASY, _('Easy')),
        (MEDIUM, _('Medium')),
        (HARD, _('Hard')),
    ]
    
    # Default Values
    DEFAULT_DIFFICULTY = MEDIUM


# ============================================================================
# TEST SESSION STATUS CONSTANTS
# ============================================================================

class SessionStatus:
    """Constants for test session status values"""
    
    # Status Values
    UPCOMING = 'upcoming'
    ACTIVE = 'active'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    UNKNOWN = 'unknown'
    
    # Status Display Names
    STATUS_DISPLAY = {
        UPCOMING: _('Upcoming'),
        ACTIVE: _('Active'),
        EXPIRED: _('Expired'),
        CANCELLED: _('Cancelled'),
        UNKNOWN: _('Unknown'),
    }


# ============================================================================
# DEFAULT VALUES
# ============================================================================

class Defaults:
    """Default values for various fields and configurations"""
    
    # Test Configuration
    TIME_LIMIT_MINUTES = 60           # Default test duration
    
    # Progress Tracking
    QUESTION_INDEX = 0                # Starting question index (0-based)
    TIME_SPENT = 0                    # Default time spent in seconds
    PROGRESS_DEFAULT_VALUE = 0        # Default progress when no questions
    PROGRESS_PERCENTAGE_MULTIPLIER = 100
    
    # Organization
    ORGANIZATION_NAME = 'Default Organization'
    
    # Navigation
    QUESTION_NUMBER_DISPLAY_OFFSET = 1  # Convert 0-based index to 1-based display
    QUESTION_INDEX_INCREMENT = 1
    QUESTION_INDEX_DECREMENT = 1
    LAST_QUESTION_INDEX_OFFSET = 1


# ============================================================================
# SYSTEM CONFIGURATION CONSTANTS
# ============================================================================

class SystemConfig:
    """System-level configuration constants"""
    
    # Database
    DEFAULT_DB_PORT = '5433'
    
    # Startup Configuration
    POSTGRES_WAIT_ATTEMPTS = 15       # Max attempts to wait for PostgreSQL
    POSTGRES_WAIT_INTERVAL = 1        # Seconds between PostgreSQL checks
    
    # Timer Configuration (JavaScript)
    TIMER_UPDATE_INTERVAL = 1000      # Milliseconds (1 second)
    WARNING_5_MINUTES = 300000        # 5 minutes in milliseconds
    WARNING_1_MINUTE = 60000          # 1 minute in milliseconds
    AUTO_REFRESH_DELAY = 3000         # 3 seconds for status updates


# ============================================================================
# VALIDATION CONSTANTS
# ============================================================================

class Validation:
    """Constants for validation rules"""
    
    # Access Code Validation
    ACCESS_CODE_ALPHANUMERIC_PATTERN = r'^[A-Z0-9]{6}$'
    
    # Password Requirements (for future use)
    MIN_PASSWORD_LENGTH = 8
    
    # File Upload Limits (for question images)
    MAX_IMAGE_SIZE_MB = 5
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024


# ============================================================================
# URL NAMESPACES
# ============================================================================

class URLNamespaces:
    """Constants for URL namespaces used in reversing URLs"""
    
    ACCOUNTS = 'accounts'
    QUESTIONS = 'questions'
    TESTS = 'tests'
    TEST_SESSIONS = 'test_sessions'


# ============================================================================
# CACHE KEYS (for future Redis implementation)
# ============================================================================

class CacheKeys:
    """Constants for cache key prefixes and patterns"""
    
    USER_PROFILE = 'user_profile_{user_id}'
    TEST_SESSION = 'test_session_{session_id}'
    QUESTION_SET = 'question_set_{test_id}'
    ACTIVE_SESSIONS = 'active_sessions'
    USER_ATTEMPTS = 'user_attempts_{user_id}'


# ============================================================================
# PERMISSION CONSTANTS
# ============================================================================

class Permissions:
    """Constants for permission names and groups"""
    
    # Custom Permissions
    CAN_CREATE_QUESTIONS = 'can_create_questions'
    CAN_CREATE_TESTS = 'can_create_tests'
    CAN_MANAGE_SESSIONS = 'can_manage_sessions'
    CAN_VIEW_RESULTS = 'can_view_results'
    
    # Permission Groups
    TEACHER_PERMISSIONS = [
        CAN_CREATE_QUESTIONS,
        CAN_CREATE_TESTS,
        CAN_MANAGE_SESSIONS,
        CAN_VIEW_RESULTS,
    ]


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Standardized error messages for consistent user experience"""
    
    # Authentication
    INVALID_CREDENTIALS = _('Invalid username or password.')
    ACCESS_DENIED = _('Access denied. You do not have permission to perform this action.')
    
    # Access Codes
    INVALID_ACCESS_CODE = _('Invalid access code. Please check and try again.')
    ACCESS_CODE_REQUIRED = _('Please enter an access code.')
    ACCESS_CODE_FORMAT = _('Access code must be 6 alphanumeric characters.')
    
    # Test Sessions
    SESSION_NOT_FOUND = _('Test session not found.')
    SESSION_EXPIRED = _('This test session has expired and is no longer available.')
    SESSION_NOT_STARTED = _('Test has not started yet. Please join at the scheduled time.')
    ALREADY_JOINED = _('You have already joined this test. Each test can only be joined once.')
    
    # Tests and Questions
    TEST_NOT_FOUND = _('Test not found.')
    QUESTION_NOT_FOUND = _('Question not found.')
    NO_QUESTIONS_AVAILABLE = _('No questions found for this test.')
    
    # Form Validation
    REQUIRED_FIELD = _('This field is required.')
    INVALID_CHOICE = _('Please select a valid choice.')


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Standardized success messages for consistent user experience"""
    
    # Account Management
    ACCOUNT_CREATED = _('Account created successfully.')
    LOGIN_SUCCESSFUL = _('Welcome back!')
    LOGOUT_SUCCESSFUL = _('You have been logged out successfully.')
    
    # CRUD Operations
    CREATED_SUCCESSFULLY = _('Created successfully.')
    UPDATED_SUCCESSFULLY = _('Updated successfully.')
    DELETED_SUCCESSFULLY = _('Deleted successfully.')
    
    # Test Operations
    TEST_JOINED = _('Successfully joined the test session.')
    ANSWER_SAVED = _('Answer saved successfully.')
    TEST_SUBMITTED = _('Test submitted successfully.')