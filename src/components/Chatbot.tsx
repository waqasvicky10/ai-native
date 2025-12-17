import React, { useState, useEffect, useRef } from 'react';

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: string, content: string, sources?: string[] }[]>([]);
  const [input, setInput] = useState('');
  const [selectedText, setSelectedText] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim().length > 0) {
        setSelectedText(selection.toString().trim());
      } else {
        // Optional: clear selection if they click away, but might be annoying.
        // Keeping it for now.
      }
    };

    document.addEventListener('mouseup', handleSelection);
    return () => document.removeEventListener('mouseup', handleSelection);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const contextToSend = selectedText; // Capture current selection
    setSelectedText(''); // Clear selection after sending

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: userMsg.content,
          context: contextToSend || null
        })
      });

      const data = await response.json();
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      }]);
    } catch (error) {
      console.error("Chatbot Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error connecting to backend.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ position: 'fixed', bottom: '20px', right: '20px', zIndex: 9999 }}>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          style={{
            backgroundColor: '#25c2a0', color: 'white', border: 'none', borderRadius: '50%',
            width: '60px', height: '60px', cursor: 'pointer', boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
            fontSize: '24px'
          }}
        >
          💬
        </button>
      )}

      {isOpen && (
        <div style={{
          width: '350px', height: '500px', backgroundColor: 'white', borderRadius: '10px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)', display: 'flex', flexDirection: 'column',
          overflow: 'hidden', border: '1px solid #ddd'
        }}>
          <div style={{
            backgroundColor: '#25c2a0', color: 'white', padding: '10px', display: 'flex',
            justifyContent: 'space-between', alignItems: 'center'
          }}>
            <strong>Book Assistant</strong>
            <button onClick={() => setIsOpen(false)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>✕</button>
          </div>

          <div style={{ flex: 1, padding: '10px', overflowY: 'auto', backgroundColor: '#f9f9f9', color: '#000000' }}>
            {messages.map((m, i) => (
              <div key={i} style={{ marginBottom: '10px', textAlign: m.role === 'user' ? 'right' : 'left' }}>
                <div style={{
                  display: 'inline-block', padding: '8px 12px', borderRadius: '10px',
                  backgroundColor: m.role === 'user' ? '#007bff' : '#e9ecef',
                  color: m.role === 'user' ? 'white' : 'black',
                  maxWidth: '80%'
                }}>
                  {m.content}
                </div>
                {m.sources && m.sources.length > 0 && (
                  <div style={{ fontSize: '10px', color: '#666', marginTop: '2px' }}>
                    Source: {m.sources.join(', ')}
                  </div>
                )}
              </div>
            ))}
            {loading && <div style={{ textAlign: 'left', color: '#888' }}>Thinking...</div>}
            <div ref={chatEndRef} />
          </div>

          {selectedText && (
            <div style={{ padding: '5px 10px', backgroundColor: '#fff3cd', fontSize: '12px', borderTop: '1px solid #ffeeba', color: '#333' }}>
              <strong>Context:</strong> {selectedText.substring(0, 50)}...
              <button
                onClick={() => setSelectedText('')}
                style={{ marginLeft: '5px', border: 'none', background: 'none', cursor: 'pointer', color: '#666' }}>
                ✕
              </button>
            </div>
          )}

          <div style={{ padding: '10px', borderTop: '1px solid #eee', display: 'flex' }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask a question..."
              style={{ flex: 1, padding: '8px', border: '1px solid #ddd', borderRadius: '4px', marginRight: '5px' }}
            />
            <button onClick={sendMessage} style={{
              padding: '8px 12px', backgroundColor: '#25c2a0', color: 'white', border: 'none',
              borderRadius: '4px', cursor: 'pointer'
            }}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
