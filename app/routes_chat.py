"""
Chat Routes untuk RAG-based Question Answering dengan Chroma Vector Database
"""

from flask import Blueprint, request, jsonify, render_template, session
from functools import wraps
from datetime import datetime
from .smart_search import ChromaDocumentSearch
from .groq_integration import GroqChatManager  # Primary AI provider (Gemini free tier API not available)
from .models import db, ChatSession, ChatMessage, ChatMessageSource, ChatFeedback
import os

# Global instances - using dictionary to avoid scoping issues
_system_state = {
    'chat_manager': None,
    'fallback_chat_manager': None,  # Groq is primary AI
    'search_engine': None
}

def initialize_chat_system():
    """Initialize chat system dengan Groq (PRIMARY) dan Chroma"""
    global _system_state
    
    try:
        # SKIP Gemini (free tier v1beta API tidak support)
        
        # Initialize Groq as PRIMARY AI (RECOMMENDED: proven working)
        groq_manager = GroqChatManager()
        print(f"✅ Groq Manager created. Initialized: {groq_manager.initialized}")
        
        # Initialize Chroma-based search engine
        credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials.json')
        chroma_engine = ChromaDocumentSearch(credentials_path)
        
        # Store in global state
        _system_state['fallback_chat_manager'] = groq_manager
        _system_state['search_engine'] = chroma_engine
        
        # Status
        groq_ok = groq_manager.initialized
        
        print(f"✅ Chat system initialized")
        print(f"   AI Provider (Groq PRIMARY): {'✅' if groq_ok else '❌'}")
        print(f"   Vector DB (Chroma): ✅")
        print(f"   System state updated successfully")
        
    except Exception as e:
        print(f"❌ Error initializing chat system: {e}")
        import traceback
        traceback.print_exc()


def require_login(f):
    """Decorator untuk memastikan user sudah login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_or_create_active_session(user_id: int) -> ChatSession:
    """Get atau create active chat session untuk user"""
    session_obj = ChatSession.query.filter_by(
        peserta_id=user_id,
        is_active=True
    ).order_by(ChatSession.updated_at.desc()).first()
    
    if not session_obj:
        session_obj = ChatSession(peserta_id=user_id)
        db.session.add(session_obj)
        db.session.commit()
    
    return session_obj


chat = Blueprint('chat', __name__, url_prefix='/api/chat')


@chat.route('/health', methods=['GET'])
def chat_health():
    """Check chat system health"""
    groq_mgr = _system_state.get('fallback_chat_manager')
    return jsonify({
        'status': 'ok',
        'groq_available': groq_mgr.initialized if groq_mgr else False,
        'search_available': _system_state['search_engine'] is not None
    })


@chat.route('/ask', methods=['POST'])
@require_login
def ask_question():
    """
    Main endpoint untuk tanya-jawab dengan RAG + Chroma Vector DB
    
    POST /api/chat/ask
    {
        'question': str,
        'use_documents': bool (default: True),
        'search_limit': int (default: 5)
    }
    """
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        question = data.get('question', '').strip()
        use_documents = data.get('use_documents', True)
        search_limit = data.get('search_limit', 5)
        
        # Validasi input
        if not question or len(question) < 2:
            return jsonify({'error': 'Pertanyaan terlalu pendek. Minimal 2 karakter.'}), 400
        
        if len(question) > 1000:
            return jsonify({'error': 'Pertanyaan terlalu panjang. Maksimal 1000 karakter.'}), 400
        
        # Get atau create active chat session
        chat_session = get_or_create_active_session(user_id)
        
        # Save user message to database
        user_msg = ChatMessage(
            session_id=chat_session.id,
            role='user',
            content=question
        )
        db.session.add(user_msg)
        db.session.commit()
        
        # Search documents dari Chroma
        context = ""
        sources = []
        
        search_engine = _system_state.get('search_engine')
        if use_documents and search_engine:
            try:
                search_results = search_engine.search(
                    query=question,
                    search_limit=search_limit,
                    results_limit=10
                )
                
                # Format context untuk AI
                context = search_engine.format_context_for_ai(search_results)
                
                # Collect sources
                for result in search_results.get('results', []):
                    for chunk in result.get('chunks', []):
                        sources.append({
                            'file_id': result['file_id'],
                            'file_name': result['file_name'],
                            'relevance': chunk['similarity']
                        })
            except Exception as e:
                print(f"⚠️  Error searching documents in Chroma: {e}")
        
        # Generate answer dengan Groq (ONLY AI provider)
        # Groq: FREE tier dengan 1000 req/hari, super cepat, reliable
        result = {'success': False, 'error': 'Groq AI provider not available'}
        
        # Get Groq manager from system state
        groq_manager = _system_state.get('fallback_chat_manager')
        
        # Use Groq ONLY (Gemini free tier tidak support v1beta API)
        if groq_manager and groq_manager.initialized:
            try:
                print(f"🚀 Using Groq AI for response...")
                result = groq_manager.generate_answer(
                    query=question,
                    context=context
                )
                if result['success']:
                    print(f"✅ Groq response generated successfully")
            except Exception as e:
                print(f"❌ Groq error: {e}")
                result = {'success': False, 'error': f'Groq API error: {str(e)[:100]}'}
        else:
            print(f"❌ Groq chat manager not initialized! State: {_system_state}")
            return jsonify({
                'success': False,
                'error': 'AI provider not initialized. Please restart the application.',
                'answer': None
            }), 500
        
        # If Groq fails, return error (no fallback to Gemini)
        if not result.get('success'):
            error_msg = result.get('error', 'Groq API error')
            return jsonify({
                'success': False,
                'error': error_msg,
                'answer': None
            }), 500
        
        # Save assistant message to database
        if result['success']:
            assistant_msg = ChatMessage(
                session_id=chat_session.id,
                role='assistant',
                content=result['answer'],
                tokens_used=result.get('tokens')
            )
            db.session.add(assistant_msg)
            db.session.flush()  # Get the ID
            
            # Save sources
            for source in sources[:5]:  # Limit to top 5 sources
                source_record = ChatMessageSource(
                    message_id=assistant_msg.id,
                    file_name=source['file_name'],
                    relevance_score=source['relevance']
                )
                db.session.add(source_record)
            
            db.session.commit()
        
        # Update session timestamp
        chat_session.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': result['success'],
            'answer': result.get('answer'),
            'sources': sources,
            'with_rag': result.get('with_rag', False),
            'model': result.get('model'),
            'error': result.get('error'),
            'generated_at': result.get('generated_at'),
            'session_id': chat_session.id
        })
    
    except Exception as e:
        print(f"❌ Error in ask endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@chat.route('/history', methods=['GET'])
@require_login
def get_history():
    """Get persistent chat history dari database"""
    try:
        user_id = session.get('user_id')
        limit = request.args.get('limit', 20, type=int)
        
        # Get active chat session
        chat_session = ChatSession.query.filter_by(
            peserta_id=user_id,
            is_active=True
        ).order_by(ChatSession.updated_at.desc()).first()
        
        if not chat_session:
            return jsonify({
                'success': True,
                'history': [],
                'session_id': None
            })
        
        # Get messages dari session
        messages = ChatMessage.query.filter_by(
            session_id=chat_session.id
        ).order_by(ChatMessage.timestamp.asc()).limit(limit).all()
        
        history = []
        for msg in messages:
            msg_data = {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'sources': []
            }
            
            # Get sources jika ada
            if msg.sources:
                msg_data['sources'] = [
                    {
                        'file_name': s.file_name,
                        'relevance': s.relevance_score
                    }
                    for s in msg.sources
                ]
            
            history.append(msg_data)
        
        return jsonify({
            'success': True,
            'history': history,
            'session_id': chat_session.id,
            'total_messages': len(history)
        })
    except Exception as e:
        print(f"❌ Error getting history: {e}")
        return jsonify({'error': str(e)}), 500


@chat.route('/history/clear', methods=['POST'])
@require_login
def clear_history():
    """Close active chat session dan start new one"""
    try:
        user_id = session.get('user_id')
        
        # Get active session
        chat_session = ChatSession.query.filter_by(
            peserta_id=user_id,
            is_active=True
        ).first()
        
        if chat_session:
            chat_session.is_active = False
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Chat session closed. New session will be created on next question.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat.route('/stats', methods=['GET'])
def get_chat_stats():
    """Get Chroma vector database statistics"""
    try:
        search_engine = _system_state.get('search_engine')
        if not search_engine:
            return jsonify({'error': 'Search engine not available'}), 503
        
        stats = search_engine.get_stats()
        
        return jsonify({
            'success': True,
            'vector_store': stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat.route('/search', methods=['POST'])
@require_login
def search_documents():
    """
    Direct document search endpoint menggunakan Chroma
    
    POST /api/chat/search
    {
        'query': str,
        'limit': int (default: 5)
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({'error': 'Query tidak boleh kosong'}), 400
        
        search_engine = _system_state.get('search_engine')
        if not search_engine:
            return jsonify({'error': 'Search engine tidak tersedia'}), 503
        
        results = search_engine.search(query, search_limit=limit, results_limit=10)
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results.get('results', []),
            'total_documents': results.get('total_results', 0)
        })
    
    except Exception as e:
        print(f"❌ Error in search endpoint: {e}")
        return jsonify({'error': str(e)}), 500


