function UploadAudio() {
  const [transcript, setTranscript] = React.useState("");

  async function handleFileChange(event) {
    const file = event.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/transcribe", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setTranscript(data.transcription);
  }

  return (
    <div>
      <input type="file" accept="audio/*" onChange={handleFileChange} />
      <p>Transcription: {transcript}</p>
    </div>
  );
}
