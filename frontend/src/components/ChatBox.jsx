import { useState, useRef, useEffect } from 'react'
import { getApiUrl } from '../utils/env'

export default function ChatBox() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const chatEndRef = useRef(null)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const askQuestion = async (e) => {
    e.preventDefault()
    if (!question.trim()) return

    // Add user message to chat
    const userMessage = { type: 'user', content: question }
    setMessages(prev => [...prev, userMessage])
    setQuestion('') // Clear the input
    setIsStreaming(true)

    try {
      const res = await fetch(`${getApiUrl()}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: question }),
      })

      if (!res.ok) {
        try {
          const errorData = await res.json()
          throw new Error(errorData.error || `HTTP error! status: ${res.status}`)
        } catch (e) {
          throw new Error(`HTTP error! status: ${res.status}`)
        }
      }

      let aiResponse = ''
      if (res.body) {
        const reader = res.body.getReader()
        const decoder = new TextDecoder('utf-8')
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          const text = decoder.decode(value)
          try {
            const parsed = JSON.parse(text)
            const responseText = parsed.response || parsed.final_response || text
            aiResponse += responseText
            setMessages(prev => {
              const newMessages = [...prev]
              if (newMessages[newMessages.length - 1]?.type === 'ai') {
                newMessages[newMessages.length - 1].content = aiResponse
              } else {
                newMessages.push({ type: 'ai', content: aiResponse })
              }
              return newMessages
            })
          } catch {
            aiResponse += text
            setMessages(prev => {
              const newMessages = [...prev]
              if (newMessages[newMessages.length - 1]?.type === 'ai') {
                newMessages[newMessages.length - 1].content = aiResponse
              } else {
                newMessages.push({ type: 'ai', content: aiResponse })
              }
              return newMessages
            })
          }
        }
      } else {
        const data = await res.json()
        const responseText = data.response || data.final_response || 'No response received'
        setMessages(prev => [...prev, { type: 'ai', content: responseText }])
      }
    } catch (error) {
      console.error('Error:', error)
      setMessages(prev => [...prev, { type: 'ai', content: 'Error: ' + error.message }])
    } finally {
      setIsStreaming(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      askQuestion(e)
    }
  }

  return (
    <>
      <div className="response-panel" data-testid="response-panel">
        {messages.length === 0 ? (
          'Ask me anything about golf...'
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`message ${message.type === 'user' ? 'user-message' : 'ai-message'}`}
            >
              {message.content}
            </div>
          ))
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="question-input-row">
        <textarea
          data-testid="question-input"
          rows={3}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about golf... (Press Enter to submit, Shift+Enter for new line)"
        />

        <button onClick={askQuestion} disabled={isStreaming}>
          {isStreaming ? 'Thinking…' : 'Ask'}
        </button>
      </div>
    </>
  )
}
