import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

MAX_RESULTS = 5


def web_search(query: str) -> str:
    logger.debug("Web search: %r", query)
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_RESULTS))
        if not results:
            return "No results found."
        lines = [f"**🔍 Search results for:** {query}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"**{i}. {r['title']}**")
            lines.append(r['body'])
            lines.append(f"🔗 {r['href']}\n")
        return "\n".join(lines)
    except Exception as e:
        logger.error("Web search error: %s", e)
        return f"Search failed: {e}"


def price_search(product: str) -> str:
    logger.debug("Price search: %r", product)
    query = f"{product} price buy online"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_RESULTS))
        if not results:
            return "No price results found."
        lines = [f"**💰 Price results for:** {product}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"**{i}. {r['title']}**")
            lines.append(r['body'])
            lines.append(f"🔗 {r['href']}\n")
        return "\n".join(lines)
    except Exception as e:
        logger.error("Price search error: %s", e)
        return f"Price search failed: {e}"


def restaurant_search(location: str) -> str:
    logger.debug("Restaurant search: %r", location)
    query = f"best restaurants near {location} with menu"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=MAX_RESULTS))
        if not results:
            return "No restaurants found."
        lines = [f"**🍽️ Restaurants near:** {location}\n"]
        for i, r in enumerate(results, 1):
            lines.append(f"**{i}. {r['title']}**")
            lines.append(r['body'])
            lines.append(f"🔗 {r['href']}\n")
        return "\n".join(lines)
    except Exception as e:
        logger.error("Restaurant search error: %s", e)
        return f"Restaurant search failed: {e}"


def send_email(to: str, subject: str, body: str) -> str:
    gmail_address = os.environ.get("GMAIL_ADDRESS", "").strip()
    gmail_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not gmail_address or not gmail_password:
        return "❌ Email not configured. Add GMAIL_ADDRESS and GMAIL_APP_PASSWORD to Railway Variables."

    logger.debug("Sending email to %s, subject: %r", to, subject)
    try:
        msg = MIMEMultipart()
        msg["From"] = gmail_address
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_password)
            server.sendmail(gmail_address, to, msg.as_string())

        logger.info("Email sent to %s", to)
        return f"✅ Email sent to **{to}**\n**Subject:** {subject}"
    except smtplib.SMTPAuthenticationError:
        return "❌ Gmail authentication failed. Make sure you're using an App Password, not your regular Gmail password."
    except Exception as e:
        logger.error("Email send error: %s", e)
        return f"❌ Failed to send email: {e}"
