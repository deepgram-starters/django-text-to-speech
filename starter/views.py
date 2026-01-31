"""Django Text-to-Speech Starter - Views"""
import os, json
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

@csrf_exempt
@require_http_methods(["POST"])
def synthesize(request):
    """POST /tts/synthesize"""
    try:
        body = json.loads(request.body)
        text = body.get('text')
        if not text or not text.strip():
            return JsonResponse({"error": "Text required"}, status=400)
        
        model = request.POST.get('model', 'aura-asteria-en')
        options = {"text": text}
        response = deepgram.speak.rest.v("1").stream_raw(options, {"model": model})
        audio_data = b"".join(response.stream)
        
        return HttpResponse(audio_data, content_type="audio/mpeg")
    except Exception as e:
        print(f"TTS Error: {e}")
        return JsonResponse({"error": "TTS synthesis failed"}, status=500)

@require_http_methods(["GET"])
def metadata(request):
    """GET /api/metadata"""
    try:
        with open('deepgram.toml', 'r') as f:
            return JsonResponse(toml.load(f).get('meta', {}))
    except:
        return JsonResponse({'error': 'Failed'}, status=500)
