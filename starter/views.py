"""Django Text-to-Speech Starter - Views"""
import functools
import os
import json
import secrets
import time

import jwt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from deepgram import DeepgramClient
from dotenv import load_dotenv
import toml

load_dotenv()
API_KEY = os.environ.get("DEEPGRAM_API_KEY")
if not API_KEY:
    raise ValueError("DEEPGRAM_API_KEY required")
deepgram = DeepgramClient(api_key=API_KEY)

# ============================================================================
# SESSION AUTH - JWT tokens for production security
# ============================================================================

SESSION_SECRET = os.environ.get("SESSION_SECRET") or secrets.token_hex(32)
JWT_EXPIRY = 3600  # 1 hour


# Read frontend/dist/index.html for serving (production only)
_index_html_template = None
try:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist", "index.html")) as f:
        _index_html_template = f.read()
except FileNotFoundError:
    pass  # No built frontend (dev mode)


def require_session(f):
    """Decorator that validates JWT from Authorization header."""
    @functools.wraps(f)
    def decorated(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse({
                "error": {
                    "type": "AuthenticationError",
                    "code": "MISSING_TOKEN",
                    "message": "Authorization header with Bearer token is required",
                }
            }, status=401)
        token = auth_header[7:]
        try:
            jwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return JsonResponse({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_TOKEN",
                    "message": "Session expired, please refresh the page",
                }
            }, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({
                "error": {
                    "type": "AuthenticationError",
                    "code": "INVALID_TOKEN",
                    "message": "Invalid session token",
                }
            }, status=401)
        return f(request, *args, **kwargs)
    return decorated


# ============================================================================
# SESSION ROUTES - Auth endpoints (unprotected)
# ============================================================================

def serve_index(request):
    """Serve index.html (production only)."""
    if not _index_html_template:
        return HttpResponse("Frontend not built. Run make build first.", status=404)
    return HttpResponse(_index_html_template, content_type="text/html")


def get_session(request):
    """Issues a JWT session token."""
    token = jwt.encode(
        {"iat": int(time.time()), "exp": int(time.time()) + JWT_EXPIRY},
        SESSION_SECRET,
        algorithm="HS256",
    )
    return JsonResponse({"token": token})


# ============================================================================
# API ROUTES - Define your API endpoints here
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
@require_session
def synthesize(request):
    """POST /api/text-to-speech"""
    try:
        body = json.loads(request.body)
        text = body.get('text')
        if not text or not text.strip():
            return JsonResponse({
                "error": {
                    "type": "ValidationError",
                    "code": "INVALID_INPUT",
                    "message": "Text required"
                }
            }, status=400)

        model = request.POST.get('model', 'aura-asteria-en')

        audio_generator = deepgram.speak.v1.audio.generate(
            text=text,
            model=model
        )
        audio_data = b"".join(audio_generator)

        return HttpResponse(audio_data, content_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Error: {e}")
        error_msg = str(e).lower()

        # Check if it's a Deepgram text length error
        if any(keyword in error_msg for keyword in ['too long', 'length', 'limit', 'exceed']):
            return JsonResponse({
                "error": {
                    "type": "ValidationError",
                    "code": "TEXT_TOO_LONG",
                    "message": "Text exceeds maximum allowed length"
                }
            }, status=400)

        return JsonResponse({
            "error": {
                "type": "SynthesisError",
                "code": "SYNTHESIS_FAILED",
                "message": str(e)
            }
        }, status=500)

@require_http_methods(["GET"])
def metadata(request):
    """GET /api/metadata"""
    try:
        with open('deepgram.toml', 'r') as f:
            return JsonResponse(toml.load(f).get('meta', {}))
    except:
        return JsonResponse({
            "error": {
                "type": "MetadataError",
                "code": "METADATA_FAILED",
                "message": "Failed to read metadata"
            }
        }, status=500)
