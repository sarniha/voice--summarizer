import { useState, useRef } from "react"
import axios from "axios"
import "./App.css"

export default function App() {
  const [status, setStatus] = useState("idle")
  const [transcript, setTranscript] = useState("")
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState("")

  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mediaRecorder = new MediaRecorder(stream)
    mediaRecorderRef.current = mediaRecorder
    audioChunksRef.current = []
    mediaRecorder.ondataavailable = (e) => audioChunksRef.current.push(e.data)
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" })
      await sendToBackend(audioBlob, "recording.webm")
    }
    mediaRecorder.start()
    setStatus("recording")
  }

  const stopRecording = () => {
    mediaRecorderRef.current.stop()
    setStatus("loading")
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setStatus("loading")
    await sendToBackend(file, file.name)
  }

  const sendToBackend = async (audioBlob, filename) => {
    setError("")
    const formData = new FormData()
    formData.append("file", audioBlob, filename)
    try {
      const response = await axios.post(
  `${import.meta.env.VITE_API_URL}/upload-audio`,
  formData,
  { headers: { "Content-Type": "multipart/form-data" } }
)
      
      setTranscript(response.data.transcript)
      setSummary(response.data.summary)
      setStatus("result")
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong")
      setStatus("idle")
    }
  }

  const reset = () => {
    setStatus("idle")
    setTranscript("")
    setSummary(null)
    setError("")
  }

  return (
    <div className="container">

      {/* Header — always visible */}
      <header className="header">
        <div className="header-eyebrow">Voice AI</div>
        <h1>
          Turn speech into<br />
          <em>structured insight</em>
        </h1>
        <p className="header-sub">
          Record or upload audio — get a summary, action items, and key points in seconds.
        </p>
      </header>

      {/* Idle */}
      {status === "idle" && (
        <div className="orb-stage">
          <div className="orb-wrapper">
            <div className="orb" />
          </div>
          <div className="actions">
            <button className="btn-primary" onClick={startRecording}>
              Start recording
            </button>
            <div className="divider">or</div>
            <label className="upload-label btn-secondary" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              Upload audio file
              <input type="file" accept=".mp3,.wav,.m4a,.webm,.ogg" onChange={handleFileUpload} />
            </label>
            {error && <p className="error-msg">{error}</p>}
          </div>
        </div>
      )}

      {/* Recording */}
      {status === "recording" && (
        <div className="orb-stage">
          <div className="orb-wrapper recording">
            <div className="orb" />
          </div>
          <div className="actions">
            <div className="recording-status">
              <span className="recording-dot" />
              Listening…
            </div>
            <button className="btn-stop" onClick={stopRecording}>
              Stop &amp; summarize
            </button>
          </div>
        </div>
      )}

      {/* Loading */}
      {status === "loading" && (
        <div className="skeleton-wrapper">
          {[
            ["Summary", ["full", "medium"]],
            ["Action items", ["medium", "short"]],
            ["Key points", ["medium", "short"]],
          ].map(([, lines], i) => (
            <div className="skeleton-card" key={i}>
              <div className="skeleton-label" />
              {lines.map((w, j) => (
                <div className={`skeleton-line ${w}`} key={j} />
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Result */}
      {status === "result" && summary && (
        <div className="result">
          <div className="result-card">
            <div className="result-card-label">Summary</div>
            <p>{summary.summary}</p>
          </div>

          <div className="result-card">
            <div className="result-card-label">Action items</div>
            <ul>
              {summary.action_items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          </div>

          <div className="result-card">
            <div className="result-card-label">Key points</div>
            <ul>
              {summary.key_points.map((point, i) => (
                <li key={i}>{point}</li>
              ))}
            </ul>
          </div>

          <div className="result-card">
            <div className="result-card-label">Full transcript</div>
            <p className="transcript-text">{transcript}</p>
          </div>

          <button className="btn-secondary" onClick={reset} style={{ marginTop: 8 }}>
            Start over
          </button>
        </div>
      )}

    </div>
  )
}
