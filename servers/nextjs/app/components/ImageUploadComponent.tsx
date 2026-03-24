"use client";

import React, { useState, useCallback } from "react";

interface ImageUploadComponentProps {
  onImageUpload: (imageUrl: string, fileName: string) => void;
  onError: (error: string) => void;
  maxSize?: number;
  accept?: string;
  presentationId?: string;
}

export function ImageUploadComponent({
  onImageUpload,
  onError,
  maxSize = 5,
  accept = "image/jpeg,image/png,image/webp",
  presentationId
}: ImageUploadComponentProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const uploadFile = async (file: File) => {
    const validTypes = accept.split(",").map(t => t.trim());
    if (!validTypes.includes(file.type)) {
      onError(`Invalid file type. Allowed: ${accept}`);
      return;
    }

    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSize) {
      onError(`File too large. Maximum: ${maxSize}MB`);
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      if (presentationId) formData.append("presentation_id", presentationId);

      const response = await fetch("/api/v1/ppt/images/upload", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Upload failed");
      }

      const data = await response.json();
      onImageUpload(data.url, data.file_name);
    } catch (error) {
      onError(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      style={{
        border: dragActive ? "2px solid #8F1A95" : "2px dashed #8F1A95",
        borderRadius: "8px",
        padding: "24px",
        textAlign: "center",
        cursor: "pointer",
        backgroundColor: dragActive ? "rgba(143, 26, 149, 0.05)" : "transparent",
        transition: "all 0.3s ease"
      }}
    >
      <input
        type="file"
        accept={accept}
        onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])}
        disabled={isUploading}
        style={{ display: "none" }}
        id="image-upload-input"
      />
      <label htmlFor="image-upload-input" style={{ cursor: isUploading ? "not-allowed" : "pointer", display: "block" }}>
        <div style={{ fontSize: "14px", color: "#44546A", marginBottom: "8px" }}>
          {isUploading ? "Uploading..." : "Drag & drop or click to browse"}
        </div>
        <div style={{ fontSize: "12px", color: "#999" }}>
          JPEG, PNG, WebP • Max {maxSize}MB
        </div>
      </label>
    </div>
  );
}
