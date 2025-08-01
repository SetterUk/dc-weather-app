# DC Watchtower Animated Background Features

## Overview
The DC Weather Watchtower now features a fully animated background that dynamically changes based on:
- **Time of Day**: Morning, Afternoon, Evening, Night
- **Weather Conditions**: Clear, Rain, Snow, Storm, Fog, Cloudy
- **User Location**: Adapts to local time and weather

## Time-Based Animations

### Morning (5 AM - 12 PM)
- **Sun**: Animated sun with rotating rays and pulsing glow
- **Sky**: Orange to yellow to blue gradient
- **Lighting**: Warm golden light overlay

### Afternoon (12 PM - 5 PM)
- **Sun**: Positioned higher with bright yellow glow
- **Sky**: Blue gradient with clear visibility
- **Lighting**: Bright, clear atmosphere

### Evening (5 PM - 8 PM)
- **Sun**: Lower position with orange/red tint
- **Sky**: Purple to pink to orange gradient
- **Lighting**: Warm sunset lighting effect

### Night (8 PM - 5 AM)
- **Moon**: Animated moon with craters and soft glow
- **Stars**: Twinkling stars scattered across the sky
- **Sky**: Deep indigo to purple to black gradient
- **Beacon**: Rotating watchtower beacon light
- **Lighting**: Moonlight overlay effect

## Weather-Based Animations

### Rain
- **Effect**: 100 animated raindrops falling at different speeds
- **Visual**: Blue translucent drops with realistic physics
- **Sky**: Darker, more overcast appearance

### Snow
- **Effect**: 50 animated snowflakes with wind drift
- **Visual**: White circular flakes with gentle swaying motion
- **Sky**: Gray-white overcast atmosphere

### Storm
- **Effect**: Heavy rain + lightning flashes
- **Visual**: Intense rainfall with periodic white lightning overlay
- **Sky**: Dark, dramatic storm clouds

### Fog
- **Effect**: Animated fog overlay with opacity changes
- **Visual**: Gray mist that pulses and moves
- **Sky**: Reduced visibility with gray tint

### Cloudy
- **Effect**: Moving cloud emojis across the sky
- **Visual**: Animated clouds drifting from left to right
- **Sky**: Partially overcast appearance

### Wind
- **Effect**: Particle effects when wind speed > 15 km/h
- **Visual**: Small white particles moving horizontally
- **Sky**: Dynamic particle movement

## Additional Features

### Atmospheric Particles
- 30 floating particles that gently move up and down
- Creates depth and atmosphere
- Subtle opacity and scale animations

### Watchtower Beacon (Night Only)
- Rotating beacon light from the watchtower
- 8-second rotation cycle
- Yellow gradient beam with blur effect

### Dynamic Sky Opacity
- Sky overlay opacity changes based on weather conditions
- Storm: 80% opacity for dramatic effect
- Rain: 60% opacity for overcast look
- Fog: 70% opacity for reduced visibility
- Clear: 40-70% opacity based on time of day

## Technical Implementation

### Components
- `WatchtowerBackground.js`: Main background component
- Integrated with existing weather data from backend
- Uses Framer Motion for smooth animations
- Responsive design for all screen sizes

### Performance Optimizations
- Efficient particle systems
- Optimized animation loops
- Conditional rendering based on weather conditions
- Background image caching

### Responsive Design
- Works on desktop and mobile devices
- Scales appropriately for different screen sizes
- Maintains performance across devices

## Usage
The background automatically activates when the app loads and continuously updates based on:
1. Current local time (updates every minute)
2. Weather data from the API
3. User's geographic location

No additional configuration required - the background adapts automatically to provide an immersive, location-aware experience that matches the current weather and time of day.