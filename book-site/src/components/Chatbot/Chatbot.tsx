import React, { useState, useRef, useEffect } from 'react';
import styles from './Chatbot.module.css';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  content: string;
  source: string;
  relevance_score: number;
}

interface ChatbotProps {
  backendUrl?: string;
}

const Chatbot: React.FC<ChatbotProps> = ({ 
  backendUrl = 'http://localhost:8000' 
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Listen for text selection on the page
  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection?.toString().trim();
      if (text && text.length > 10) {
        setSelectedText(text);
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  const handleSendMessage = async (useSelected: boolean = false) => {
    if (!input.trim() && !useSelected) return;

    const questionText = input.trim();
    const userMessage: Message = { 
      role: 'user', 
      content: useSelected && selectedText 
        ? `About: "${selectedText.substring(0, 100)}..." - ${questionText}`
        : questionText
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          question: questionText,
          selected_text: useSelected ? selectedText : null
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      const assistantMessage: Message = { 
        role: 'assistant', 
        content: data.answer,
        sources: data.sources
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // Clear selected text after use
      if (useSelected) {
        setSelectedText('');
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again or check if the backend is running.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const quickQuestions = [
    "What is ROS 2?",
    "Explain NVIDIA Isaac",
    "How does Gazebo simulation work?",
    "What are humanoid robot challenges?"
  ];

  const handleQuickQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <>
      {/* Floating chat button */}
      <button 
        className={styles.floatingButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chatbot"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat window */}
      {isOpen && (
        <div className={styles.chatContainer}>
          <div className={styles.chatHeader}>
            <h3>📚 Physical AI Assistant</h3>
            <button onClick={clearChat} className={styles.clearButton}>
              Clear Chat
            </button>
          </div>

          <div className={styles.messagesContainer}>
            {messages.length === 0 ? (
              <div className={styles.welcomeMessage}>
                <h4>👋 Hello! I'm your Physical AI textbook assistant.</h4>
                <p>Ask me anything about:</p>
                <ul>
                  <li>ROS 2 and robot control</li>
                  <li>Gazebo & Unity simulation</li>
                  <li>NVIDIA Isaac platform</li>
                  <li>Humanoid robotics</li>
                </ul>
                <div className={styles.quickQuestions}>
                  <p><strong>Quick questions:</strong></p>
                  {quickQuestions.map((q, idx) => (
                    <button
                      key={idx}
                      className={styles.quickQuestionButton}
                      onClick={() => handleQuickQuestion(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`${styles.message} ${styles[msg.role]}`}
                >
                  <div className={styles.messageContent}>
                    {msg.content}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className={styles.sources}>
                      <details>
                        <summary>📚 Sources ({msg.sources.length})</summary>
                        <ul>
                          {msg.sources.map((source, i) => (
                            <li key={i}>
                              <strong>{source.source}</strong>
                              <span className={styles.relevanceScore}>
                                {(source.relevance_score * 100).toFixed(0)}% match
                              </span>
                              <p>{source.content}</p>
                            </li>
                          ))}
                        </ul>
                      </details>
                    </div>
                  )}
                </div>
              ))
            )}
            
            {loading && (
              <div className={`${styles.message} ${styles.assistant}`}>
                <div className={styles.loadingDots}>
                  <span>.</span><span>.</span><span>.</span>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {selectedText && (
            <div className={styles.selectedTextBanner}>
              <span>💡 Text selected: "{selectedText.substring(0, 50)}..."</span>
              <button 
                onClick={() => handleSendMessage(true)}
                className={styles.askAboutButton}
                disabled={!input.trim()}
              >
                Ask about this
              </button>
            </div>
          )}

          <div className={styles.inputArea}>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                selectedText 
                  ? "Ask a question about the selected text..." 
                  : "Ask me anything about the textbook..."
              }
              disabled={loading}
              rows={2}
            />
            <button 
              onClick={() => handleSendMessage(false)} 
              disabled={loading || !input.trim()}
              className={styles.sendButton}
            >
              {loading ? '⏳' : '📤'}
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export default Chatbot;