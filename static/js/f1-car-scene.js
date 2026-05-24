/**
 * ═══════════════════════════════════════════════════════════════════════
 * F1 CAR 3D SCENE MANAGER
 * Interactive animated Red Bull RB19 that reacts to page navigation
 * ═══════════════════════════════════════════════════════════════════════
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';

class F1CarScene {
    constructor() {
        this.container = null;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.car = null;
        this.wheels = [];
        this.mixer = null;
        this.clock = new THREE.Clock();
        this.currentPage = this.detectCurrentPage();
        this.isTransitioning = false;
        this.wheelRotation = 0;
        this.carVelocity = new THREE.Vector3();
        this.targetPosition = new THREE.Vector3();
        this.targetRotation = new THREE.Euler();
        
        // Animation state
        this.animationState = {
            speed: 0,
            drift: 0,
            suspension: 0,
            cameraShake: 0
        };

        // Page-specific configurations
        this.pageConfigs = {
            '/': {
                position: new THREE.Vector3(0, -0.5, 0),
                rotation: new THREE.Euler(0, Math.PI * 0.15, 0),
                cameraPos: new THREE.Vector3(4, 2, 5),
                lightColor: 0xffffff,
                animation: 'idle'
            },
            '/binary-classification': {
                position: new THREE.Vector3(-3, -0.5, 1),
                rotation: new THREE.Euler(0, Math.PI * 0.4, 0),
                cameraPos: new THREE.Vector3(3, 2.5, 6),
                lightColor: 0xffd700,
                animation: 'accelerate'
            },
            '/multiclass-classification': {
                position: new THREE.Vector3(2, -0.5, -1),
                rotation: new THREE.Euler(0, -Math.PI * 0.3, 0),
                cameraPos: new THREE.Vector3(5, 2, 4),
                lightColor: 0x00ffff,
                animation: 'drift'
            },
            '/regression-position': {
                position: new THREE.Vector3(-2, -0.5, -2),
                rotation: new THREE.Euler(0, Math.PI * 0.6, 0),
                cameraPos: new THREE.Vector3(6, 3, 3),
                lightColor: 0xff6600,
                animation: 'speed'
            },
            '/clustering': {
                position: new THREE.Vector3(1, -0.5, 2),
                rotation: new THREE.Euler(0, -Math.PI * 0.5, 0),
                cameraPos: new THREE.Vector3(4, 2, 6),
                lightColor: 0xff00ff,
                animation: 'rotate'
            },
            '/race-prediction': {
                position: new THREE.Vector3(0, -0.5, -1),
                rotation: new THREE.Euler(0, Math.PI, 0),
                cameraPos: new THREE.Vector3(3, 2, 7),
                lightColor: 0xff0000,
                animation: 'race'
            }
        };
    }

    detectCurrentPage() {
        const path = window.location.pathname;
        return path === '/' ? '/' : path;
    }

    async init() {
        // Create container
        this.container = document.createElement('div');
        this.container.id = 'f1-car-container';
        this.container.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 0;
            opacity: 0;
            transition: opacity 1s ease-out;
        `;
        document.body.insertBefore(this.container, document.body.firstChild);

        // Setup Three.js scene
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.Fog(0x667eea, 10, 50);

        // Camera
        this.camera = new THREE.PerspectiveCamera(
            45,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        const config = this.pageConfigs[this.currentPage] || this.pageConfigs['/'];
        this.camera.position.copy(config.cameraPos);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true, 
            alpha: true,
            powerPreference: 'high-performance'
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.2;
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;
        this.container.appendChild(this.renderer.domElement);

        // Lights
        this.setupLights();

        // Load car model
        await this.loadCar();

        // Start animation loop
        this.animate();

        // Fade in
        setTimeout(() => {
            this.container.style.opacity = '0.85';
        }, 100);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());

        // Listen for page changes
        this.setupNavigationListeners();
    }

    setupLights() {
        // Ambient light
        const ambient = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambient);

        // Main directional light (sun)
        this.mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
        this.mainLight.position.set(5, 10, 5);
        this.mainLight.castShadow = true;
        this.mainLight.shadow.mapSize.width = 2048;
        this.mainLight.shadow.mapSize.height = 2048;
        this.mainLight.shadow.camera.near = 0.5;
        this.mainLight.shadow.camera.far = 50;
        this.scene.add(this.mainLight);

        // Rim lights for dramatic effect
        const rimLight1 = new THREE.SpotLight(0xff0000, 0.8);
        rimLight1.position.set(-5, 3, -5);
        rimLight1.angle = Math.PI / 6;
        rimLight1.penumbra = 0.5;
        this.scene.add(rimLight1);

        const rimLight2 = new THREE.SpotLight(0x0066ff, 0.6);
        rimLight2.position.set(5, 3, -5);
        rimLight2.angle = Math.PI / 6;
        rimLight2.penumbra = 0.5;
        this.scene.add(rimLight2);

        // Dynamic accent light (changes per page)
        this.accentLight = new THREE.PointLight(0xffffff, 1, 20);
        this.accentLight.position.set(0, 2, 3);
        this.scene.add(this.accentLight);

        // Ground plane for shadows
        const groundGeometry = new THREE.PlaneGeometry(50, 50);
        const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.15 });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.5;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }

    async loadCar() {
        const loader = new GLTFLoader();
        
        return new Promise((resolve, reject) => {
            loader.load(
                '/static/f1_model/source/oracle_redbull_rb19.glb',
                (gltf) => {
                    this.car = gltf.scene;
                    
                    // Scale and position
                    this.car.scale.set(0.8, 0.8, 0.8);
                    const config = this.pageConfigs[this.currentPage] || this.pageConfigs['/'];
                    this.car.position.copy(config.position);
                    this.car.rotation.copy(config.rotation);

                    // Enable shadows
                    this.car.traverse((child) => {
                        if (child.isMesh) {
                            child.castShadow = true;
                            child.receiveShadow = true;
                            
                            // Enhance materials
                            if (child.material) {
                                child.material.envMapIntensity = 1.5;
                                child.material.metalness = Math.min(child.material.metalness * 1.2, 1);
                                child.material.roughness = Math.max(child.material.roughness * 0.8, 0.1);
                            }

                            // Identify wheels for animation
                            if (child.name.toLowerCase().includes('wheel') || 
                                child.name.toLowerCase().includes('tire')) {
                                this.wheels.push(child);
                            }
                        }
                    });

                    this.scene.add(this.car);
                    
                    // Setup animation mixer if animations exist
                    if (gltf.animations && gltf.animations.length > 0) {
                        this.mixer = new THREE.AnimationMixer(this.car);
                        gltf.animations.forEach((clip) => {
                            this.mixer.clipAction(clip).play();
                        });
                    }

                    console.log('✓ F1 car loaded successfully');
                    resolve();
                },
                (progress) => {
                    const percent = (progress.loaded / progress.total * 100).toFixed(0);
                    console.log(`Loading F1 car: ${percent}%`);
                },
                (error) => {
                    console.error('Error loading F1 car:', error);
                    reject(error);
                }
            );
        });
    }

    animateToPage(targetPage) {
        if (this.isTransitioning || !this.car) return;
        
        const config = this.pageConfigs[targetPage] || this.pageConfigs['/'];
        this.isTransitioning = true;
        this.currentPage = targetPage;

        // Set target transforms
        this.targetPosition.copy(config.position);
        this.targetRotation.copy(config.rotation);

        // Update accent light color
        this.accentLight.color.setHex(config.lightColor);

        // Trigger animation based on page
        this.triggerPageAnimation(config.animation);

        // Smooth camera movement
        this.animateCamera(config.cameraPos);

        // Reset transition flag after animation
        setTimeout(() => {
            this.isTransitioning = false;
        }, 2000);
    }

    triggerPageAnimation(animationType) {
        switch (animationType) {
            case 'accelerate':
                this.animationState.speed = 1;
                setTimeout(() => { this.animationState.speed = 0; }, 1500);
                break;
            case 'drift':
                this.animationState.drift = 1;
                setTimeout(() => { this.animationState.drift = 0; }, 1800);
                break;
            case 'speed':
                this.animationState.speed = 1.5;
                setTimeout(() => { this.animationState.speed = 0; }, 1200);
                break;
            case 'rotate':
                // Full 360 rotation
                this.targetRotation.y += Math.PI * 2;
                break;
            case 'race':
                this.animationState.speed = 2;
                this.animationState.cameraShake = 0.5;
                setTimeout(() => { 
                    this.animationState.speed = 0;
                    this.animationState.cameraShake = 0;
                }, 2000);
                break;
            default:
                // idle
                break;
        }
    }

    animateCamera(targetPos) {
        const startPos = this.camera.position.clone();
        const duration = 1500;
        const startTime = Date.now();

        const updateCamera = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = this.easeInOutCubic(progress);

            this.camera.position.lerpVectors(startPos, targetPos, eased);
            this.camera.lookAt(0, 0, 0);

            if (progress < 1) {
                requestAnimationFrame(updateCamera);
            }
        };

        updateCamera();
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const delta = this.clock.getDelta();

        // Update mixer
        if (this.mixer) {
            this.mixer.update(delta);
        }

        if (this.car) {
            // Smooth position interpolation
            this.car.position.lerp(this.targetPosition, 0.05);
            
            // Smooth rotation interpolation
            this.car.rotation.x += (this.targetRotation.x - this.car.rotation.x) * 0.05;
            this.car.rotation.y += (this.targetRotation.y - this.car.rotation.y) * 0.05;
            this.car.rotation.z += (this.targetRotation.z - this.car.rotation.z) * 0.05;

            // Wheel rotation based on speed
            if (this.animationState.speed > 0) {
                this.wheelRotation += delta * this.animationState.speed * 15;
                this.wheels.forEach(wheel => {
                    wheel.rotation.x = this.wheelRotation;
                });
            }

            // Drift effect (lean into turn)
            if (this.animationState.drift > 0) {
                const driftAngle = Math.sin(Date.now() * 0.003) * 0.1 * this.animationState.drift;
                this.car.rotation.z = driftAngle;
            }

            // Suspension bounce (subtle)
            const bounce = Math.sin(Date.now() * 0.005) * 0.02;
            this.car.position.y = this.targetPosition.y + bounce;

            // Camera shake during high speed
            if (this.animationState.cameraShake > 0) {
                const shake = this.animationState.cameraShake;
                this.camera.position.x += (Math.random() - 0.5) * shake * 0.1;
                this.camera.position.y += (Math.random() - 0.5) * shake * 0.1;
            }

            // Idle floating animation
            if (!this.isTransitioning && this.animationState.speed === 0) {
                const float = Math.sin(Date.now() * 0.001) * 0.05;
                this.car.position.y = this.targetPosition.y + float;
            }
        }

        // Rotate accent light around car
        const time = Date.now() * 0.0005;
        this.accentLight.position.x = Math.cos(time) * 4;
        this.accentLight.position.z = Math.sin(time) * 4;

        this.renderer.render(this.scene, this.camera);
    }

    setupNavigationListeners() {
        // Intercept all navigation clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href]');
            if (!link) return;

            const href = link.getAttribute('href');
            if (!href || href.startsWith('#') || href.startsWith('http')) return;

            // Trigger car animation before navigation
            this.animateToPage(href);
        });

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            const newPage = this.detectCurrentPage();
            this.animateToPage(newPage);
        });
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    easeInOutCubic(t) {
        return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
    }

    // Public API
    destroy() {
        if (this.renderer) {
            this.renderer.dispose();
        }
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.f1CarScene = new F1CarScene();
        window.f1CarScene.init().catch(err => {
            console.warn('F1 car scene initialization failed:', err);
        });
    });
} else {
    window.f1CarScene = new F1CarScene();
    window.f1CarScene.init().catch(err => {
        console.warn('F1 car scene initialization failed:', err);
    });
}

export default F1CarScene;
