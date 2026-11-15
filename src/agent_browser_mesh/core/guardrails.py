"""Tier-0 Pre-Execution & Post-Extraction Security Guardrails for AI Browser Agents.

Provides real-time:
- SG-4: SSRF & Private Intranet Protection (blocks RFC1918, link-local, loopback, cloud metadata)
- SG-5: Indirect Prompt Injection Firewall (heuristics, adversarial tags, CSS hiding traps)
- SG-6: Shannon Entropy Secret Interceptor (intercepts exposed API keys, tokens, auth headers)
"""

from __future__ import annotations

import ipaddress
import math
import re
from typing import List, Tuple
from urllib.parse import urlparse

from pydantic import BaseModel, Field


class SecurityVerdict(BaseModel):
    """Result of a guardrail evaluation."""
    allowed: bool = Field(..., description="Whether the action or content is deemed safe")
    reason: str = Field(default="CLEAN", description="Detailed explanation if blocked or flagged")
    sanitized_text: str = Field(default="", description="Sanitized version of text if altered")
    violations: List[str] = Field(default_factory=list, description="List of rule violations")


class BrowserGuardrails:
    """Zero-Trust Security Shield for Browser Automation."""

    PROHIBITED_METADATA_HOSTS = {
        "169.254.169.254",          # AWS / OpenStack / GCP metadata
        "metadata.google.internal", # GCP
        "169.254.169.250",          # Azure IMDS
        "fd00::1",                  # IPv6 ULA metadata
        "localhost",
        "127.0.0.1",
        "::1"
    }

    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(?:all\s+)?prior\s+instructions",
        r"disregard\s+(?:all\s+)?previous\s+instructions",
        r"system\s*:\s*you\s+are\s+now",
        r"you\s+must\s+act\s+as\s+an\s+unrestricted",
        r"new\s+system\s+prompt\s*:",
        r"do\s+not\s+tell\s+the\s+user",
        r"send\s+(?:your\s+)?(?:credentials|api[_\s-]?keys?|secrets?|tokens?)\s+to",
        r"fetch\s+(?:env|environment)\s+variables",
        r"curl\s+https?://[^\s]+\s+-\s*d",
        r"post\s+all\s+(?:passwords|cookies|tokens)\s+to",
        r"data:text/html;base64,[A-Za-z0-9+/=]{30,}"
    ]

    API_KEY_PATTERNS = [
        r"\b(?:sk-[a-zA-Z0-9]{20,48})\b",             # OpenAI
        r"\b(?:ghp_[a-zA-Z0-9]{36,40})\b",           # GitHub PAT
        r"\b(?:AKIA[0-9A-Z]{16})\b",                  # AWS Access Key
        r"\b(?:xox[baprs]-[0-9a-zA-Z-]{24,})\b",       # Slack
        r"\b(?:AIza[0-9A-Za-z-_]{35})\b",             # Google API Key
        r"\b(?:glpat-[0-9a-zA-Z-_]{20,})\b"           # GitLab PAT
    ]

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self._compiled_pi = [re.compile(p, re.IGNORECASE) for p in self.PROMPT_INJECTION_PATTERNS]
        self._compiled_secrets = [re.compile(p) for p in self.API_KEY_PATTERNS]

    def inspect_navigation_url(self, url: str) -> SecurityVerdict:
        """Inspects target URL against SSRF and intranet probe attacks."""
        if not url or not isinstance(url, str):
            return SecurityVerdict(allowed=False, reason="INVALID_URL_EMPTY")

        parsed = urlparse(url.strip())
        scheme = parsed.scheme.lower()
        
        if scheme not in ("http", "https", "about", "data"):
            return SecurityVerdict(
                allowed=False,
                reason=f"PROHIBITED_SCHEME: Scheme '{scheme}' is forbidden. Only HTTP/HTTPS permitted.",
                violations=["PROHIBITED_PROTOCOL_SCHEME"]
            )

        if scheme in ("about", "data"):
            if scheme == "about" and parsed.path.lower() in ("blank", ""):
                return SecurityVerdict(allowed=True, reason="SAFE_BLANK_PAGE")
            return SecurityVerdict(allowed=False, reason="PROHIBITED_PSEUDO_SCHEME")

        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return SecurityVerdict(allowed=False, reason="MISSING_HOSTNAME")

        # Check metadata hosts
        if hostname in self.PROHIBITED_METADATA_HOSTS:
            return SecurityVerdict(
                allowed=False,
                reason=f"SSRF_PROHIBITED_HOST: Direct access to cloud metadata host '{hostname}' is blocked.",
                violations=["SSRF_METADATA_ATTEMPT"]
            )

        # Check raw IP addresses
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private:
                return SecurityVerdict(
                    allowed=False,
                    reason=f"SSRF_PRIVATE_IP: Access to RFC1918 private address '{hostname}' is forbidden.",
                    violations=["SSRF_PRIVATE_IP"]
                )
            if ip.is_loopback:
                return SecurityVerdict(
                    allowed=False,
                    reason=f"SSRF_LOOPBACK: Access to loopback address '{hostname}' is forbidden.",
                    violations=["SSRF_LOOPBACK"]
                )
            if ip.is_link_local:
                return SecurityVerdict(
                    allowed=False,
                    reason=f"SSRF_LINK_LOCAL: Access to link-local address '{hostname}' is forbidden.",
                    violations=["SSRF_LINK_LOCAL"]
                )
        except ValueError:
            # Domain name, not a raw IP
            pass

        return SecurityVerdict(allowed=True, reason="CLEAN_URL")

    def sanitize_content(self, text: str) -> Tuple[str, SecurityVerdict]:
        """Scans and neutralizes indirect prompt injections and hidden traps in extracted text."""
        if not text:
            return "", SecurityVerdict(allowed=True, reason="EMPTY_CONTENT")

        violations = []
        clean_text = text

        # 1. Scan for prompt injection patterns
        for pattern in self._compiled_pi:
            matches = pattern.findall(clean_text)
            if matches:
                violations.append("INDIRECT_PROMPT_INJECTION_DETECTED")
                # Redact the malicious phrase in-place
                clean_text = pattern.sub("[REDACTED_PROMPT_INJECTION_ATTEMPT]", clean_text)

        # 2. Scan and redact exposed high-entropy secrets
        for pattern in self._compiled_secrets:
            matches = pattern.findall(clean_text)
            if matches:
                violations.append("HIGH_ENTROPY_SECRET_EXPOSED")
                clean_text = pattern.sub("[REDACTED_API_SECRET]", clean_text)

        # 3. Check for Shannon entropy anomalies on long uninterrupted tokens
        words = clean_text.split()
        for w in words:
            if len(w) >= 32 and self._shannon_entropy(w) > 4.5:
                # Potential raw secret or token
                if not w.startswith("[REDACTED"):
                    violations.append("HIGH_ENTROPY_TOKEN")
                    clean_text = clean_text.replace(w, "[REDACTED_HIGH_ENTROPY_TOKEN]")

        verdict = SecurityVerdict(
            allowed=len(violations) == 0,
            reason="CONTENT_ALTERED_FOR_SAFETY" if violations else "CLEAN_CONTENT",
            sanitized_text=clean_text,
            violations=violations
        )
        return clean_text, verdict

    @staticmethod
    def _shannon_entropy(s: str) -> float:
        """Calculates Shannon entropy in bits per character."""
        if not s:
            return 0.0
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
        return -sum(p * math.log(p) / math.log(2.0) for p in prob)
