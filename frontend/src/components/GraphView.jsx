import React, { useRef, useEffect, useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, ExternalLink } from 'lucide-react';

export default function GraphView({ target, targetType, findings = [] }) {
  const canvasRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  const relevantFindings = findings.filter(
    (f) => f.status === 'found' || f.status === 'info'
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    ctx.save();
    ctx.translate(width / 2 + offset.x, height / 2 + offset.y);
    ctx.scale(zoom, zoom);

    // Minimal grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = -width; x < width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, -height);
      ctx.lineTo(x, height);
      ctx.stroke();
    }
    for (let y = -height; y < height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(-width, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    const centerX = 0;
    const centerY = 0;
    const radius = Math.min(width, height) * 0.35;
    const count = relevantFindings.length;

    // Draw Connections & Peripheral Nodes
    relevantFindings.forEach((f, idx) => {
      const angle = (idx / (count || 1)) * 2 * Math.PI;
      const nx = Math.cos(angle) * radius;
      const ny = Math.sin(angle) * radius;

      // Clean white connection line
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(nx, ny);
      ctx.strokeStyle = f.status === 'found' ? 'rgba(255, 255, 255, 0.25)' : 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // Peripheral node circle
      ctx.beginPath();
      ctx.arc(nx, ny, 14, 0, 2 * Math.PI);
      ctx.fillStyle = f.status === 'found' ? '#18181b' : '#09090b';
      ctx.fill();
      ctx.strokeStyle = f.status === 'found' ? '#ffffff' : '#52525b';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Node Label
      ctx.fillStyle = '#e4e4e7';
      ctx.font = '11px JetBrains Mono, monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const label = f.source || 'Item';
      ctx.fillText(label, nx, ny + 24);
    });

    // Draw Central Target Node (High-Contrast White)
    ctx.shadowColor = 'rgba(255, 255, 255, 0.3)';
    ctx.shadowBlur = 15;

    ctx.beginPath();
    ctx.arc(centerX, centerY, 30, 0, 2 * Math.PI);
    ctx.fillStyle = '#ffffff';
    ctx.fill();
    ctx.strokeStyle = '#27272a';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.shadowBlur = 0;

    // Center Node Label
    ctx.fillStyle = '#09090b';
    ctx.font = 'bold 11px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const displayTarget = target ? (target.length > 9 ? target.slice(0, 8) + '…' : target) : 'TARGET';
    ctx.fillText(displayTarget, centerX, centerY);

    ctx.restore();
  }, [relevantFindings, target, zoom, offset]);

  const handleCanvasClick = (e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left - canvas.width / 2 - offset.x;
    const mouseY = e.clientY - rect.top - canvas.height / 2 - offset.y;

    const scaledX = mouseX / zoom;
    const scaledY = mouseY / zoom;

    const radius = Math.min(canvas.width, canvas.height) * 0.35;
    const count = relevantFindings.length;

    let clicked = null;
    relevantFindings.forEach((f, idx) => {
      const angle = (idx / (count || 1)) * 2 * Math.PI;
      const nx = Math.cos(angle) * radius;
      const ny = Math.sin(angle) * radius;
      const dist = Math.hypot(scaledX - nx, scaledY - ny);
      if (dist <= 18) {
        clicked = f;
      }
    });

    setSelectedNode(clicked);
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setOffset({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => setIsDragging(false);

  return (
    <div className="w-full max-w-4xl mx-auto mono-panel rounded-xl p-4 border border-white/10 relative overflow-hidden">
      {/* Graph Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-xs uppercase tracking-wider text-white font-mono">
            Relationship Graph
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded bg-zinc-800 text-zinc-300 font-mono border border-white/10">
            {relevantFindings.length} Nodes
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.2, 2.5))}
            className="p-1.5 rounded bg-zinc-900 border border-white/10 text-zinc-300 hover:text-white"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}
            className="p-1.5 rounded bg-zinc-900 border border-white/10 text-zinc-300 hover:text-white"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => { setZoom(1); setOffset({ x: 0, y: 0 }); }}
            className="p-1.5 rounded bg-zinc-900 border border-white/10 text-zinc-300 hover:text-white"
            title="Reset"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Canvas Viewport */}
      <div className="relative w-full h-[500px] bg-[#09090b] rounded-lg overflow-hidden border border-white/10 cursor-grab active:cursor-grabbing">
        <canvas
          ref={canvasRef}
          width={800}
          height={500}
          onClick={handleCanvasClick}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          className="w-full h-full block"
        />

        {/* Selected Node Details Floating Popup */}
        {selectedNode && (
          <div className="absolute bottom-4 left-4 right-4 sm:right-auto sm:w-80 bg-zinc-950/95 backdrop-blur-md p-4 rounded-lg border border-white/20 shadow-2xl animate-fadeIn">
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-bold text-xs text-white font-mono">{selectedNode.source}</span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-zinc-500 hover:text-white text-xs"
              >
                ✕
              </button>
            </div>
            <div className="text-xs text-zinc-200 font-medium mb-1">
              {selectedNode.title || 'Connected Entity'}
            </div>
            <p className="text-[11px] text-zinc-400 mb-2 font-mono">
              {selectedNode.description || 'No description available.'}
            </p>
            {selectedNode.url && (
              <a
                href={selectedNode.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs text-white hover:underline font-mono"
              >
                <span>Visit Source</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        )}
      </div>

      <div className="mt-2 text-center text-[11px] text-zinc-500 font-mono">
        Drag to navigate • Click nodes to view details
      </div>
    </div>
  );
}
