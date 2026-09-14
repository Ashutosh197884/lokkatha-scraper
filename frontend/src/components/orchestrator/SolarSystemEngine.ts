import * as THREE from "three";
import { DataSource } from "../../types/source";
import {
  createPlanetTexture,
  createPlanetaryRingTexture,
  createSunTexture,
} from "./textureUtils";

export interface Planet3DNode {
  source: DataSource;
  group: THREE.Group;
  mesh: THREE.Mesh;
  atmosphereMesh: THREE.Mesh;
  ringMesh?: THREE.Mesh;
  orbitLine: THREE.LineLoop;
  currentAngle: number;
}

export interface DataParticle {
  mesh: THREE.Mesh;
  startPos: THREE.Vector3;
  targetPos: THREE.Vector3;
  controlPos: THREE.Vector3;
  progress: number;
  speed: number;
  color: string;
  sourceId: string;
}

export class SolarSystemEngine {
  public container: HTMLElement;
  public scene: THREE.Scene;
  public camera: THREE.PerspectiveCamera;
  public renderer: THREE.WebGLRenderer;
  
  private sunGroup: THREE.Group;
  private sunMesh: THREE.Mesh;
  private sunCoronaMesh: THREE.Mesh;
  private sunOuterGlowMesh: THREE.Mesh;
  private sunLight: THREE.PointLight;
  private ambientLight: THREE.AmbientLight;
  
  private starsParticles: THREE.Points;
  private planetsMap: Map<string, Planet3DNode> = new Map();
  private dataParticles: DataParticle[] = [];
  private particleGeo: THREE.SphereGeometry;
  
  // Animation & Camera State
  private isDestroyed = false;
  private animationFrameId: number | null = null;
  private clock = new THREE.Clock();
  public simulationSpeed = 1.0;
  
  // Camera controls state
  private isMouseDown = false;
  private mouseX = 0;
  private mouseY = 0;
  private targetCameraTheta = 0.35;
  private targetCameraPhi = 1.15;
  private targetCameraRadius = 680;
  private currentCameraTheta = 0.35;
  private currentCameraPhi = 1.15;
  private currentCameraRadius = 680;
  private targetLookAt = new THREE.Vector3(0, 0, 0);
  private currentLookAt = new THREE.Vector3(0, 0, 0);
  
  private focusedSourceId: string | null = null;
  private raycaster = new THREE.Raycaster();
  private mouseVec = new THREE.Vector2();
  
  // Callbacks
  public onPlanetClick?: (source: DataSource) => void;
  public onPlanetHover?: (source: DataSource | null, screenPos: { x: number; y: number } | null) => void;
  public onBackgroundClick?: () => void;

  constructor(container: HTMLElement) {
    this.container = container;
    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    // 1. Scene setup
    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x04060c, 0.0006);

    // 2. Camera setup
    this.camera = new THREE.PerspectiveCamera(45, width / height, 1, 4000);
    this.updateCameraPosition();

    // 3. Renderer setup
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      powerPreference: "high-performance",
      alpha: true,
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;
    container.appendChild(this.renderer.domElement);

    // 4. Lights
    this.ambientLight = new THREE.AmbientLight(0x223048, 0.8);
    this.scene.add(this.ambientLight);

    this.sunLight = new THREE.PointLight(0xffaa22, 2.5, 1800, 1.2);
    this.sunLight.position.set(0, 0, 0);
    this.scene.add(this.sunLight);

    // 5. Starfield & Cosmic Dust
    this.starsParticles = this.createStarfield();
    this.scene.add(this.starsParticles);

    // 6. Central Sun Core
    this.sunGroup = new THREE.Group();
    const { sunMesh, coronaMesh, glowMesh } = this.createSunCore();
    this.sunMesh = sunMesh;
    this.sunCoronaMesh = coronaMesh;
    this.sunOuterGlowMesh = glowMesh;
    this.sunGroup.add(sunMesh);
    this.sunGroup.add(coronaMesh);
    this.sunGroup.add(glowMesh);
    this.scene.add(this.sunGroup);

    // 7. Particle Geometry template
    this.particleGeo = new THREE.SphereGeometry(1.2, 8, 8);

    // 8. Event listeners
    this.bindEvents();

