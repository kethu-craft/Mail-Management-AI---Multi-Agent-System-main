# [file name]: auth.py
# [file content begin]
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
import base64
import hmac
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

class AuthSystem:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.secret_key = os.getenv('JWT_SECRET', 'mail_management_secret_key_2024_change_in_production')
        self.users = self.load_users()
        self.otp_storage = {}  # Store OTPs temporarily
        self.otp_expiry = 300  # 5 minutes
    
    def load_users(self):
        """Load users from JSON file"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception:
            return False
    
    def hash_password(self, password):
        """Hash password with salt using PBKDF2"""
        salt = secrets.token_hex(32)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${hashed.hex()}"

    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        try:
            salt, stored_hash = hashed_password.split('$')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
            return computed_hash == stored_hash
        except Exception:
            return False
    
    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def send_otp_email(self, email, otp):
        """Send OTP to user's email"""
        try:
            # Email configuration from environment
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            email_address = os.getenv('EMAIL_ADDRESS')
            email_password = os.getenv('EMAIL_PASSWORD')
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = email_address
            msg['To'] = email
            msg['Subject'] = "Your OTP for Mail Management AI"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; text-align: center;">Mail Management AI - OTP Verification</h2>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Hello,
                    </p>
                    <p style="color: #666; font-size: 16px; line-height: 1.6;">
                        Your One-Time Password (OTP) for account verification is:
                    </p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="font-size: 32px; font-weight: bold; color: #667eea; letter-spacing: 5px; background-color: #f8f9fa; padding: 15px 25px; border-radius: 8px; display: inline-block;">
                            {otp}
                        </span>
                    </div>
                    <p style="color: #666; font-size: 14px; line-height: 1.6;">
                        This OTP will expire in 5 minutes. Please do not share this code with anyone.
                    </p>
                    <p style="color: #999; font-size: 12px; text-align: center; margin-top: 30px;">
                        If you didn't request this OTP, please ignore this email.
                    </p>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, email, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            print(f"Error sending OTP email: {e}")
            return False
    
    def initiate_registration(self, email):
        """Initiate registration by sending OTP"""
        # Validate email format
        if '@' not in email or '.' not in email:
            return False, "Invalid email format"
        
        # Check if user already exists
        if email in self.users:
            return False, "User already exists"
        
        # Generate and store OTP
        otp = self.generate_otp()
        self.otp_storage[email] = {
            'otp': otp,
            'created_at': datetime.now().timestamp(),
            'verified': False
        }
        
        # Send OTP email
        if self.send_otp_email(email, otp):
            return True, "OTP sent successfully to your email"
        else:
            return False, "Failed to send OTP. Please check your email configuration"
    
    def verify_otp(self, email, otp):
        """Verify OTP for registration"""
        if email not in self.otp_storage:
            return False, "OTP not found or expired"
        
        otp_data = self.otp_storage[email]
        
        # Check if OTP is expired
        if datetime.now().timestamp() - otp_data['created_at'] > self.otp_expiry:
            del self.otp_storage[email]
            return False, "OTP has expired. Please request a new one"
        
        # Verify OTP
        if otp_data['otp'] == otp:
            otp_data['verified'] = True
            return True, "OTP verified successfully"
        else:
            return False, "Invalid OTP"
    
    def complete_registration(self, email, password):
        """Complete registration after OTP verification"""
        if email not in self.otp_storage:
            return False, "Registration not initiated"
        
        if not self.otp_storage[email]['verified']:
            return False, "OTP not verified"
        
        # Validate password strength
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        # Hash password and store user
        hashed_password = self.hash_password(password)
        self.users[email] = {
            'password': hashed_password,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'email_verified': True
        }
        
        # Clean up OTP storage
        del self.otp_storage[email]
        
        if self.save_users():
            return True, "Registration completed successfully"
        else:
            return False, "Registration failed - could not save user data"
    
    def login_user(self, email, password):
        """Authenticate user"""
        if email not in self.users:
            return False, "User not found", None
        
        if not self.verify_password(password, self.users[email]['password']):
            return False, "Invalid password", None
        
        # Update last login
        self.users[email]['last_login'] = datetime.now().isoformat()
        self.save_users()
        
        # Generate simple token
        token = self.generate_simple_token(email)
        return True, "Login successful", token
    
    def generate_simple_token(self, email):
        """Generate a simple token without JWT dependencies"""
        timestamp = str(int(datetime.now().timestamp()))
        data = f"{email}:{timestamp}"
        
        # Create signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        token_data = f"{data}:{signature}"
        return base64.b64encode(token_data.encode('utf-8')).decode('utf-8')
    
    def verify_simple_token(self, token):
        """Verify the simple token"""
        try:
            # Decode token
            token_data = base64.b64decode(token.encode('utf-8')).decode('utf-8')
            email, timestamp, signature = token_data.split(':')
            
            # Verify signature
            expected_data = f"{email}:{timestamp}"
            expected_signature = hmac.new(
                self.secret_key.encode('utf-8'),
                expected_data.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Check signature and token expiration (24 hours)
            if not hmac.compare_digest(signature, expected_signature):
                return None
            
            token_time = datetime.fromtimestamp(int(timestamp))
            if datetime.now() - token_time > timedelta(hours=24):
                return None
                    
            return email
            
        except Exception:
            return None
    
    def verify_token(self, token):
        """Verify token (compatibility method)"""
        return self.verify_simple_token(token)
    
    def user_exists(self, email):
        """Check if user exists"""
        return email in self.users
    
    def get_user_count(self):
        """Get total number of registered users"""
        return len(self.users)
    
    def resend_otp(self, email):
        """Resend OTP to user"""
        return self.initiate_registration(email)

    # NEW: Delete account method
    def delete_account(self, email, password):
        """Delete user account after password verification"""
        if email not in self.users:
            return False, "User not found"
        
        if not self.verify_password(password, self.users[email]['password']):
            return False, "Invalid password"
        
        # Remove user from storage
        del self.users[email]
        
        if self.save_users():
            return True, "Account deleted successfully"
        else:
            return False, "Failed to delete account - could not update data"
# [file content end]