# ai_assistant/views.py
import json
import traceback
from django.http import JsonResponse
import google.generativeai as genai

from .services import GEMINI_MODEL
from . import tools

def chat_with_ai(request):
    if GEMINI_MODEL is None:
        return JsonResponse({'error': 'Service IA non disponible.'}, status=503)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            if not user_message:
                return JsonResponse({'error': 'Message vide.'}, status=400)

            chat_history = request.session.get('ai_chat_history', [])
            chat_session = GEMINI_MODEL.start_chat(history=chat_history)
            
            # On envoie le message de l'utilisateur
            response = chat_session.send_message(user_message)

            # On boucle TANT QUE l'IA nous demande d'appeler des outils
            # Boucle tant que l'IA demande d'appeler un outil
            while response.candidates and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                if part.function_call:
                    function_call = part.function_call
                    tool_name = function_call.name
                    tool_args = {k: v for k, v in function_call.args.items()}

                    if hasattr(tools, tool_name):
                        tool_function = getattr(tools, tool_name)
                        tool_response_data = tool_function(**tool_args)

                        # On renvoie le résultat de l'outil pour continuer la conversation
                        response = chat_session.send_message(
                            genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(
                                    name=tool_name,
                                    response={"result": tool_response_data},
                                )
                            )
                        )
                    else:
                        ai_response_text = f"Erreur : outil inconnu '{tool_name}'."
                        break
                elif part.text:
                    ai_response_text = part.text
                    break
                else:
                    ai_response_text = "Erreur : réponse inconnue."
                    break



            # Mise à jour de l'historique de session
            chat_history.append({'role': 'user', 'parts': [{'text': user_message}]})
            chat_history.append({'role': 'model', 'parts': [{'text': ai_response_text}]})
            request.session['ai_chat_history'] = chat_history[-10:]

            return JsonResponse({'reply': ai_response_text})

        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'error': f"Une erreur interne est survenue: {str(e)}"}, status=500)
            
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)