    // 9. Start render loop
    this.animate();
  }

  private createStarfield(): THREE.Points {
    const starCount = 2800;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(starCount * 3);
    const colors = new Float32Array(starCount * 3);

    const colorPalette = [
      new THREE.Color(0xffffff),
      new THREE.Color(0x93c5fd),
      new THREE.Color(0xc084fc),
      new THREE.Color(0xfde047),
      new THREE.Color(0x38bdf8),
    ];

    for (let i = 0; i < starCount; i++) {
      const radius = 900 + Math.random() * 1200;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = (radius * Math.sin(phi) * Math.sin(theta)) * 0.7; // slight galactic disc flattening
      positions[i * 3 + 2] = radius * Math.cos(phi);

      const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
      const brightness = 0.4 + Math.random() * 0.6;
      colors[i * 3] = color.r * brightness;
      colors[i * 3 + 1] = color.g * brightness;
      colors[i * 3 + 2] = color.b * brightness;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 2.2,
      vertexColors: true,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending,
    });

    return new THREE.Points(geometry, material);
  }

  private createSunCore(): { sunMesh: THREE.Mesh; coronaMesh: THREE.Mesh; glowMesh: THREE.Mesh } {
    const sunTexture = createSunTexture();
    
    // Core sphere
    const sunGeo = new THREE.SphereGeometry(22, 64, 64);
    const sunMat = new THREE.MeshBasicMaterial({
      map: sunTexture,
      color: 0xffe082,
    });
    const sunMesh = new THREE.Mesh(sunGeo, sunMat);

    // Inner pulsating corona layer
    const coronaGeo = new THREE.SphereGeometry(25.5, 48, 48);
    const coronaMat = new THREE.MeshBasicMaterial({
      color: 0xff9900,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
    });
    const coronaMesh = new THREE.Mesh(coronaGeo, coronaMat);

    // Outer luminous solar atmosphere glow
    const glowGeo = new THREE.SphereGeometry(32, 32, 32);
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0xff6600,
      transparent: true,
      opacity: 0.22,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
    });
    const glowMesh = new THREE.Mesh(glowGeo, glowMat);

    return { sunMesh, coronaMesh, glowMesh };
  }

  public setSources(sources: DataSource[]): void {
    const currentIds = new Set(sources.map((s) => s.id));

    // Remove deleted planets
    for (const [id, node] of this.planetsMap.entries()) {
      if (!currentIds.has(id)) {
        this.scene.remove(node.group);
        this.scene.remove(node.orbitLine);
        this.planetsMap.delete(id);
      }
    }

    // Add or update planets
    for (const source of sources) {
      if (this.planetsMap.has(source.id)) {
        const node = this.planetsMap.get(source.id)!;
        node.source = source;
        this.updatePlanetAppearance(node);
      } else {
        this.createPlanet(source);
      }
    }
  }

  private createPlanet(source: DataSource): void {
    const group = new THREE.Group();

    // 1. Planet mesh
    const radius = source.visual.radius || 5;
    const geo = new THREE.SphereGeometry(radius, 32, 32);
    const texture = createPlanetTexture(source.visual.theme, source.visual.color);
    
    const mat = new THREE.MeshStandardMaterial({
      map: texture,
      roughness: 0.7,
      metalness: 0.1,
      emissive: new THREE.Color(source.visual.color),
      emissiveIntensity: 0.15,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.rotation.z = THREE.MathUtils.degToRad(source.rotation.tilt || 15);
    (mesh as any).userData = { sourceId: source.id };
    group.add(mesh);

    // 2. Planet atmosphere glow halo
    const atmoGeo = new THREE.SphereGeometry(radius * 1.25, 24, 24);
    const atmoMat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(source.visual.glowColor),
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending,
      side: THREE.BackSide,
    });
    const atmosphereMesh = new THREE.Mesh(atmoGeo, atmoMat);
    group.add(atmosphereMesh);

    // 3. Planetary rings if applicable
    let ringMesh: THREE.Mesh | undefined;
    if (source.visual.hasRings) {
      const innerRadius = radius * 1.4;
      const outerRadius = radius * (source.visual.ringRadius ? source.visual.ringRadius / radius : 2.4);
      const ringGeo = new THREE.RingGeometry(innerRadius, outerRadius, 48);
      const ringTexture = createPlanetaryRingTexture(source.visual.ringColor);
      const ringMat = new THREE.MeshBasicMaterial({
        map: ringTexture,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.8,
        blending: THREE.AdditiveBlending,
      });
      ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2 + 0.2;
      group.add(ringMesh);
    }

    // 4. Orbital Ring line loop in space
    const orbitLine = this.createOrbitPath(source);
    this.scene.add(orbitLine);
    this.scene.add(group);

    const node: Planet3DNode = {
      source,
      group,
      mesh,
      atmosphereMesh,
      ringMesh,
      orbitLine,
      currentAngle: source.orbit.angle,
    };

    this.planetsMap.set(source.id, node);
    this.updatePlanetPosition(node);
  }

  private createOrbitPath(source: DataSource): THREE.LineLoop {
    const segments = 128;
    const points: THREE.Vector3[] = [];
    const r = source.orbit.radius;
    const inc = source.orbit.inclination || 0;
    const ecc = source.orbit.eccentricity || 1.0;

    for (let i = 0; i <= segments; i++) {
      const theta = (i / segments) * Math.PI * 2;
      const x = r * Math.cos(theta) * ecc;
      const z = r * Math.sin(theta);
      const y = Math.sin(theta) * Math.sin(inc) * (r * 0.25);
      points.push(new THREE.Vector3(x, y, z));
    }

    const geo = new THREE.BufferGeometry().setFromPoints(points);
    const isActive = source.status === "active" || source.status === "fetching" || source.status === "analyzing";
    
    const mat = new THREE.LineBasicMaterial({
      color: isActive ? new THREE.Color(source.visual.glowColor) : new THREE.Color(0x1e293b),
      transparent: true,
      opacity: isActive ? 0.65 : 0.2,
      blending: THREE.AdditiveBlending,
    });

    return new THREE.LineLoop(geo, mat);
  }

  private updatePlanetAppearance(node: Planet3DNode): void {
    const s = node.source;
    const isActive = s.status === "active" || s.status === "fetching" || s.status === "analyzing";
    const isError = s.status === "error";

    // Atmosphere opacity
    const atmoMat = node.atmosphereMesh.material as THREE.MeshBasicMaterial;
    if (isError) {
      atmoMat.color.setHex(0xef4444);
      atmoMat.opacity = 0.55;
    } else if (isActive) {
      atmoMat.color.set(s.visual.glowColor);
      atmoMat.opacity = 0.45;
    } else {
      atmoMat.color.set(s.visual.glowColor);
      atmoMat.opacity = 0.15;
    }

    // Orbit line luminosity
    const orbitMat = node.orbitLine.material as THREE.LineBasicMaterial;
    if (isActive) {
      orbitMat.color.set(s.visual.glowColor);
      orbitMat.opacity = 0.7;
    } else {
      orbitMat.color.setHex(0x1e293b);
      orbitMat.opacity = 0.2;
    }
  }

  private updatePlanetPosition(node: Planet3DNode): void {
    const r = node.source.orbit.radius;
    const angle = node.currentAngle;
    const inc = node.source.orbit.inclination || 0;
    const ecc = node.source.orbit.eccentricity || 1.0;

    const x = r * Math.cos(angle) * ecc;
    const z = r * Math.sin(angle);
    const y = Math.sin(angle) * Math.sin(inc) * (r * 0.25);

    node.group.position.set(x, y, z);
  }

  public focusOnPlanet(sourceId: string): void {
    this.focusedSourceId = sourceId;
    const node = this.planetsMap.get(sourceId);
    if (node) {
      this.targetCameraRadius = 140;
    }
  }

  public resetView(): void {
    this.focusedSourceId = null;
    this.targetCameraTheta = 0.35;
    this.targetCameraPhi = 1.15;
    this.targetCameraRadius = 680;
    this.targetLookAt.set(0, 0, 0);
  }

  public getPlanetScreenPosition(sourceId: string): { x: number; y: number; visible: boolean } | null {
    const node = this.planetsMap.get(sourceId);
    if (!node) return null;

    const pos = new THREE.Vector3();
    node.group.getWorldPosition(pos);
    pos.project(this.camera);

    const isBehind = pos.z > 1;
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;

    return {
      x: ((pos.x + 1) * width) / 2,
      y: ((-pos.y + 1) * height) / 2,
      visible: !isBehind,
    };
  }

  public getSunScreenPosition(): { x: number; y: number } {
    const pos = new THREE.Vector3(0, 0, 0);
    pos.project(this.camera);
    const width = this.container.clientWidth;
    const height = this.container.clientHeight;
    return {
      x: ((pos.x + 1) * width) / 2,
      y: ((-pos.y + 1) * height) / 2,
    };
  }

  private spawnDataParticle(node: Planet3DNode): void {
    if (this.dataParticles.length >= 80) return;

    const startPos = new THREE.Vector3();
    node.group.getWorldPosition(startPos);

    const targetPos = new THREE.Vector3(0, 0, 0);
    // Add an arch control point for curved orbital trajectory
    const midX = (startPos.x + targetPos.x) / 2 + (Math.random() - 0.5) * 30;
    const midY = (startPos.y + targetPos.y) / 2 + 25 + Math.random() * 20;
    const midZ = (startPos.z + targetPos.z) / 2 + (Math.random() - 0.5) * 30;
    const controlPos = new THREE.Vector3(midX, midY, midZ);

    const mat = new THREE.MeshBasicMaterial({
      color: new THREE.Color(node.source.visual.glowColor),
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
    });
    const mesh = new THREE.Mesh(this.particleGeo, mat);
    mesh.position.copy(startPos);
    this.scene.add(mesh);

    this.dataParticles.push({
      mesh,
      startPos,
      targetPos,
      controlPos,
      progress: 0,
      speed: 0.008 + Math.random() * 0.006,
      color: node.source.visual.glowColor,
      sourceId: node.source.id,
    });
  }

  private updateDataParticles(delta: number): void {
    for (let i = this.dataParticles.length - 1; i >= 0; i--) {
      const p = this.dataParticles[i];
      p.progress += p.speed * this.simulationSpeed * (delta * 60);

      if (p.progress >= 1.0) {
        // Absorbed by Sun
        this.scene.remove(p.mesh);
        p.mesh.geometry.dispose();
        (p.mesh.material as THREE.Material).dispose();
        this.dataParticles.splice(i, 1);

        // Flash corona briefly
        const coronaMat = this.sunCoronaMesh.material as THREE.MeshBasicMaterial;
        coronaMat.opacity = Math.min(coronaMat.opacity + 0.04, 0.7);
      } else {
        // Quadratic Bezier interpolation
        const t = p.progress;
        const invT = 1 - t;
        p.mesh.position.x = invT * invT * p.startPos.x + 2 * invT * t * p.controlPos.x + t * t * p.targetPos.x;
        p.mesh.position.y = invT * invT * p.startPos.y + 2 * invT * t * p.controlPos.y + t * t * p.targetPos.y;
        p.mesh.position.z = invT * invT * p.startPos.z + 2 * invT * t * p.controlPos.z + t * t * p.targetPos.z;
        
        // Scale particle slightly as it accelerates
        const s = 1.0 + Math.sin(t * Math.PI) * 0.5;
        p.mesh.scale.set(s, s, s);
      }
    }
  }

  private bindEvents(): void {
    const el = this.container;

    const onMouseDown = (e: MouseEvent) => {
      this.isMouseDown = true;
      this.mouseX = e.clientX;
      this.mouseY = e.clientY;
    };

    const onMouseMove = (e: MouseEvent) => {
      if (this.isMouseDown) {
        const deltaX = e.clientX - this.mouseX;
        const deltaY = e.clientY - this.mouseY;
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;

        this.targetCameraTheta -= deltaX * 0.005;
        this.targetCameraPhi = Math.max(0.2, Math.min(Math.PI / 2 - 0.05, this.targetCameraPhi + deltaY * 0.005));
      }

      // Check hover
      const rect = el.getBoundingClientRect();
      this.mouseVec.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouseVec.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this.checkHover(e.clientX, e.clientY);
    };

    const onMouseUp = () => {
      this.isMouseDown = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      this.targetCameraRadius = Math.max(80, Math.min(1100, this.targetCameraRadius + e.deltaY * 0.6));
    };

    const onClick = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      this.mouseVec.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouseVec.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      this.raycaster.setFromCamera(this.mouseVec, this.camera);
      const meshes: THREE.Object3D[] = [];
      this.planetsMap.forEach((node) => meshes.push(node.mesh));

      const intersects = this.raycaster.intersectObjects(meshes, false);
      if (intersects.length > 0) {
        const hitMesh = intersects[0].object;
        const sourceId = hitMesh.userData.sourceId;
        const node = this.planetsMap.get(sourceId);
        if (node && this.onPlanetClick) {
          this.onPlanetClick(node.source);
        }
      } else {
        if (this.onBackgroundClick) {
          this.onBackgroundClick();
        }
      }
    };

    const onDblClick = () => {
      this.resetView();
    };

    el.addEventListener("mousedown", onMouseDown);
    window.addEventListener("mousemove", onMouseMove);
    window.addEventListener("mouseup", onMouseUp);
    el.addEventListener("wheel", onWheel, { passive: false });
    el.addEventListener("click", onClick);
    el.addEventListener("dblclick", onDblClick);
  }

  private checkHover(clientX: number, clientY: number): void {
    if (!this.onPlanetHover) return;

    this.raycaster.setFromCamera(this.mouseVec, this.camera);
    const meshes: THREE.Object3D[] = [];
    this.planetsMap.forEach((node) => meshes.push(node.mesh));

    const intersects = this.raycaster.intersectObjects(meshes, false);
    if (intersects.length > 0) {
      const sourceId = intersects[0].object.userData.sourceId;
      const node = this.planetsMap.get(sourceId);
      if (node) {
        this.onPlanetHover(node.source, { x: clientX, y: clientY });
        return;
      }
    }
    this.onPlanetHover(null, null);
  }

  private updateCameraPosition(): void {
    // Interpolate towards target lookAt
    if (this.focusedSourceId) {
      const node = this.planetsMap.get(this.focusedSourceId);
      if (node) {
        node.group.getWorldPosition(this.targetLookAt);
      }
    }

    this.currentLookAt.lerp(this.targetLookAt, 0.06);
    this.currentCameraTheta += (this.targetCameraTheta - this.currentCameraTheta) * 0.08;
    this.currentCameraPhi += (this.targetCameraPhi - this.currentCameraPhi) * 0.08;
    this.currentCameraRadius += (this.targetCameraRadius - this.currentCameraRadius) * 0.08;

    const x = this.currentLookAt.x + this.currentCameraRadius * Math.sin(this.currentCameraPhi) * Math.sin(this.currentCameraTheta);
    const y = this.currentLookAt.y + this.currentCameraRadius * Math.cos(this.currentCameraPhi);
    const z = this.currentLookAt.z + this.currentCameraRadius * Math.sin(this.currentCameraPhi) * Math.cos(this.currentCameraTheta);

    this.camera.position.set(x, y, z);
    this.camera.lookAt(this.currentLookAt);
  }

  public resize(width: number, height: number): void {
    if (!this.renderer || !this.camera) return;
    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);
  }

  private animate = (): void => {
    if (this.isDestroyed) return;
    this.animationFrameId = requestAnimationFrame(this.animate);

    const delta = this.clock.getDelta();
    const elapsedTime = this.clock.getElapsedTime();

    // 1. Sun surface & corona rotation + pulsing
    this.sunMesh.rotation.y += 0.003 * this.simulationSpeed;
    this.sunCoronaMesh.rotation.y -= 0.005 * this.simulationSpeed;
    this.sunCoronaMesh.rotation.z += 0.002 * this.simulationSpeed;

    const pulse = 1.0 + Math.sin(elapsedTime * 2.5) * 0.04;
    this.sunCoronaMesh.scale.set(pulse, pulse, pulse);
    const outerPulse = 1.0 + Math.cos(elapsedTime * 1.8) * 0.06;
    this.sunOuterGlowMesh.scale.set(outerPulse, outerPulse, outerPulse);

    // 2. Stars slow galactic drift
    if (this.starsParticles) {
      this.starsParticles.rotation.y += 0.00015 * this.simulationSpeed;
    }

    // 3. Planet orbital revolution & axial rotation
    for (const node of this.planetsMap.values()) {
      // Axial rotation
      node.mesh.rotation.y += node.source.rotation.speed * this.simulationSpeed * (delta * 60);

      // Orbital revolution
      if (this.simulationSpeed > 0) {
        node.currentAngle += node.source.orbit.speed * this.simulationSpeed * (delta * 60);
        this.updatePlanetPosition(node);
      }

      // Spawning data particles for active/fetching sources
      const s = node.source;
      if ((s.status === "fetching" || s.status === "active") && Math.random() < 0.12 * this.simulationSpeed) {
        this.spawnDataParticle(node);
      } else if (s.status === "analyzing" && Math.random() < 0.08 * this.simulationSpeed) {
        this.spawnDataParticle(node);
      }
    }

    // 4. Data particles movement
    this.updateDataParticles(delta);

    // 5. Camera interpolation
    this.updateCameraPosition();

    // 6. Render
    this.renderer.render(this.scene, this.camera);
  };

  public destroy(): void {
    this.isDestroyed = true;
    if (this.animationFrameId !== null) {
      cancelAnimationFrame(this.animationFrameId);
    }
    this.renderer.dispose();
    if (this.container.contains(this.renderer.domElement)) {
      this.container.removeChild(this.renderer.domElement);
    }
  }
}
