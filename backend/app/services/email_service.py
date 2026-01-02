"""
Email Service

Generic email service for sending emails via SMTP.
Supports HTML and plain text emails with configurable recipients, CC, BCC.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Union
from app.core.config import settings
from app.core.logging_config import get_logger
import traceback

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails via SMTP"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from_email = settings.SMTP_FROM_EMAIL
        self.smtp_from_name = settings.SMTP_FROM_NAME
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.smtp_use_ssl = settings.SMTP_USE_SSL
        self.smtp_timeout = settings.SMTP_TIMEOUT
    
    def _parse_recipients(self, recipients: Union[str, List[str]]) -> List[str]:
        """Parse recipients string (comma-separated) or list into list"""
        if isinstance(recipients, str):
            return [email.strip() for email in recipients.split(",") if email.strip()]
        return recipients if isinstance(recipients, list) else []
    
    def _create_message(
        self,
        subject: str,
        body: str,
        recipients: Union[str, List[str]],
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        html: bool = False,
        attachments: Optional[List[dict]] = None
    ) -> MIMEMultipart:
        """Create email message"""
        msg = MIMEMultipart('alternative' if html else 'related')
        msg['From'] = f"{self.smtp_from_name} <{self.smtp_from_email}>"
        msg['Subject'] = subject
        
        # Parse recipients
        to_list = self._parse_recipients(recipients)
        msg['To'] = ", ".join(to_list)
        
        if cc:
            cc_list = self._parse_recipients(cc)
            if cc_list:
                msg['Cc'] = ", ".join(cc_list)
                to_list.extend(cc_list)
        
        if bcc:
            bcc_list = self._parse_recipients(bcc)
            if bcc_list:
                to_list.extend(bcc_list)
        
        # Add body
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Add attachments if any
        if attachments:
            for attachment in attachments:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.get('content', b''))
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {attachment.get("filename", "attachment")}'
                )
                msg.attach(part)
        
        return msg, to_list
    
    def send_email(
        self,
        subject: str,
        body: str,
        recipients: Union[str, List[str]],
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        html: bool = False,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            subject: Email subject
            body: Email body (plain text or HTML)
            recipients: Recipient email(s) - string (comma-separated) or list
            cc: CC recipient(s) - string (comma-separated) or list (optional)
            bcc: BCC recipient(s) - string (comma-separated) or list (optional)
            html: Whether body is HTML (default: False)
            attachments: List of attachment dicts with 'filename' and 'content' keys (optional)
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.smtp_host or not self.smtp_user:
            logger.warning("SMTP not configured. Email not sent.")
            return False
        
        try:
            # Create message
            msg, to_list = self._create_message(
                subject=subject,
                body=body,
                recipients=recipients,
                cc=cc,
                bcc=bcc,
                html=html,
                attachments=attachments
            )
            
            # Connect to SMTP server
            if self.smtp_use_ssl:
                server = smtplib.SMTP_SSL(
                    self.smtp_host,
                    self.smtp_port,
                    timeout=self.smtp_timeout
                )
            else:
                server = smtplib.SMTP(
                    self.smtp_host,
                    self.smtp_port,
                    timeout=self.smtp_timeout
                )
            
            # Enable TLS if needed
            if self.smtp_use_tls and not self.smtp_use_ssl:
                server.starttls()
            
            # Login if credentials provided
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            
            # Send email
            server.send_message(msg, to_addrs=to_list)
            server.quit()
            
            logger.info(f"Email sent successfully to {len(to_list)} recipient(s)")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}", exc_info=True, extra={"traceback": traceback.format_exc()})
            return False
    
    def send_html_email(
        self,
        subject: str,
        html_body: str,
        recipients: Union[str, List[str]],
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """Send HTML email (convenience method)"""
        return self.send_email(
            subject=subject,
            body=html_body,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            html=True,
            attachments=attachments
        )
    
    def send_plain_email(
        self,
        subject: str,
        text_body: str,
        recipients: Union[str, List[str]],
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """Send plain text email (convenience method)"""
        return self.send_email(
            subject=subject,
            body=text_body,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            html=False,
            attachments=attachments
        )
    
    def send_email_with_defaults(
        self,
        subject: str,
        body: str,
        recipients: Optional[Union[str, List[str]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        html: bool = False,
        attachments: Optional[List[dict]] = None,
        use_env_defaults: bool = True
    ) -> bool:
        """
        Send email with default recipients from environment (debug mode) or custom recipients (production)
        
        Args:
            subject: Email subject
            body: Email body (plain text or HTML)
            recipients: Custom recipient email(s) - string (comma-separated) or list (optional)
                       If None and use_env_defaults=True, uses EMAIL_ADMIN_RECIPIENTS from env
            cc: CC recipient(s) - string (comma-separated) or list (optional)
                If None and use_env_defaults=True, uses EMAIL_ADMIN_CC from env
            bcc: BCC recipient(s) - string (comma-separated) or list (optional)
                 If None and use_env_defaults=True, uses EMAIL_ADMIN_BCC from env
            html: Whether body is HTML (default: False)
            attachments: List of attachment dicts with 'filename' and 'content' keys (optional)
            use_env_defaults: If True (debug mode), use environment defaults when recipients not provided.
                             If False (production), require explicit recipients.
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        # Determine recipients based on mode
        if use_env_defaults and settings.DEBUG_MODE:
            # Debug mode: Use environment defaults if recipients not provided
            final_recipients = recipients if recipients else settings.EMAIL_ADMIN_RECIPIENTS
            final_cc = cc if cc is not None else (settings.EMAIL_ADMIN_CC if settings.EMAIL_ADMIN_CC else None)
            final_bcc = bcc if bcc is not None else (settings.EMAIL_ADMIN_BCC if settings.EMAIL_ADMIN_BCC else None)
            
            logger.debug(f"Using environment defaults for recipients: {final_recipients}")
        else:
            # Production mode: Require explicit recipients
            if not recipients:
                logger.error("Recipients must be provided in production mode (use_env_defaults=False or DEBUG_MODE=False)")
                return False
            final_recipients = recipients
            final_cc = cc
            final_bcc = bcc
        
        return self.send_email(
            subject=subject,
            body=body,
            recipients=final_recipients,
            cc=final_cc,
            bcc=final_bcc,
            html=html,
            attachments=attachments
        )
    
    def send_html_email_with_defaults(
        self,
        subject: str,
        html_body: str,
        recipients: Optional[Union[str, List[str]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[dict]] = None,
        use_env_defaults: bool = True
    ) -> bool:
        """Send HTML email with default recipients (debug mode) or custom recipients (production)"""
        return self.send_email_with_defaults(
            subject=subject,
            body=html_body,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            html=True,
            attachments=attachments,
            use_env_defaults=use_env_defaults
        )
    
    def send_plain_email_with_defaults(
        self,
        subject: str,
        text_body: str,
        recipients: Optional[Union[str, List[str]]] = None,
        cc: Optional[Union[str, List[str]]] = None,
        bcc: Optional[Union[str, List[str]]] = None,
        attachments: Optional[List[dict]] = None,
        use_env_defaults: bool = True
    ) -> bool:
        """Send plain text email with default recipients (debug mode) or custom recipients (production)"""
        return self.send_email_with_defaults(
            subject=subject,
            body=text_body,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            html=False,
            attachments=attachments,
            use_env_defaults=use_env_defaults
        )


# Global email service instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create the global email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
