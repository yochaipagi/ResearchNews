"""Email module for sending digest emails."""
import logging
import os
import jwt
from datetime import datetime, timedelta
from typing import List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent

from .settings import settings
from .models import UserAccount, Paper

# Configure logging
logger = logging.getLogger(__name__)

def generate_unsubscribe_token(user_id: int) -> str:
    """Generate a JWT token for unsubscribe links."""
    expiration = datetime.utcnow() + timedelta(days=365)  # 1 year expiration
    
    payload = {
        "sub": str(user_id),
        "exp": expiration.timestamp(),
        "action": "unsubscribe"
    }
    
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def render_html_template(user: UserAccount, papers: List[Paper]) -> str:
    """Render the HTML email template."""
    # Generate unsubscribe token and URL
    token = generate_unsubscribe_token(user.id)
    unsubscribe_url = f"{settings.BASE_URL}/unsubscribe?token={token}"
    
    # Start building HTML
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            h1 {{ color: #2c3e50; }}
            h2 {{ margin: 0 0 4px; font-size: 18px; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .paper {{ border-bottom: 1px solid #ddd; padding: 12px 0; }}
            .authors {{ margin: 0; color: #555; font-size: 14px; }}
            .abstract {{ margin: 8px 0; font-size: 15px; }}
            .tldr {{ margin: 0 0 12px; font-style: italic; color: #222; }}
            .footer {{ padding-top: 16px; font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <h1>Your Research Digest</h1>
        <p>Hello {user.name or user.email.split('@')[0]},</p>
        <p>Here are the latest papers from arXiv in your areas of interest:</p>
    """
    
    # Add papers
    for p in papers:
        # Truncate abstract to first paragraph and max 1500 chars
        abstract = p.abstract.split('\n\n')[0][:1500]
        if len(p.abstract) > len(abstract):
            abstract += "…"
            
        # Format the paper section
        html += f"""
        <div class="paper">
            <h2><a href="https://arxiv.org/abs/{p.arxiv_id}">{p.title}</a></h2>
            <p class="authors">{p.authors} – {p.published_at.strftime('%Y-%m-%d')}</p>
            <p class="abstract">{abstract}</p>
            <p class="tldr">TL;DR: {p.summary}</p>
        </div>
        """
    
    # Add footer
    html += f"""
        <div class="footer">
            <p>Thanks to arXiv for use of its open-access interoperability.<br>
            <a href="{unsubscribe_url}">Unsubscribe</a> from digest emails</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_digest_email(user: UserAccount, papers: List[Paper]):
    """Send a digest email to a user."""
    try:
        # Create the HTML content
        html_content = render_html_template(user, papers)
        
        # Create email message
        message = Mail(
            from_email=From(settings.EMAIL_FROM_ADDRESS, settings.EMAIL_FROM_NAME),
            to_emails=To(user.email),
            subject=Subject(f"Your Research Digest - {datetime.now().strftime('%Y-%m-%d')}"),
            html_content=HtmlContent(html_content)
        )
        
        # Send the email with SendGrid
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        
        logger.info(f"Email sent to {user.email}, Status: {response.status_code}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {user.email}: {e}")
        return False 