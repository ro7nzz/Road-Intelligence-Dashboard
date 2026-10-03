import React, { useRef } from 'react';

export default function AnalysisUpload({ selectedFile, setSelectedFile }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const removeFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="glass-panel roadai-upload-card">
      <div className="roadai-section-heading">
        <div className="roadai-section-icon">?</div>
        <div>
          <h3>Road Image Source</h3>
          <p>Upload imagery for AI damage detection</p>
        </div>
      </div>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".jpg,.jpeg,.png,.webp,.bmp"
        style={{ display: 'none' }}
      />

      {!selectedFile ? (
        <div
          className="roadai-dropzone"
          onClick={() => fileInputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          <div className="roadai-drop-glow" />

          <div className="roadai-upload-icon">
            <span>?</span>
          </div>

          <div className="roadai-upload-title">
            Drop road imagery here
          </div>

          <div className="roadai-upload-subtitle">
            or <span>browse from your device</span>
          </div>

          <div className="roadai-format-row">
            <span>JPG</span>
            <span>JPEG</span>
            <span>PNG</span>
            <span>WEBP</span>
            <span>BMP</span>
          </div>

          <div className="roadai-upload-hint">
            AI accepts road inspection imagery up to 10 MB
          </div>
        </div>
      ) : (
        <div className="roadai-file-preview">
          <div className="roadai-preview-image">
            <img
              src={URL.createObjectURL(selectedFile)}
              alt="Selected road preview"
            />
            <div className="roadai-preview-overlay">
              READY
            </div>
          </div>

          <div className="roadai-file-info">
            <div className="roadai-file-status">
              <span className="roadai-status-pulse" />
              IMAGE LOADED
            </div>

            <div className="roadai-file-name">
              {selectedFile.name}
            </div>

            <div className="roadai-file-meta">
              {(selectedFile.size / 1024).toFixed(1)} KB
              <span>•</span>
              Ready for AI analysis
            </div>
          </div>

          <button
            type="button"
            onClick={removeFile}
            className="roadai-change-button"
          >
            Change
          </button>
        </div>
      )}
    </div>
  );
}
