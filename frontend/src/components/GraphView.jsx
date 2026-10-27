import React, { useRef, useEffect, useState } from 'react';
import { ZoomIn, ZoomOut, Maximize2, RotateCcw, Info, ExternalLink } from 'lucide-react';

export default function GraphView({ target, targetType, findings = [] }) {
  const canvasRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Filter only found or interesting findings
  const relevantFindings = findings.filter(
    (f) => f.status === 'found' || f.status === 'info'
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear
    ctx.clearRect(0, 0, width, height);

    ctx.save();
    ctx.translate(width / 2 + offset.x, height / 2 + offset.y);
    ctx.scale(zoom, zoom);

    // Draw grid
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.05)';
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

      // Draw connection edge line
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(nx, ny);
      ctx.strokeStyle = f.status === 'found' ? 'rgba(16, 185, 129, 0.4)' : 'rgba(56, 189, 248, 0.3)';
      ctx.lineWidth = 1.5;
      ctx.stroke();

      // Node shadow
      ctx.shadowColor = f.status === 'found' ? 'rgba(16, 185, 129, 0.6)' : 'rgba(56, 189, 248, 0.5)';
      ctx.shadowBlur = 10;

      // Draw peripheral node circle
      ctx.beginPath();
      ctx.arc(nx, ny, 16, 0, 2 * Math.PI);
      ctx.fillStyle = f.status === 'found' ? '#064e3b' : '#0c4a6e';
      ctx.fill();
      ctx.strokeStyle = f.status === 'found' ? '#10b981' : '#38bdf8';
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.shadowBlur = 0; // reset shadow

      // Peripheral Label
      ctx.fillStyle = '#f1f5f9';
      ctx.font = '11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      const label = f.source || 'Item';
      ctx.fillText(label, nx, ny + 28);
    });

    // Draw Central Target Node
    ctx.shadowColor = 'rgba(56, 189, 248, 0.8)';
    ctx.shadowBlur = 20;

    ctx.beginPath();
    ctx.arc(centerX, centerY, 32, 0, 2 * Math.PI);
    ctx.fillStyle = '#0f172a';
    ctx.fill();
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 3;
    ctx.stroke();

    ctx.shadowBlur = 0;

    // Center Node Label
    ctx.fillStyle = '#38bdf8';
    ctx.font = 'bold 12px JetBrains Mono, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const displayTarget = target ? (target.length > 10 ? target.slice(0, 9) + '…' : target) : 'TARGET';
    ctx.fillText(displayTarget, centerX, centerY);

    ctx.restore();
  }, [relevantFindings, target, zoom, offset]);

  // Click on canvas to select node
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
      if (dist <= 20) {
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
    <div className="w-full max-w-4xl mx-auto glass-panel rounded-2xl p-4 border border-cyan-500/20 relative overflow-hidden">
      {/* Graph Toolbar */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-sm text-slate-200">Investigation Relationship Graph</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-800 text-cyan-400 font-mono">
            {relevantFindings.length} active nodes
          </span>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => setZoom((z) => Math.min(z + 0.2, 2.5))}
            className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
            title="Zoom In"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={() => setZoom((z) => Math.max(z - 0.2, 0.4))}
            className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
            title="Zoom Out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={() => { setZoom(1); setOffset({ x: 0, y: 0 }); }}
            className="p-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white"
            title="Reset View"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Canvas Viewport */}
      <div className="relative w-full h-[500px] bg-[#070b12] rounded-xl overflow-hidden border border-slate-800 cursor-grab active:cursor-grabbing">
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
          <div className="absolute bottom-4 left-4 right-4 sm:right-auto sm:w-80 bg-slate-900/95 backdrop-blur-md p-4 rounded-xl border border-cyan-500/40 shadow-2xl animate-fadeIn">
            <div className="flex items-center justify-between mb-1.5">
              <span className="font-bold text-sm text-cyan-300">{selectedNode.source}</span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-slate-200 text-xs"
              >
                ✕
              </button>
            </div>
            <div className="text-xs text-slate-200 font-semibold mb-1">
              {selectedNode.title || 'Connected Entity'}
            </div>
            <p className="text-[11px] text-slate-400 mb-2">
              {selectedNode.description || 'No additional summary available.'}
            </p>
            {selectedNode.url && (
              <a
                href={selectedNode.url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-xs text-cyan-400 hover:underline font-mono"
              >
                <span>Visit Source Profile</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            )}
          </div>
        )}
      </div>

      <div className="mt-2 text-center text-xs text-slate-500 font-mono">
        Drag to pan • Click any node to inspect relationship • Mouse wheel / buttons to zoom
      </div>
    </div>
  );
}
