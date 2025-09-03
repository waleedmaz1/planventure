import bcrypt
import secrets
import string
import re
from werkzeug.security import generate_password_hash, check_password_hash

class PasswordUtils:
    """Utility class for password hashing, validation, and generation"""
    
    # Password complexity requirements
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @staticmethod
    def generate_salt(rounds=12):
        """
        Generate a bcrypt salt with specified rounds
        
        Args:
            rounds (int): Number of rounds for bcrypt (default: 12)
            
        Returns:
            bytes: Generated salt
        """
        return bcrypt.gensalt(rounds=rounds)
    
    @staticmethod
    def hash_password_bcrypt(password, salt=None):
        """
        Hash password using bcrypt with optional custom salt
        
        Args:
            password (str): Plain text password
            salt (bytes, optional): Custom salt (generates new if None)
            
        Returns:
            str: Hashed password
        """
        if isinstance(password, str):
            password = password.encode('utf-8')
        
        if salt is None:
            salt = PasswordUtils.generate_salt()
        
        hashed = bcrypt.hashpw(password, salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def hash_password_werkzeug(password, method='pbkdf2:sha256', salt_length=16):
        """
        Hash password using Werkzeug's security functions
        
        Args:
            password (str): Plain text password
            method (str): Hash method (default: pbkdf2:sha256)
            salt_length (int): Salt length (default: 16)
            
        Returns:
            str: Hashed password
        """
        return generate_password_hash(
            password, 
            method=method, 
            salt_length=salt_length
        )
    
    @staticmethod
    def verify_password_bcrypt(password, hashed_password):
        """
        Verify password against bcrypt hash
        
        Args:
            password (str): Plain text password
            hashed_password (str): Hashed password
            
        Returns:
            bool: True if password matches
        """
        if isinstance(password, str):
            password = password.encode('utf-8')
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        
        return bcrypt.checkpw(password, hashed_password)
    
    @staticmethod
    def verify_password_werkzeug(password, hashed_password):
        """
        Verify password against Werkzeug hash
        
        Args:
            password (str): Plain text password
            hashed_password (str): Hashed password
            
        Returns:
            bool: True if password matches
        """
        return check_password_hash(hashed_password, password)
    
    @staticmethod
    def validate_password_strength(password):
        """
        Validate password strength based on requirements
        
        Args:
            password (str): Password to validate
            
        Returns:
            dict: Validation result with status and errors
        """
        errors = []
        
        # Length check
        if len(password) < PasswordUtils.MIN_LENGTH:
            errors.append(f"Password must be at least {PasswordUtils.MIN_LENGTH} characters long")
        
        if len(password) > PasswordUtils.MAX_LENGTH:
            errors.append(f"Password must not exceed {PasswordUtils.MAX_LENGTH} characters")
        
        # Character requirements
        if PasswordUtils.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if PasswordUtils.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if PasswordUtils.REQUIRE_DIGITS and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if PasswordUtils.REQUIRE_SPECIAL and not re.search(f'[{re.escape(PasswordUtils.SPECIAL_CHARS)}]', password):
            errors.append(f"Password must contain at least one special character ({PasswordUtils.SPECIAL_CHARS})")
        
        # Common password patterns
        if password.lower() in ['password', '123456', 'admin', 'user', 'test']:
            errors.append("Password is too common")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': PasswordUtils._calculate_strength_score(password)
        }
    
    @staticmethod
    def _calculate_strength_score(password):
        """
        Calculate password strength score (0-100)
        
        Args:
            password (str): Password to score
            
        Returns:
            int: Strength score
        """
        score = 0
        
        # Length bonus
        score += min(len(password) * 4, 25)
        
        # Character variety bonus
        if re.search(r'[a-z]', password):
            score += 5
        if re.search(r'[A-Z]', password):
            score += 5
        if re.search(r'\d', password):
            score += 5
        if re.search(f'[{re.escape(PasswordUtils.SPECIAL_CHARS)}]', password):
            score += 10
        
        # Complexity bonus
        char_types = sum([
            bool(re.search(r'[a-z]', password)),
            bool(re.search(r'[A-Z]', password)),
            bool(re.search(r'\d', password)),
            bool(re.search(f'[{re.escape(PasswordUtils.SPECIAL_CHARS)}]', password))
        ])
        score += char_types * 10
        
        # Penalize repetitive patterns
        if len(set(password)) < len(password) * 0.5:
            score -= 20
        
        return max(0, min(100, score))
    
    @staticmethod
    def generate_secure_password(length=12, include_symbols=True):
        """
        Generate a secure random password
        
        Args:
            length (int): Password length (default: 12)
            include_symbols (bool): Include special characters (default: True)
            
        Returns:
            str: Generated password
        """
        if length < PasswordUtils.MIN_LENGTH:
            length = PasswordUtils.MIN_LENGTH
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = PasswordUtils.SPECIAL_CHARS if include_symbols else ""
        
        # Ensure at least one character from each required set
        password_chars = []
        if PasswordUtils.REQUIRE_LOWERCASE:
            password_chars.append(secrets.choice(lowercase))
        if PasswordUtils.REQUIRE_UPPERCASE:
            password_chars.append(secrets.choice(uppercase))
        if PasswordUtils.REQUIRE_DIGITS:
            password_chars.append(secrets.choice(digits))
        if PasswordUtils.REQUIRE_SPECIAL and include_symbols:
            password_chars.append(secrets.choice(symbols))
        
        # Fill remaining length with random characters
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - len(password_chars)):
            password_chars.append(secrets.choice(all_chars))
        
        # Shuffle the characters
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)
    
    @staticmethod
    def generate_reset_token(length=32):
        """
        Generate a secure token for password reset
        
        Args:
            length (int): Token length (default: 32)
            
        Returns:
            str: Generated token
        """
        return secrets.token_urlsafe(length)
