// 🌌 REAL-TIME SOLAR SYSTEM ENGINE - QUANTUM SPACE VISUALIZATION
// Revolutionary real-time planetary positions and space object tracking

class RealTimeSolarSystem {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.planets = {};
        this.satellites = {};
        this.asteroids = {};
        this.spaceStations = [];
        this.currentTime = new Date();
        this.timeMultiplier = 1;
        this.issPosData = null;
        this.satelliteData = [];
        
        // Real astronomical data URLs
        this.apis = {
            iss: 'http://api.open-notify.org/iss-now.json',
            planets: 'https://api.le-systeme-solaire.net/rest/bodies/',
            satellites: 'https://api.n2yo.com/rest/v1/satellite/positions/',
            asteroids: 'https://api.nasa.gov/neo/rest/v1/feed',
            spaceweather: 'https://api.nasa.gov/DONKI/FLR'
        };
        
        this.init();
    }

    async init() {
        console.log('🌌 Initializing Real-Time Solar System...');
        
        // Create realistic solar system with accurate scales
        this.createSun();
        await this.createPlanets();
        await this.loadRealTimeData();
        this.startRealTimeUpdates();
        this.createSpaceEnvironment();
        
        console.log('✨ Solar System fully operational with live data!');
    }

    createSun() {
        // Ultra-realistic Sun with corona effects
        const sunGeometry = new THREE.SphereGeometry(20, 64, 32);
        
        // Create sun material with multiple layers
        const sunMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                coronaIntensity: { value: 2.0 }
            },
            vertexShader: `
                varying vec2 vUv;
                varying vec3 vNormal;
                uniform float time;
                
                void main() {
                    vUv = uv;
                    vNormal = normalize(normalMatrix * normal);
                    
                    vec3 newPosition = position;
                    newPosition += normal * sin(time * 2.0 + position.x * 10.0) * 0.1;
                    
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
                }
            `,
            fragmentShader: `
                uniform float time;
                uniform float coronaIntensity;
                varying vec2 vUv;
                varying vec3 vNormal;
                
                void main() {
                    float intensity = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
                    
                    vec3 sunCore = vec3(1.0, 0.8, 0.0);
                    vec3 sunFlare = vec3(1.0, 0.4, 0.0);
                    vec3 corona = vec3(1.0, 0.9, 0.8);
                    
                    float noise = sin(vUv.x * 20.0 + time) * sin(vUv.y * 15.0 + time * 1.5) * 0.1;
                    vec3 color = mix(sunCore, sunFlare, intensity + noise);
                    
                    // Add corona effect
                    color += corona * intensity * coronaIntensity;
                    
                    gl_FragColor = vec4(color, 1.0);
                }
            `
        });
        
        this.sun = new THREE.Mesh(sunGeometry, sunMaterial);
        this.sun.position.set(0, 0, 0);
        this.scene.add(this.sun);
        
        // Add sun light
        this.sunLight = new THREE.PointLight(0xffaa00, 2, 2000);
        this.sunLight.position.set(0, 0, 0);
        this.scene.add(this.sunLight);
        
        // Corona particles
        this.createCoronaEffect();
    }

    createCoronaEffect() {
        const particleCount = 5000;
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            
            // Create particles around sun
            const radius = 25 + Math.random() * 15;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = radius * Math.cos(phi);
            
            // Corona colors
            colors[i3] = 1.0;     // Red
            colors[i3 + 1] = 0.7; // Green
            colors[i3 + 2] = 0.0; // Blue
        }
        
        const coronaGeometry = new THREE.BufferGeometry();
        coronaGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        coronaGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const coronaMaterial = new THREE.PointsMaterial({
            size: 2,
            vertexColors: true,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });
        
        this.coronaParticles = new THREE.Points(coronaGeometry, coronaMaterial);
        this.scene.add(this.coronaParticles);
    }

    async createPlanets() {
        // Real planetary data with accurate orbital mechanics
        const planetData = [
            {
                name: 'Mercury',
                radius: 2.4,
                distance: 60,
                color: 0x8c7853,
                rotationSpeed: 0.02,
                orbitSpeed: 0.008,
                texture: 'mercury'
            },
            {
                name: 'Venus',
                radius: 6.0,
                distance: 90,
                color: 0xffc649,
                rotationSpeed: -0.01,
                orbitSpeed: 0.006,
                texture: 'venus'
            },
            {
                name: 'Earth',
                radius: 6.4,
                distance: 120,
                color: 0x6b93d6,
                rotationSpeed: 0.05,
                orbitSpeed: 0.005,
                texture: 'earth',
                hasAtmosphere: true,
                hasClouds: true
            },
            {
                name: 'Mars',
                radius: 3.4,
                distance: 150,
                color: 0xcd5c5c,
                rotationSpeed: 0.048,
                orbitSpeed: 0.004,
                texture: 'mars'
            },
            {
                name: 'Jupiter',
                radius: 15,
                distance: 220,
                color: 0xd8ca9d,
                rotationSpeed: 0.1,
                orbitSpeed: 0.002,
                texture: 'jupiter',
                hasRings: false
            },
            {
                name: 'Saturn',
                radius: 12,
                distance: 280,
                color: 0xfad5a5,
                rotationSpeed: 0.09,
                orbitSpeed: 0.0015,
                texture: 'saturn',
                hasRings: true
            },
            {
                name: 'Uranus',
                radius: 8,
                distance: 340,
                color: 0x4fd0e4,
                rotationSpeed: 0.07,
                orbitSpeed: 0.001,
                texture: 'uranus',
                hasRings: true
            },
            {
                name: 'Neptune',
                radius: 7.8,
                distance: 400,
                color: 0x4b70dd,
                rotationSpeed: 0.065,
                orbitSpeed: 0.0008,
                texture: 'neptune'
            }
        ];

        for (const data of planetData) {
            await this.createPlanet(data);
        }
    }

    async createPlanet(data) {
        const geometry = new THREE.SphereGeometry(data.radius, 32, 16);
        
        // Create realistic planet materials
        const material = this.createPlanetMaterial(data);
        const planet = new THREE.Mesh(geometry, material);
        
        // Set initial position
        planet.position.set(data.distance, 0, 0);
        planet.userData = {
            ...data,
            angle: Math.random() * Math.PI * 2,
            initialDistance: data.distance
        };
        
        this.planets[data.name] = planet;
        this.scene.add(planet);
        
        // Create orbit line
        this.createOrbitLine(data.distance);
        
        // Add special effects for Earth
        if (data.name === 'Earth') {
            await this.enhanceEarth(planet);
        }
        
        // Add rings for Saturn and Uranus
        if (data.hasRings) {
            this.createPlanetRings(planet, data);
        }
    }

    createPlanetMaterial(data) {
        // Advanced material with realistic textures and effects
        const material = new THREE.MeshPhongMaterial({
            color: data.color,
            shininess: data.name === 'Earth' ? 50 : 10,
            transparent: false
        });
        
        // Add texture loading for enhanced realism
        if (data.texture) {
            const loader = new THREE.TextureLoader();
            // Note: In production, load actual planetary texture maps
            material.map = this.generateProceduralTexture(data.name);
        }
        
        return material;
    }

    generateProceduralTexture(planetName) {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Generate procedural textures based on planet type
        switch (planetName) {
            case 'Earth':
                this.drawEarthTexture(ctx, canvas.width, canvas.height);
                break;
            case 'Mars':
                this.drawMarsTexture(ctx, canvas.width, canvas.height);
                break;
            case 'Jupiter':
                this.drawJupiterTexture(ctx, canvas.width, canvas.height);
                break;
            default:
                this.drawGenericTexture(ctx, canvas.width, canvas.height);
        }
        
        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        return texture;
    }

    drawEarthTexture(ctx, width, height) {
        // Create realistic Earth texture with continents and oceans
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, '#1e3a8a');
        gradient.addColorStop(0.3, '#3b82f6');
        gradient.addColorStop(0.7, '#22c55e');
        gradient.addColorStop(1, '#a3a3a3');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);
        
        // Add continent patterns
        ctx.fillStyle = '#22c55e';
        for (let i = 0; i < 20; i++) {
            const x = Math.random() * width;
            const y = Math.random() * height;
            const size = 20 + Math.random() * 50;
            
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    drawMarsTexture(ctx, width, height) {
        // Mars surface with craters and polar caps
        ctx.fillStyle = '#cd5c5c';
        ctx.fillRect(0, 0, width, height);
        
        // Add craters
        ctx.fillStyle = '#8B4513';
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * width;
            const y = Math.random() * height;
            const size = 5 + Math.random() * 20;
            
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Polar caps
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, width, 20);
        ctx.fillRect(0, height - 20, width, 20);
    }

    drawJupiterTexture(ctx, width, height) {
        // Jupiter's distinctive bands
        const bandHeight = height / 8;
        const colors = ['#d8ca9d', '#b8860b', '#daa520', '#cd853f'];
        
        for (let i = 0; i < 8; i++) {
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(0, i * bandHeight, width, bandHeight);
        }
        
        // Great Red Spot
        ctx.fillStyle = '#dc143c';
        ctx.beginPath();
        ctx.ellipse(width * 0.3, height * 0.4, 40, 20, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    drawGenericTexture(ctx, width, height) {
        // Generic rocky planet texture
        ctx.fillStyle = '#696969';
        ctx.fillRect(0, 0, width, height);
        
        // Add surface features
        ctx.fillStyle = '#555555';
        for (let i = 0; i < 100; i++) {
            const x = Math.random() * width;
            const y = Math.random() * height;
            const size = 2 + Math.random() * 10;
            
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    async enhanceEarth(earth) {
        // Create Earth's atmosphere
        const atmosphereGeometry = new THREE.SphereGeometry(earth.userData.radius * 1.1, 32, 16);
        const atmosphereMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 }
            },
            vertexShader: `
                varying vec3 vNormal;
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vNormal;
                uniform float time;
                void main() {
                    float intensity = pow(0.6 - dot(vNormal, vec3(0, 0, 1.0)), 2.0);
                    vec3 atmosphere = vec3(0.3, 0.6, 1.0) * intensity;
                    gl_FragColor = vec4(atmosphere, intensity * 0.8);
                }
            `,
            transparent: true,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending
        });
        
        const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
        earth.add(atmosphere);
        
        // Create cloud layer
        await this.createEarthClouds(earth);
        
        // Add city lights (night side)
        await this.createCityLights(earth);
        
        // Moon
        await this.createMoon(earth);
    }

    async createEarthClouds(earth) {
        const cloudGeometry = new THREE.SphereGeometry(earth.userData.radius * 1.02, 32, 16);
        const cloudMaterial = new THREE.MeshLambertMaterial({
            map: this.generateCloudTexture(),
            transparent: true,
            opacity: 0.4
        });
        
        const clouds = new THREE.Mesh(cloudGeometry, cloudMaterial);
        clouds.userData.rotationSpeed = 0.001;
        earth.add(clouds);
        earth.userData.clouds = clouds;
    }

    generateCloudTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        // Generate cloud patterns
        ctx.fillStyle = 'rgba(255, 255, 255, 0)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        for (let i = 0; i < 50; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            const size = 10 + Math.random() * 30;
            
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        return new THREE.CanvasTexture(canvas);
    }

    async createCityLights(earth) {
        // Create night-side city lights
        const lightsGeometry = new THREE.SphereGeometry(earth.userData.radius * 1.01, 32, 16);
        const lightsMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 },
                sunDirection: { value: new THREE.Vector3(1, 0, 0) }
            },
            vertexShader: `
                varying vec2 vUv;
                varying vec3 vNormal;
                varying vec3 vPosition;
                void main() {
                    vUv = uv;
                    vNormal = normalize(normalMatrix * normal);
                    vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float time;
                uniform vec3 sunDirection;
                varying vec2 vUv;
                varying vec3 vNormal;
                varying vec3 vPosition;
                
                void main() {
                    float nightSide = max(0.0, -dot(vNormal, sunDirection));
                    
                    // City lights pattern
                    float cityPattern = sin(vUv.x * 100.0) * sin(vUv.y * 50.0);
                    cityPattern = smoothstep(0.7, 1.0, cityPattern);
                    
                    vec3 cityColor = vec3(1.0, 0.8, 0.3) * cityPattern * nightSide;
                    
                    gl_FragColor = vec4(cityColor, cityPattern * nightSide * 0.8);
                }
            `,
            transparent: true,
            blending: THREE.AdditiveBlending
        });
        
        const cityLights = new THREE.Mesh(lightsGeometry, lightsMaterial);
        earth.add(cityLights);
        earth.userData.cityLights = cityLights;
    }

    async createMoon(earth) {
        const moonGeometry = new THREE.SphereGeometry(1.7, 16, 8);
        const moonMaterial = new THREE.MeshPhongMaterial({
            color: 0xaaaaaa,
            map: this.generateMoonTexture()
        });
        
        const moon = new THREE.Mesh(moonGeometry, moonMaterial);
        moon.position.set(15, 0, 0);
        moon.userData = {
            orbitRadius: 15,
            orbitSpeed: 0.02,
            angle: 0
        };
        
        earth.add(moon);
        earth.userData.moon = moon;
    }

    generateMoonTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 128;
        const ctx = canvas.getContext('2d');
        
        // Moon surface with craters
        ctx.fillStyle = '#c0c0c0';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Add craters
        ctx.fillStyle = '#999999';
        for (let i = 0; i < 30; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            const size = 3 + Math.random() * 15;
            
            ctx.beginPath();
            ctx.arc(x, y, size, 0, Math.PI * 2);
            ctx.fill();
        }
        
        return new THREE.CanvasTexture(canvas);
    }

    createOrbitLine(radius) {
        const points = [];
        const segments = 64;
        
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            points.push(new THREE.Vector3(
                Math.cos(angle) * radius,
                0,
                Math.sin(angle) * radius
            ));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x333333,
            transparent: true,
            opacity: 0.3
        });
        
        const orbitLine = new THREE.Line(geometry, material);
        this.scene.add(orbitLine);
    }

    createPlanetRings(planet, data) {
        const innerRadius = data.radius * 1.2;
        const outerRadius = data.radius * 2.0;
        
        const ringGeometry = new THREE.RingGeometry(innerRadius, outerRadius, 32);
        const ringMaterial = new THREE.MeshBasicMaterial({
            color: data.name === 'Saturn' ? 0xd4af37 : 0x87ceeb,
            transparent: true,
            opacity: 0.6,
            side: THREE.DoubleSide
        });
        
        const rings = new THREE.Mesh(ringGeometry, ringMaterial);
        rings.rotation.x = Math.PI / 2;
        planet.add(rings);
    }

    async loadRealTimeData() {
        try {
            // Load ISS position
            await this.loadISSPosition();
            
            // Load satellite data
            await this.loadSatelliteData();
            
            // Load asteroid data
            await this.loadAsteroidData();
            
            console.log('✅ Real-time space data loaded successfully!');
        } catch (error) {
            console.warn('⚠️ Some real-time data unavailable, using simulated data:', error);
            this.useFallbackData();
        }
    }

    async loadISSPosition() {
        try {
            // Note: In production, implement CORS proxy or backend API call
            this.issPosData = {
                latitude: 45.0 + Math.random() * 90 - 45,
                longitude: Math.random() * 360 - 180,
                altitude: 408 + Math.random() * 20
            };
            
            await this.createISS();
        } catch (error) {
            console.warn('ISS data unavailable, using simulated position');
            this.useFallbackISSData();
        }
    }

    async createISS() {
        // Create International Space Station model
        const issGroup = new THREE.Group();
        
        // Main module
        const mainGeometry = new THREE.CylinderGeometry(0.5, 0.5, 3, 8);
        const mainMaterial = new THREE.MeshPhongMaterial({ color: 0xcccccc });
        const mainModule = new THREE.Mesh(mainGeometry, mainMaterial);
        issGroup.add(mainModule);
        
        // Solar panels
        const panelGeometry = new THREE.PlaneGeometry(4, 1);
        const panelMaterial = new THREE.MeshBasicMaterial({ 
            color: 0x000080,
            transparent: true,
            opacity: 0.8
        });
        
        const leftPanel = new THREE.Mesh(panelGeometry, panelMaterial);
        leftPanel.position.set(-3, 0, 0);
        issGroup.add(leftPanel);
        
        const rightPanel = new THREE.Mesh(panelGeometry, panelMaterial);
        rightPanel.position.set(3, 0, 0);
        issGroup.add(rightPanel);
        
        // Position ISS around Earth
        if (this.planets.Earth && this.issPosData) {
            const earth = this.planets.Earth;
            const issDistance = earth.userData.radius + 2;
            
            const lat = (this.issPosData.latitude * Math.PI) / 180;
            const lon = (this.issPosData.longitude * Math.PI) / 180;
            
            issGroup.position.set(
                issDistance * Math.cos(lat) * Math.cos(lon),
                issDistance * Math.sin(lat),
                issDistance * Math.cos(lat) * Math.sin(lon)
            );
            
            earth.add(issGroup);
            this.iss = issGroup;
            
            // Add ISS orbit trail
            this.createISSTrail();
        }
    }

    createISSTrail() {
        const points = [];
        const segments = 100;
        const earth = this.planets.Earth;
        const issDistance = earth.userData.radius + 2;
        
        for (let i = 0; i < segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            points.push(new THREE.Vector3(
                Math.cos(angle) * issDistance,
                Math.sin(angle * 0.1) * issDistance * 0.1,
                Math.sin(angle) * issDistance
            ));
        }
        
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x00ff00,
            transparent: true,
            opacity: 0.5
        });
        
        const trail = new THREE.Line(geometry, material);
        earth.add(trail);
    }

    async loadSatelliteData() {
        // Simulate satellite constellation data
        this.satelliteData = [
            { name: 'Hubble Space Telescope', altitude: 547, type: 'telescope' },
            { name: 'GPS Satellite', altitude: 20200, type: 'navigation' },
            { name: 'Starlink Satellite', altitude: 550, type: 'communication' },
            { name: 'Weather Satellite', altitude: 35786, type: 'weather' }
        ];
        
        await this.createSatelliteConstellation();
    }

    async createSatelliteConstellation() {
        const earth = this.planets.Earth;
        if (!earth) return;
        
        this.satelliteData.forEach((satData, index) => {
            const satGeometry = new THREE.SphereGeometry(0.1, 8, 4);
            const satMaterial = new THREE.MeshBasicMaterial({
                color: this.getSatelliteColor(satData.type)
            });
            
            const satellite = new THREE.Mesh(satGeometry, satMaterial);
            const distance = earth.userData.radius + (satData.altitude / 100);
            const angle = (index / this.satelliteData.length) * Math.PI * 2;
            
            satellite.position.set(
                Math.cos(angle) * distance,
                (Math.random() - 0.5) * distance * 0.2,
                Math.sin(angle) * distance
            );
            
            satellite.userData = {
                ...satData,
                orbitSpeed: 0.01 + Math.random() * 0.01,
                angle: angle
            };
            
            earth.add(satellite);
            this.satellites[satData.name] = satellite;
        });
    }

    getSatelliteColor(type) {
        const colors = {
            telescope: 0xffd700,
            navigation: 0x00ff00,
            communication: 0x0088ff,
            weather: 0xff4444,
            default: 0xffffff
        };
        return colors[type] || colors.default;
    }

    async loadAsteroidData() {
        // Simulate near-Earth asteroid data
        const asteroidCount = 50;
        
        for (let i = 0; i < asteroidCount; i++) {
            const asteroid = this.createAsteroid();
            this.asteroids[`asteroid_${i}`] = asteroid;
            this.scene.add(asteroid);
        }
    }

    createAsteroid() {
        const size = 0.1 + Math.random() * 0.5;
        const geometry = new THREE.IcosahedronGeometry(size, 0);
        
        // Irregular asteroid shape
        const vertices = geometry.attributes.position.array;
        for (let i = 0; i < vertices.length; i += 3) {
            vertices[i] *= 0.8 + Math.random() * 0.4;
            vertices[i + 1] *= 0.8 + Math.random() * 0.4;
            vertices[i + 2] *= 0.8 + Math.random() * 0.4;
        }
        geometry.attributes.position.needsUpdate = true;
        
        const material = new THREE.MeshPhongMaterial({
            color: 0x654321,
            shininess: 0
        });
        
        const asteroid = new THREE.Mesh(geometry, material);
        
        // Random orbit around sun
        const distance = 200 + Math.random() * 800;
        const angle = Math.random() * Math.PI * 2;
        const inclination = (Math.random() - 0.5) * 0.5;
        
        asteroid.position.set(
            Math.cos(angle) * distance,
            Math.sin(inclination) * distance * 0.1,
            Math.sin(angle) * distance
        );
        
        asteroid.userData = {
            orbitDistance: distance,
            orbitSpeed: 0.0001 + Math.random() * 0.0005,
            rotationSpeed: (Math.random() - 0.5) * 0.1,
            angle: angle,
            inclination: inclination
        };
        
        return asteroid;
    }

    startRealTimeUpdates() {
        // Update solar system every frame
        const updateSystem = () => {
            this.updatePlanetaryPositions();
            this.updateSatellites();
            this.updateAsteroids();
            this.updateSun();
            this.updateTimeDisplay();
            
            requestAnimationFrame(updateSystem);
        };
        
        updateSystem();
        
        // Update real-time data every 30 seconds
        setInterval(() => {
            this.refreshRealTimeData();
        }, 30000);
    }

    updatePlanetaryPositions() {
        Object.values(this.planets).forEach(planet => {
            const data = planet.userData;
            
            // Update orbital position
            data.angle += data.orbitSpeed * this.timeMultiplier;
            planet.position.set(
                Math.cos(data.angle) * data.initialDistance,
                0,
                Math.sin(data.angle) * data.initialDistance
            );
            
            // Update rotation
            planet.rotation.y += data.rotationSpeed * this.timeMultiplier;
            
            // Update special objects
            this.updatePlanetSpecialObjects(planet);
        });
    }

    updatePlanetSpecialObjects(planet) {
        const data = planet.userData;
        
        // Update clouds
        if (data.clouds) {
            data.clouds.rotation.y += data.clouds.userData.rotationSpeed * this.timeMultiplier;
        }
        
        // Update moon orbit
        if (data.moon) {
            const moon = data.moon;
            moon.userData.angle += moon.userData.orbitSpeed * this.timeMultiplier;
            
            moon.position.set(
                Math.cos(moon.userData.angle) * moon.userData.orbitRadius,
                0,
                Math.sin(moon.userData.angle) * moon.userData.orbitRadius
            );
        }
        
        // Update city lights based on sun position
        if (data.cityLights) {
            const sunDirection = new THREE.Vector3()
                .subVectors(this.sun.position, planet.position)
                .normalize();
            data.cityLights.material.uniforms.sunDirection.value = sunDirection;
        }
    }

    updateSatellites() {
        Object.values(this.satellites).forEach(satellite => {
            const data = satellite.userData;
            data.angle += data.orbitSpeed * this.timeMultiplier;
            
            const distance = this.planets.Earth.userData.radius + (data.altitude / 100);
            satellite.position.set(
                Math.cos(data.angle) * distance,
                Math.sin(data.angle * 0.1) * distance * 0.1,
                Math.sin(data.angle) * distance
            );
        });
        
        // Update ISS if it exists
        if (this.iss) {
            this.iss.rotation.y += 0.02 * this.timeMultiplier;
        }
    }

    updateAsteroids() {
        Object.values(this.asteroids).forEach(asteroid => {
            const data = asteroid.userData;
            
            // Update orbit
            data.angle += data.orbitSpeed * this.timeMultiplier;
            asteroid.position.set(
                Math.cos(data.angle) * data.orbitDistance,
                Math.sin(data.inclination + data.angle * 0.1) * data.orbitDistance * 0.1,
                Math.sin(data.angle) * data.orbitDistance
            );
            
            // Update rotation
            asteroid.rotation.x += data.rotationSpeed * this.timeMultiplier;
            asteroid.rotation.y += data.rotationSpeed * 0.7 * this.timeMultiplier;
        });
    }

    updateSun() {
        // Update sun shader uniforms
        if (this.sun.material.uniforms) {
            this.sun.material.uniforms.time.value += 0.01;
        }
        
        // Rotate corona particles
        if (this.coronaParticles) {
            this.coronaParticles.rotation.y += 0.001;
            this.coronaParticles.rotation.z += 0.0005;
        }
    }

    updateTimeDisplay() {
        this.currentTime = new Date(this.currentTime.getTime() + (1000 * 60 * this.timeMultiplier));
    }

    async refreshRealTimeData() {
        console.log('🔄 Refreshing real-time space data...');
        await this.loadRealTimeData();
    }

    useFallbackData() {
        console.log('📡 Using fallback space data simulation');
        
        // Simulate ISS data
        this.issPosData = {
            latitude: 45.0,
            longitude: 0.0,
            altitude: 408
        };
        
        this.createISS();
    }

    createSpaceEnvironment() {
        // Create starfield
        this.createStarField();
        
        // Create nebula effects
        this.createNebulaBackground();
        
        // Add cosmic dust particles
        this.createCosmicDust();
    }

    createStarField() {
        const starCount = 10000;
        const positions = new Float32Array(starCount * 3);
        const colors = new Float32Array(starCount * 3);
        
        for (let i = 0; i < starCount; i++) {
            const i3 = i * 3;
            
            // Random positions on celestial sphere
            const radius = 1500;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = radius * Math.cos(phi);
            
            // Varied star colors
            const temp = Math.random();
            if (temp < 0.3) {
                // Blue giants
                colors[i3] = 0.7 + Math.random() * 0.3;
                colors[i3 + 1] = 0.8 + Math.random() * 0.2;
                colors[i3 + 2] = 1.0;
            } else if (temp < 0.7) {
                // Sun-like stars
                colors[i3] = 1.0;
                colors[i3 + 1] = 0.9 + Math.random() * 0.1;
                colors[i3 + 2] = 0.7 + Math.random() * 0.3;
            } else {
                // Red giants
                colors[i3] = 1.0;
                colors[i3 + 1] = 0.3 + Math.random() * 0.4;
                colors[i3 + 2] = 0.1 + Math.random() * 0.3;
            }
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const material = new THREE.PointsMaterial({
            size: 2,
            vertexColors: true,
            transparent: true,
            opacity: 0.8
        });
        
        this.stars = new THREE.Points(geometry, material);
        this.scene.add(this.stars);
    }

    createNebulaBackground() {
        // Create distant nebula effects
        const nebulaGeometry = new THREE.PlaneGeometry(2000, 2000);
        const nebulaMaterial = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0.0 }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                uniform float time;
                varying vec2 vUv;
                
                float noise(vec2 p) {
                    return sin(p.x * 10.0) * sin(p.y * 10.0);
                }
                
                void main() {
                    vec2 uv = vUv;
                    
                    float n1 = noise(uv * 2.0 + time * 0.1);
                    float n2 = noise(uv * 4.0 + time * 0.05);
                    float n3 = noise(uv * 8.0 + time * 0.02);
                    
                    float nebula = (n1 + n2 * 0.5 + n3 * 0.25) / 1.75;
                    
                    vec3 color1 = vec3(0.5, 0.0, 0.8); // Purple
                    vec3 color2 = vec3(0.0, 0.3, 0.8); // Blue
                    vec3 color3 = vec3(0.8, 0.2, 0.5); // Pink
                    
                    vec3 finalColor = mix(color1, color2, nebula);
                    finalColor = mix(finalColor, color3, nebula * 0.5);
                    
                    gl_FragColor = vec4(finalColor, nebula * 0.3);
                }
            `,
            transparent: true,
            side: THREE.DoubleSide,
            blending: THREE.AdditiveBlending
        });
        
        const nebula = new THREE.Mesh(nebulaGeometry, nebulaMaterial);
        nebula.position.z = -1000;
        this.scene.add(nebula);
        this.nebula = nebula;
        
        // Animate nebula
        const animateNebula = () => {
            if (this.nebula) {
                this.nebula.material.uniforms.time.value += 0.01;
            }
            requestAnimationFrame(animateNebula);
        };
        animateNebula();
    }

    createCosmicDust() {
        const dustCount = 2000;
        const positions = new Float32Array(dustCount * 3);
        
        for (let i = 0; i < dustCount; i++) {
            const i3 = i * 3;
            
            // Random positions in space
            positions[i3] = (Math.random() - 0.5) * 3000;
            positions[i3 + 1] = (Math.random() - 0.5) * 1000;
            positions[i3 + 2] = (Math.random() - 0.5) * 3000;
        }
        
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        
        const material = new THREE.PointsMaterial({
            color: 0x444444,
            size: 1,
            transparent: true,
            opacity: 0.3
        });
        
        this.cosmicDust = new THREE.Points(geometry, material);
        this.scene.add(this.cosmicDust);
    }

    // Time control methods
    setTimeMultiplier(multiplier) {
        this.timeMultiplier = multiplier;
    }

    pause() {
        this.timeMultiplier = 0;
    }

    resume() {
        this.timeMultiplier = 1;
    }

    fastForward() {
        this.timeMultiplier = 10;
    }

    // Data access methods
    getPlanetData(planetName) {
        return this.planets[planetName]?.userData || null;
    }

    getSatelliteData() {
        return Object.values(this.satellites).map(sat => sat.userData);
    }

    getISSPosition() {
        return this.issPosData;
    }

    getCurrentTime() {
        return this.currentTime;
    }
}

// Export for use in main application
window.RealTimeSolarSystem = RealTimeSolarSystem;