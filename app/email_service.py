import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


class EmailService:
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
    
    def send_verification_email(self, email: str, verification_token: str, base_url: str) -> bool:
        """Send verification email to user"""
        if not all([self.smtp_server, self.smtp_port, self.smtp_username, self.smtp_password]):
            # In development, just log the verification token
            print(f"Verification token for {email}: {verification_token}")
            return True
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = email
            msg['Subject'] = "Email Verification - File Sharing System"
            
            # Create verification link
            verification_link = f"{base_url}/verify-email?email={email}&token={verification_token}"
            
            # Email body
            body = f"""
            Hello!
            
            Thank you for signing up to our File Sharing System.
            Please click the link below to verify your email address:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.
            
            Best regards,
            File Sharing System Team
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            text = msg.as_string()
            server.sendmail(self.smtp_username, email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False


email_service = EmailService()