@chat.route('/extract-key-points', methods=['POST'])
@require_login
def extract_key_points():
    """
    Extract key points dari text
    
    POST /api/chat/extract-key-points
    {
        'text': str
    }
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text tidak boleh kosong'}), 400
        
        if not chat_manager:
            return jsonify({'error': 'AI engine tidak tersedia'}), 503
        
        result = chat_manager.extract_key_points(text)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat.route('/suggest-questions', methods=['POST'])
@require_login
def suggest_questions():
    """
    Suggest pertanyaan berdasarkan context
    
    POST /api/chat/suggest-questions
    {
        'document_name': str (optional)
    }
    """
    try:
        # List pertanyaan umum untuk mekanik
        suggestions = {
            'umum': [
                'Bagaimana cara perawatan berkala kendaraan?',
                'Apa saja persiapan sebelum service?',
                'Bagaimana cara mendiagnosa masalah mesin?',
                'Berapa interval penggantian oli standar?',
                'Bagaimana cara setting timing ignition?',
            ],
            'teknis': [
                'Apa perbedaan sistem direct injection vs indirect injection?',
                'Bagaimana cara membaca kode error pada OBD?',
                'Bagaimana cara tune-up kendaraan?',
                'Apa tanda-tanda clutch yang perlu diganti?',
                'Bagaimana cara check dan set valve clearance?',
            ]
        }
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# UI Route
@chat.route('/page', methods=['GET'])
@require_login
def chat_page():
    """Render chat page"""
    from flask import current_app
    from flask_wtf.csrf import generate_csrf
    try:
        return render_template('user/chat.html', csrf_token=generate_csrf())
    except Exception as e:
        print(f"❌ Error rendering chat page: {e}")
        return jsonify({'error': 'Could not render chat page'}), 500


def register_chat_routes(app):
    """Register chat routes ke app"""
    initialize_chat_system()
    app.register_blueprint(chat)
    print("✅ Chat routes registered")
