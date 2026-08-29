import React, { useState, useRef, useEffect } from "react";
import { Bot, Send, User, X, Sparkles, BookOpen, AlertCircle, Wrench } from "lucide-react";
import { queryCopilot } from "../api";

export default function CopilotChat({ isOpen, onClose, defaultMachineCode }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "Hello! I am your PredictX Reliability Intelligence Copilot. Ask me to diagnose anomalies, explain developing faults, or retrieve step-by-step repair manuals.",
      citations: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage = { role: "user", text: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await queryCopilot(textToSend);
      const assistantMessage = {
        role: "assistant",
        text: data.answer || "No response generated.",
        citations: data.retrieved_documents || [],
        predictions: data.predictions,
        isMock: data.is_mock,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `⚠️ Error processing query: ${err.message}`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickPrompts = [
    `Analyze health of machine ${defaultMachineCode || "M1000"}`,
    `Why is ${defaultMachineCode || "M1001"} showing high vibration?`,
    "What are the maintenance steps for bearing wear?",
    "Explain overheating dissipation procedures",
  ];

  if (!isOpen) return null;

  return (
    <div style={{
      position: "fixed",
      top: 0,
      right: 0,
      bottom: 0,
      width: "480px",
      maxWidth: "90vw",
      background: "rgba(11, 15, 25, 0.95)",
      backdropFilter: "blur(24px)",
      borderLeft: "1px solid var(--border-subtle)",
      boxShadow: "-10px 0 30px rgba(0,0,0,0.6)",
      display: "flex",
      flexDirection: "column",
      zIndex: 50,
      animation: "slide-in 0.3s ease",
    }}>
      {/* Header */}
      <div style={{
        padding: "18px 22px",
        borderBottom: "1px solid var(--border-subtle)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div style={{
            width: "36px",
            height: "36px",
            borderRadius: "var(--radius-sm)",
            background: "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}>
            <Bot size={20} color="#ffffff" />
          </div>
          <div>
            <h3 style={{ fontSize: "1.05rem", fontWeight: "700" }}>
              Reliability Copilot
            </h3>
            <span style={{ fontSize: "0.72rem", color: "var(--accent-cyan)" }}>
              Hybrid RAG + Production ML Models
            </span>
          </div>
        </div>

        <button
          onClick={onClose}
          style={{ background: "transparent", border: "none", color: "var(--text-dim)", cursor: "pointer" }}
        >
          <X size={20} />
        </button>
      </div>

      {/* Quick Prompts */}
      <div style={{ padding: "10px 16px", background: "rgba(255,255,255,0.02)", borderBottom: "1px solid var(--border-subtle)", overflowX: "auto", display: "flex", gap: "8px", whiteSpace: "nowrap" }}>
        {quickPrompts.map((q, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(q)}
            style={{
              background: "rgba(6, 182, 212, 0.1)",
              border: "1px solid rgba(6, 182, 212, 0.25)",
              color: "var(--accent-cyan)",
              borderRadius: "999px",
              padding: "4px 10px",
              fontSize: "0.72rem",
              fontWeight: "600",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "4px",
            }}
          >
            <Sparkles size={12} />
            {q}
          </button>
        ))}
      </div>

      {/* Messages area */}
      <div style={{ flex: 1, padding: "18px", overflowY: "auto", display: "flex", flexDirection: "column", gap: "16px" }}>
        {messages.map((msg, idx) => {
          const isUser = msg.role === "user";
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: isUser ? "flex-end" : "flex-start",
              }}
            >
              <div style={{
                maxWidth: "85%",
                padding: "14px 16px",
                borderRadius: "var(--radius-md)",
                background: isUser ? "linear-gradient(135deg, #0284c7 0%, #2563eb 100%)" : "var(--bg-glass)",
                border: isUser ? "none" : "1px solid var(--border-subtle)",
                color: "var(--text-main)",
                fontSize: "0.85rem",
                lineHeight: "1.5",
                whiteSpace: "pre-wrap",
                boxShadow: isUser ? "0 4px 12px rgba(37,99,235,0.3)" : "none",
              }}>
                {msg.text}
              </div>

              {/* Citations badge */}
              {msg.citations && msg.citations.length > 0 && (
                <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "6px", fontSize: "0.7rem", color: "var(--text-dim)" }}>
                  <BookOpen size={12} color="var(--accent-cyan)" />
                  <span>Referenced Manuals: {msg.citations.join(", ")}</span>
                </div>
              )}
            </div>
          );
        })}

        {loading && (
          <div style={{ display: "flex", alignItems: "center", gap: "8px", color: "var(--text-dim)", fontSize: "0.8rem" }}>
            <span className="pulse-dot pulse-dot-green" />
            Generating grounded engineering advisory...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input bar */}
      <div style={{ padding: "16px", borderTop: "1px solid var(--border-subtle)", background: "rgba(7, 10, 18, 0.95)" }}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          style={{ display: "flex", gap: "10px" }}
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask about machine faults or manuals...`}
            style={{
              flex: 1,
              padding: "10px 14px",
              background: "rgba(255,255,255,0.05)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-md)",
              color: "var(--text-main)",
              fontSize: "0.85rem",
              outline: "none",
            }}
          />
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ padding: "10px 16px" }}
          >
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
