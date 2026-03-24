"use client";

import React, { useState } from "react";

interface ImageInputFieldProps {
  label: string;
  value?: string;
  onChange: (url: string) => void;
  onUpload?: (imageUrl: string, fileName: string) => void;
  error?: string;
  placeholder?: string;
}

export function ImageInputField({
  label,
  value = "",
  onChange,
  onUpload,
  error,
  placeholder = "https://example.com/image.jpg"
}: ImageInputFieldProps) {
  const [isHoveringUpload, setIsHoveringUpload] = useState(false);

  return (
    <div style={{ marginBottom: "16px" }}>
      <label style={{ display: "block", marginBottom: "8px", fontWeight: "500", color: "#44546A" }}>
        {label}
      </label>

      <div style={{ display: "flex", gap: "8px", marginBottom: "8px" }}>
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          style={{
            flex: 1,
            padding: "10px",
            border: error ? "2px solid #ff4444" : "1px solid #ddd",
            borderRadius: "4px",
            fontFamily: "monospace",
            fontSize: "12px"
          }}
        />

        {onUpload && (
          <label
            onMouseEnter={() => setIsHoveringUpload(true)}
            onMouseLeave={() => setIsHoveringUpload(false)}
            style={{
              padding: "10px 16px",
              backgroundColor: isHoveringUpload ? "#7a1570" : "#8F1A95",
              color: "#FFFFFF",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "500",
              transition: "background-color 0.2s"
            }}
          >
            Upload
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = (event) => {
                    const url = event.target?.result as string;
                    onChange(url);
                    onUpload(url, file.name);
                  };
                  reader.readAsDataURL(file);
                }
              }}
              style={{ display: "none" }}
            />
          </label>
        )}
      </div>

      {error && (
        <div style={{ color: "#ff4444", fontSize: "12px", marginTop: "4px" }}>
          {error}
        </div>
      )}

      {value && (
        <div style={{ marginTop: "8px", maxWidth: "100%" }}>
          <img
            src={value}
            alt="Preview"
            style={{
              maxWidth: "100%",
              maxHeight: "150px",
              borderRadius: "4px",
              border: "1px solid #ddd"
            }}
            onError={() => console.error("Failed to load image")}
          />
        </div>
      )}
    </div>
  );
}

