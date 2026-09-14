import * as THREE from "three";
import { PlanetTextureTheme } from "../../types/source";

/**
 * Creates high-detail procedural canvas textures for planets, rings, and the solar core
 * without external asset dependencies.
 */
export function createSunTexture(): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext("2d")!;

  // Solar gradient base
  const grad = ctx.createLinearGradient(0, 0, 0, canvas.height);
  grad.addColorStop(0, "#ff7700");
  grad.addColorStop(0.5, "#ffbb00");
  grad.addColorStop(1, "#ff5500");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Solar granulation & turbulent convection cells
  for (let i = 0; i < 4000; i++) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const r = 2 + Math.random() * 8;
    const brightness = Math.random();

    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fillStyle = brightness > 0.5 ? "rgba(255, 255, 200, 0.25)" : "rgba(180, 50, 0, 0.2)";
    ctx.fill();
  }

  // Solar magnetic filaments
  ctx.strokeStyle = "rgba(255, 230, 100, 0.15)";
  ctx.lineWidth = 3;
  for (let j = 0; j < 30; j++) {
    ctx.beginPath();
    let cx = Math.random() * canvas.width;
    let cy = Math.random() * canvas.height;
    ctx.moveTo(cx, cy);
    for (let k = 0; k < 6; k++) {
      cx += (Math.random() - 0.5) * 80;
      cy += (Math.random() - 0.5) * 40;
      ctx.lineTo(cx, cy);
    }
    ctx.stroke();
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  return texture;
}

export function createPlanetTexture(theme: PlanetTextureTheme, baseColor: string): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 256;
  const ctx = canvas.getContext("2d")!;

  ctx.fillStyle = baseColor;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  switch (theme) {
    case "emerald-gas": {
      // Atmospheric gas bands
      for (let y = 0; y < canvas.height; y += 4) {
        const shade = Math.sin(y * 0.1) * 0.3 + 0.5;
        ctx.fillStyle = `rgba(16, 185, 129, ${shade * 0.4})`;
        ctx.fillRect(0, y, canvas.width, 4);
      }
      // Storm swirls
      for (let s = 0; s < 5; s++) {
        const sx = Math.random() * canvas.width;
        const sy = Math.random() * canvas.height;
        ctx.beginPath();
        ctx.ellipse(sx, sy, 35, 15, 0.1, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(5, 150, 105, 0.6)";
        ctx.fill();
      }
      break;
    }

    case "terrestrial-earth": {
      // Deep blue ocean base
      ctx.fillStyle = "#1e3a8a";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      // Continents & land masses
      ctx.fillStyle = "#15803d";
      for (let c = 0; c < 12; c++) {
        const cx = Math.random() * canvas.width;
        const cy = 40 + Math.random() * (canvas.height - 80);
        ctx.beginPath();
        ctx.arc(cx, cy, 30 + Math.random() * 30, 0, Math.PI * 2);
        ctx.fill();
      }
      // White swirling clouds
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      for (let cl = 0; cl < 20; cl++) {
        const clx = Math.random() * canvas.width;
        const cly = Math.random() * canvas.height;
        ctx.fillRect(clx, cly, 60 + Math.random() * 80, 8 + Math.random() * 6);
      }
      break;
    }

    case "crimson-ringed": {
      // Mars/Jupiter reddish striations
      for (let y = 0; y < canvas.height; y += 6) {
        const band = (Math.sin(y * 0.08) + 1) * 0.5;
        ctx.fillStyle = `rgba(${180 + band * 60}, ${40 + band * 30}, ${30 + band * 20}, 0.8)`;
        ctx.fillRect(0, y, canvas.width, 6);
      }
      // Great red spot
      ctx.beginPath();
      ctx.ellipse(canvas.width * 0.6, canvas.height * 0.6, 45, 25, 0, 0, Math.PI * 2);
      ctx.fillStyle = "rgba(185, 28, 28, 0.9)";
      ctx.fill();
      break;
    }

    case "amethyst-ice": {
      // Crystalline purple striations
      for (let i = 0; i < canvas.height; i += 8) {
        ctx.fillStyle = `rgba(168, 85, 247, ${0.3 + Math.sin(i * 0.15) * 0.3})`;
        ctx.fillRect(0, i, canvas.width, 8);
      }
      ctx.fillStyle = "rgba(243, 232, 255, 0.25)";
      for (let p = 0; p < 300; p++) {
        ctx.fillRect(Math.random() * canvas.width, Math.random() * canvas.height, 3, 3);
      }
      break;
    }

    case "golden-dune": {
      // Desert dune waves
      for (let y = 0; y < canvas.height; y += 3) {
        const val = Math.sin(y * 0.05 + Math.sin(y * 0.02) * 2) * 0.5 + 0.5;
        ctx.fillStyle = `rgba(245, 158, 11, ${0.4 + val * 0.5})`;
        ctx.fillRect(0, y, canvas.width, 3);
      }
      break;
    }

    case "deep-ocean":
    case "electric-azure":
    default: {
      // Atmospheric depth gradients
      for (let y = 0; y < canvas.height; y += 4) {
        const alpha = Math.sin(y * 0.12) * 0.3 + 0.6;
        ctx.fillStyle = `rgba(56, 189, 248, ${alpha * 0.5})`;
        ctx.fillRect(0, y, canvas.width, 4);
      }
      break;
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = THREE.RepeatWrapping;
  texture.wrapT = THREE.ClampToEdgeWrapping;
  return texture;
}

export function createPlanetaryRingTexture(ringColor: string = "#fca5a5"): THREE.CanvasTexture {
  const canvas = document.createElement("canvas");
  canvas.width = 512;
  canvas.height = 64;
  const ctx = canvas.getContext("2d")!;

  const grad = ctx.createLinearGradient(0, 0, canvas.width, 0);
  grad.addColorStop(0, "rgba(0,0,0,0)");
  grad.addColorStop(0.15, "rgba(240, 150, 150, 0.1)");
  grad.addColorStop(0.4, "rgba(255, 200, 200, 0.7)");
  grad.addColorStop(0.65, "rgba(220, 100, 100, 0.4)");
  grad.addColorStop(0.85, "rgba(255, 180, 180, 0.6)");
  grad.addColorStop(1, "rgba(0,0,0,0)");

  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const texture = new THREE.CanvasTexture(canvas);
  return texture;
}
